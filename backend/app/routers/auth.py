from fastapi import APIRouter, status, Depends
from schemas.request_models import UserCreate, UserLogin
from schemas.response_models import LoginSuccess, LoginError, SignupSuccess, SignupError
import requests
from dotenv import dotenv_values
from services.keycloak_service import get_admin_token
from services.secure_routes import get_current_user
from fastapi.responses import JSONResponse

env_values = dotenv_values('.env')

router = APIRouter(prefix="/auth", tags=["Authentication"])


KEYCLOAK_URL = env_values["KEYCLOAK_URL"]
REALM = env_values["KEYCLOAK_REALM"]
CLIENT_ID = env_values["AUTH_CLIENT_ID"]
CLIENT_SECRET = env_values["AUTH_CLIENT_SECRET"]


@router.post("/login", 
             response_model=LoginSuccess,
             responses={
                401: {"model": LoginError}
            },
             status_code=status.HTTP_200_OK, 

             tags=["Authentication"],
             summary="User Login",
             description=
                """
                Authenticate a user using email and password.
                """)
async def login(data : UserLogin):
    email = data.email
    password = data.password
    
    token_url = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token"

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "password",        # Password-based login
        "username": email,
        "password": password,
        "scope": "openid profile email",
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(token_url, data=data, headers=headers)
    if response.status_code != 200:
        return JSONResponse(
            status_code=401,
            content=LoginError(message="Invalid credentials").model_dump()
        )
    
    return response.json()
    



@router.post("/signup", 
             response_model=SignupSuccess,
             responses={
                500: {"model": SignupError}
            },
             status_code=status.HTTP_201_CREATED, 
             
             tags=["Authentication"],
             summary="User Signup",
             description=
                """
                Register a new user with Keycloack Authentication.
                """)
async def signup(data : UserCreate):
    email = data.email
    username = data.username
    password = data.password
    try:
        token = get_admin_token()
        
        # ----------- Step 1: Create the user -----------
        user_data = {
            "username": username,
            "email": email,
            "enabled": True,
            "emailVerified": False
        }

        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        create_user_res = requests.post(
            f"{KEYCLOAK_URL}/admin/realms/{REALM}/users",
            json=user_data,
            headers=headers
        )

        if create_user_res.status_code not in [201, 204]:
            return JSONResponse(
                status_code=500,
                content=SignupError(message="Failed to create the user").model_dump()
            )
        
        # ----------- Step 2: Get user ID from Location header -----------
        user_id = create_user_res.headers.get("Location")
        if not user_id:
            return JSONResponse(
                status_code=500,
                content=SignupError(message="Failed to extract user ID").model_dump()
            )

        user_id = user_id.split("/")[-1]

        # ------------ Step 3: Set password -----------
        password_data = {
            "type": "password",
            "value": password,
            "temporary": False
        }

        reset_pass_res = requests.put(
            f"{KEYCLOAK_URL}/admin/realms/{REALM}/users/{user_id}/reset-password",
            json=password_data,
            headers=headers
        )

        if reset_pass_res.status_code != 204:
            return JSONResponse(
                status_code=500,
                content=SignupError(message="Failed to set password").model_dump()
            )

        return JSONResponse(
            status_code=201,
            content=SignupSuccess(message="User created successfully", user_id=user_id).model_dump()
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=SignupError(message="Failed to create the user").model_dump()
        )


@router.post('/ping', 
             status_code=status.HTTP_200_OK, 
             tags=["Authentication"],
             summary="Test Token Validation",)
async def validate_token(user=Depends(get_current_user)):
    return {"uid": user["sub"], "status": "valid"}
