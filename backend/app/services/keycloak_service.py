from app.schemas.user_schema import UserInternal
from fastapi import HTTPException, status, Request
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
from app.core.config import kcsettings
from app.core import network as net
import httpx


class KeycloakAdmin:
    def __init__(self):
        self.JWKS_CACHE = None
        self.TOKEN_CACHE = None

    async def __get_jwks(self):
        if self.JWKS_CACHE:
            return self.JWKS_CACHE
        response = await net.client.get(kcsettings.KEYCLOAK_JWK_URL)
        self.JWKS_CACHE = response.json()
        return self.JWKS_CACHE

    async def verify_token(self, token: str):
        """Verifies a JWT access token from Keycloak"""
        jwks = await self.__get_jwks()
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
                audience=kcsettings.KEYCLOAK_CLIENT_ID,
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

    async def get_admin_token(self):
        """Get admin access token from Keycloak"""
        data = {
            "client_id": kcsettings.KEYCLOAK_CLIENT_ID,
            "client_secret": kcsettings.KEYCLOAK_CLIENT_SECRET,
            "username": kcsettings.KEYCLOAK_USERNAME,
            "password": kcsettings.KEYCLOAK_PASSWORD,
            "grant_type": "password",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = await net.client.post(
            kcsettings.KEYCLOAK_TOKEN_URL, data=data, headers=headers
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get admin token",
            )
        return response.json()["access_token"]

    async def trigger_email_action(
        self, user_id: str, action: str, token: str, redirect_uri: str = None
    ):
        """
        Triggers Keycloak to send an email for a specific action.
        Actions: 'UPDATE_PASSWORD', 'UPDATE_EMAIL', 'VERIFY_EMAIL'
        """
        params = {"client_id": kcsettings.KEYCLOAK_CLIENT_ID}
        if redirect_uri:
            params["redirectUri"] = redirect_uri
        try:
            response = await net.client.put(
                kcsettings.KEYCLOAK_EMAIL_ACTIONS_URL(user_id),
                json=[action],  # List of actions to trigger
                headers={"Authorization": f"Bearer {token}"},
                params=params,
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to trigger email action: {str(e)}",
            )

    async def get_user_id_by_email(self, email: str, token: str):
        try:
            resp = await net.client.get(
                kcsettings.KEYCLOAK_USERS_URL(),
                params={"email": email, "exact": True},
                headers={"Authorization": f"Bearer {token}"},
            )
            users = resp.json()
            if not users:
                return None
            return users[0]["id"]
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get user by email: {str(e)}",
            )

    # Additional admin functions, maybe used in the future:
    async def reset_password(self, user_id: str, new_password: str, token: str):
        payload = {"type": "password", "value": new_password, "temporary": False}
        try:
            await net.client.put(
                kcsettings.KEYCLOAK_RESET_PASSWORD_URL(user_id),
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
            )
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to reset password: {str(e)}",
            )

    async def update_email(self, user_id: str, new_email: str, token: str):
        payload = {"email": new_email, "emailVerified": True}
        try:
            await net.client.put(
                kcsettings.KEYCLOAK_USERS_URL(user_id),
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
            )
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update email: {str(e)}",
            )

    async def get_current_user(self, request: Request):
        """
        Check if the Middleware found a valid session.
        """
        user_payload = getattr(request.state, "user", None)
        if not user_payload:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")

        # Convert Dict -> Pydantic Model
        return UserInternal(**user_payload)


kc_admin = KeycloakAdmin()
