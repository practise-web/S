from fastapi import Header, HTTPException
from app.services.keycloak_service import verify_token


def get_current_user(authorization: str = Header(...)):
    """Extract and verify Bearer token"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    return payload
