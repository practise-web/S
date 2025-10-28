from fastapi import APIRouter, Depends, status
from services.secure_routes import get_current_user

router = APIRouter(
    prefix="/user",
    tags=["User"],
)

@router.get("/info", status_code=status.HTTP_200_OK,  summary="Get current user info")
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
