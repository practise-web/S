from dotenv import load_dotenv
import requests
import os
from fastapi import HTTPException, status
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError

load_dotenv()

KEYCLOAK_URL = os.environ.get("KEYCLOAK_URL")
REALM = os.environ.get("KEYCLOAK_REALM")
CLIENT_ID = os.environ.get("AUTH_CLIENT_ID")
CLIENT_SECRET = os.environ.get("AUTH_CLIENT_SECRET")

JWKS_CACHE = None

def get_admin_token():
    """Get admin access token from Keycloak"""
    token_url = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token"

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "password",
        "username": "admin",
        "password": "admin_password",
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(token_url, data=data, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to get admin token")

    return response.json()["access_token"]


def get_jwks():
    global JWKS_CACHE
    if JWKS_CACHE:
        return JWKS_CACHE
    jwks_url = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/certs"
    JWKS_CACHE = requests.get(jwks_url).json()
    return JWKS_CACHE


def verify_token(token: str):
    """Verifies a JWT access token from Keycloak"""
    jwks = get_jwks()
    try:
        unverified_header = jwt.get_unverified_header(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token header"
        )

    # Find the public key with the same 'kid'
    key = None
    for k in jwks["keys"]:
        if k["kid"] == unverified_header["kid"]:
            key = k
            break

    if not key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Public key not found"
        )

    try:
        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=CLIENT_ID,
            options={"verify_aud": False},
        )
        return payload  # contains user info, roles, etc.
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
