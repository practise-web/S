from fastapi import APIRouter, status, Depends, Request
from fastapi.responses import JSONResponse
from app.schemas.request_models import UserCreate, UserLogin
from app.schemas.response_models import (
    LoginSuccess,
    LoginError,
    SignupSuccess,
    SignupError,
)
from app.services.keycloak_service import get_admin_token
from app.services.secure_routes import get_current_user
from app.core.rate_limiter import limiter
from dotenv import load_dotenv
import requests
import logging
import os

logger = logging.getLogger("app.auth")
router = APIRouter(prefix="/auth", tags=["Authentication"])


load_dotenv()

KEYCLOAK_URL = os.environ.get("KEYCLOAK_URL")
REALM = os.environ.get("KEYCLOAK_REALM")
CLIENT_ID = os.environ.get("AUTH_CLIENT_ID")
CLIENT_SECRET = os.environ.get("AUTH_CLIENT_SECRET")


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

    token_url = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token"

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "password",  # Password-based login
        "username": email,
        "password": password,
        "scope": "openid profile email",
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(token_url, data=data, headers=headers)
    if response.status_code != 200:
        logger.warning(f"[{req_id}] Failed login for email {email}: {response.text}")
        return JSONResponse(
            status_code=401,
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
        token = get_admin_token()

        # ----------- Step 1: Create the user -----------
        user_data = {
            "username": username,
            "email": email,
            "enabled": True,
            "emailVerified": False,
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        create_user_res = requests.post(
            f"{KEYCLOAK_URL}/admin/realms/{REALM}/users",
            json=user_data,
            headers=headers,
        )

        if create_user_res.status_code not in [201, 204]:
            logger.error(f"[{req_id}] Failed to create user {username}: {create_user_res.text}")
            return JSONResponse(
                status_code=500,
                content=SignupError(message="Failed to create the user").model_dump(),
            )

        # ----------- Step 2: Get user ID from Location header -----------
        user_id = create_user_res.headers.get("Location")
        if not user_id:
            logger.error(f"[{req_id}] Failed to extract user ID for {username}")
            return JSONResponse(
                status_code=500,
                content=SignupError(message="Failed to extract user ID").model_dump(),
            )

        user_id = user_id.split("/")[-1]

        # ------------ Step 3: Set password -----------
        password_data = {"type": "password", "value": password, "temporary": False}

        reset_pass_res = requests.put(
            f"{KEYCLOAK_URL}/admin/realms/{REALM}/users/{user_id}/reset-password",
            json=password_data,
            headers=headers,
        )

        if reset_pass_res.status_code != 204:
            logger.error(f"[{req_id}] Failed to set password for user {username}")
            return JSONResponse(
                status_code=500,
                content=SignupError(message="Failed to set password").model_dump(),
            )
        
        logger.info(f"[{req_id}] Successfully created user {username} with ID {user_id}")
        return JSONResponse(
            status_code=201,
            content=SignupSuccess(
                message="User created successfully", user_id=user_id
            ).model_dump(),
        )

    except Exception as e:
        logger.exception(f"[{req_id}] Exception during signup for {username}: {e}")
        return JSONResponse(
            status_code=500,
            content=SignupError(message="Failed to create the user").model_dump(),
        )


@router.post(
    "/ping",
    status_code=status.HTTP_200_OK,
    tags=["Authentication"],
    summary="Test Token Validation",
)
async def validate_token(user=Depends(get_current_user)):
    return {"uid": user["sub"], "status": "valid"}
