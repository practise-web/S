import uuid
from fastapi import APIRouter, status, Request
from fastapi.responses import JSONResponse
from app.schemas.request_models import UserCreate, UserLogin, PasswordResetRequest
from app.schemas.response_models import (
    LoginSuccess,
    SignupSuccess,
)
from app.services.keycloak_service import kc_admin
from app.core.rate_limiter import limiter
from app.core.config import kcsettings
from app.core import database as db
from app.core import network as net
import logging
import os
import json
import jwt

logger = logging.getLogger("app.routers.auth")
router = APIRouter(prefix="/auth", tags=["Authentication"])
BASE_HOSTNAME = os.environ.get("BASE_HOSTNAME")


@router.post(
    "/login",
    response_model=LoginSuccess,
    status_code=status.HTTP_200_OK,
    tags=["Authentication"],
    summary="User Login",
    description="""
                Authenticate a user using email and password.
                """,
)
@limiter.limit("5/minute")
async def login(input_data: UserLogin, request: Request):
    email = input_data.email
    password = input_data.password
    req_id = getattr(request.state, "request_id", "-")
    logger.info(f"[{req_id}] Login attempt")

    data = {
        "client_id": kcsettings.KEYCLOAK_CLIENT_ID,
        "client_secret": kcsettings.KEYCLOAK_CLIENT_SECRET,
        "grant_type": "password",  # Password-based login
        "username": email,
        "password": password,
        "scope": "openid profile email",
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = await net.client.post(
        kcsettings.KEYCLOAK_TOKEN_URL, data=data, headers=headers
    )

    if response.status_code != 200:
        logger.error(f"[{req_id}] Failed login: {response.text}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid email or password"},
        )

    logger.info(f"[{req_id}] Successful login")

    # Store session data in Redis with the phantom token as the key
    tokens = response.json()
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    refresh_ttl = tokens.get("refresh_expires_in", 3600)

    decoded = jwt.decode(access_token, options={"verify_signature": False})
    user_id = decoded.get("sub")

    phantom_token = str(uuid.uuid4())
    session_data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

    await db.redis_client.setex(
        f"session:{phantom_token}", refresh_ttl, json.dumps(session_data)
    )
    await db.redis_client.sadd(f"user_sessions:{user_id}", phantom_token)
    await db.redis_client.expire(f"user_sessions:{user_id}", 2592000)

    return JSONResponse(
        content={"message": "Login successful", "session_id": phantom_token}
    )


@router.post(
    "/signup",
    response_model=SignupSuccess,
    status_code=status.HTTP_201_CREATED,
    tags=["Authentication"],
    summary="User Signup",
    description="""
                Register a new user with Keycloack Authentication.
                """,
)
@limiter.limit("5/minute")
async def signup(input_data: UserCreate, request: Request):
    email = input_data.email
    username = input_data.username
    password = input_data.password

    req_id = getattr(request.state, "request_id", "-")
    logger.info(f"[{req_id}] Signup attempt for username: {username}")

    try:
        token = await kc_admin.get_admin_token()

        # ----------- Create the user -----------
        user_data = {
            "username": username,
            "email": email,
            "enabled": True,
            "credentials": [
                {"type": "password", "value": password, "temporary": False}
            ],
            "requiredActions": ["VERIFY_EMAIL"],
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        create_user_res = await net.client.post(
            kcsettings.KEYCLOAK_USERS_URL(),
            json=user_data,
            headers=headers,
        )

        if create_user_res.status_code not in [201, 204]:
            logger.error(
                f"[{req_id}] Failed to create user {username}: {create_user_res.text}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Failed to create the user"},
            )

        # ----------- Get user ID from Location header -----------
        user_id = create_user_res.headers.get("Location")
        if not user_id:
            logger.error(f"[{req_id}] Failed to extract user ID for {username}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Failed to extract user ID"},
            )

        user_id = user_id.split("/")[-1]

        # ----------- Send verification email -----------
        redirect_uri = f"{BASE_HOSTNAME}/auth/login?verified=true"
        await kc_admin.trigger_email_action(
            user_id, "VERIFY_EMAIL", token, redirect_uri
        )
        logger.info(
            f"[{req_id}] Successfully created user {username} with ID {user_id}. Verification email sent."
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=SignupSuccess(
                message="User created successfully. Verification email sent.",
                user_id=user_id,
            ).model_dump(),
        )

    except Exception as e:
        logger.error(f"[{req_id}] Error during signup for {username}: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Failed to create the user"},
        )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    tags=["Authentication"],
    summary="User Logout",
    description="""
                Logout a user by invalidating their refresh token.
                """,
)
async def logout(request: Request):
    req_id = getattr(request.state, "request_id", "-")
    session_id = getattr(request.state, "session_id", None)
    logger.info(f"[{req_id}] Attempting logout")
    if not session_id:
        return JSONResponse(status_code=200, content={"message": "Already logged out"})
    raw_data = await db.redis_client.get(f"session:{session_id}")
    if not raw_data:
        return JSONResponse(status_code=200, content={"message": "Already logged out"})

    refresh_token = json.loads(raw_data)["refresh_token"]

    data = {
        "client_id": kcsettings.KEYCLOAK_CLIENT_ID,
        "client_secret": kcsettings.KEYCLOAK_CLIENT_SECRET,
        "refresh_token": refresh_token,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    try:
        response = await net.client.post(
            kcsettings.KEYCLOAK_LOGOUT_URL, data=data, headers=headers
        )

        if response.status_code != 204:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Failed to logout"},
            )

        await db.redis_client.delete(f"session:{session_id}")

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Successfully logged out"},
        )
    except Exception as e:
        logger.error(f"[{req_id}] Error during logout: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Failed to logout"},
        )


@router.post(
    "/logout-all",
    status_code=status.HTTP_200_OK,
    tags=["Authentication"],
    summary="Logout from all devices",
    description="Logs out the user from all devices by invalidating all their sessions.",
)
async def logout_all_devices(request: Request):
    user_id = getattr(request.state, "user_id", None)
    req_id = getattr(request.state, "request_id", "-")
    logger.info(f"[{req_id}] Attempting logout all devices for user {user_id}")
    if not user_id:
        logger.error(
            f"[{req_id}] No user ID found in request state during logout all devices"
        )
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Not authenticated"},
        )

    user_key = f"user_sessions:{user_id}"
    all_uuids = await db.redis_client.smembers(user_key)

    for _uuid in all_uuids:
        logger.info(f"[{req_id}] Deleting session {_uuid} for user {user_id}")
        await db.redis_client.delete(f"session:{_uuid}")
    await db.redis_client.delete(user_key)

    logger.info(f"[{req_id}] Successfully logged out all devices for user {user_id}")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Successfully logged out all devices"},
    )


@router.post(
    "/password-reset/request",
    status_code=status.HTTP_200_OK,
    tags=["Authentication"],
    summary="Request Password Reset",
    description="""
                Request a password reset email to be sent to the user.
                """,
)
@limiter.limit("5/minute")
async def request_password_reset(
    password_reset_request: PasswordResetRequest, request: Request
):
    req_id = getattr(request.state, "request_id", "-")
    email = password_reset_request.email
    logger.info(f"[{req_id}] Password reset request recieved")
    try:
        token = await kc_admin.get_admin_token()
        user_id = await kc_admin.get_user_id_by_email(email, token)
        if not user_id:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": "User with this email not found"},
            )

        redirect_uri = f"{BASE_HOSTNAME}/auth/login?password_reset=true"
        await kc_admin.trigger_email_action(
            user_id, "UPDATE_PASSWORD", token, redirect_uri
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Password reset email sent"},
        )
    except Exception as e:
        logger.error(f"[{req_id}] Error during password reset request: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Failed to request password reset"},
        )
