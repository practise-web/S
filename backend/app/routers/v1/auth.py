from fastapi import APIRouter, status, Depends, Request, Body
from app.schemas.request_models import UserCreate, UserLogin
from fastapi.responses import JSONResponse
from app.schemas.response_models import (
    LoginSuccess,
    LoginError,
    SignupSuccess,
    SignupError,
)
from app.services.keycloak_service import kc_admin
from app.core.security import get_current_user
from app.core.rate_limiter import limiter
from app.core.config import kcsettings
import logging
import httpx
import os

logger = logging.getLogger("app.routers.auth")
router = APIRouter(prefix="/auth", tags=["Authentication"])
BASE_HOSTNAME = os.environ.get("BASE_HOSTNAME")


@router.post(
    "/login",
    response_model=LoginSuccess,
    responses={401: {"model": LoginError}},
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
    logger.info(f"[{req_id}] Login attempt for email: {email}")

    data = {
        "client_id": kcsettings.KEYCLOAK_CLIENT_ID,
        "client_secret": kcsettings.KEYCLOAK_CLIENT_SECRET,
        "grant_type": "password",  # Password-based login
        "username": email,
        "password": password,
        "scope": "openid profile email",
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            kcsettings.KEYCLOAK_TOKEN_URL, data=data, headers=headers
        )

    if response.status_code != 200:
        logger.warning(f"[{req_id}] Failed login for email {email}: {response.text}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=LoginError(message="Invalid credentials").model_dump(),
        )

    logger.info(f"[{req_id}] Successful login for email: {email}")
    return response.json()


@router.post(
    "/signup",
    response_model=SignupSuccess,
    responses={500: {"model": SignupError}},
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
    logger.info(f"[{req_id}] Signup attempt for username: {username}, email: {email}")

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

        async with httpx.AsyncClient() as client:
            create_user_res = await client.post(
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
                content=SignupError(message="Failed to create the user").model_dump(),
            )

        # ----------- Get user ID from Location header -----------
        user_id = create_user_res.headers.get("Location")
        if not user_id:
            logger.error(f"[{req_id}] Failed to extract user ID for {username}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=SignupError(message="Failed to extract user ID").model_dump(),
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
        logger.exception(f"[{req_id}] Exception during signup for {username}: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=SignupError(message="Failed to create the user").model_dump(),
        )


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    tags=["Authentication"],
    summary="Refresh Access Token",
    description="""
                Refresh the access token using a valid refresh token.
                """,
)
async def refresh_token(refresh_token: str = Body(..., embed=True)):
    data = {
        "client_id": kcsettings.KEYCLOAK_CLIENT_ID,
        "client_secret": kcsettings.KEYCLOAK_CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                kcsettings.KEYCLOAK_TOKEN_URL, data=data, headers=headers
            )

        if response.status_code != 200:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"message": "Invalid refresh token"},
            )

        return response.json()
    except Exception as e:
        logger.exception(f"Exception during token refresh: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Failed to refresh token"},
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
async def logout(refresh_token: str = Body(..., embed=True)):
    data = {
        "client_id": kcsettings.KEYCLOAK_CLIENT_ID,
        "client_secret": kcsettings.KEYCLOAK_CLIENT_SECRET,
        "refresh_token": refresh_token,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                kcsettings.KEYCLOAK_LOGOUT_URL, data=data, headers=headers
            )

        if response.status_code != 204:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Failed to logout"},
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Successfully logged out"},
        )
    except Exception as e:
        logger.exception(f"Exception during logout: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Failed to logout"},
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
async def request_password_reset(request: Request, email: str = Body(..., embed=True)):
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
        logger.exception(f"Exception during password reset request for {email}: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Failed to request password reset"},
        )


@router.post(
    "/ping",
    status_code=status.HTTP_200_OK,
    tags=["Authentication"],
    summary="Test Token Validation",
)
async def validate_token(user=Depends(get_current_user)):
    return {"uid": user["sub"], "status": "valid"}
