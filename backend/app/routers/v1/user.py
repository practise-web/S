from fastapi import APIRouter, Depends, status
from app.core.security import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get("/me", status_code=status.HTTP_200_OK, summary="Get current user info")
async def get_user_info(user=Depends(get_current_user)):
    """
    Returns information about the currently authenticated user.
    """
    return {
        "user_id": user.get("sub"),
        "email": user.get("email"),
        "username": user.get("preferred_username"),
        "name": user.get("name"),
        "realm_roles": user.get("realm_access", {}).get("roles", []),
    }
