from fastapi import APIRouter, Depends, status
from app.services.keycloak_service import kc_admin
from app.schemas.user_schema import UserInternal

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get("/me", status_code=status.HTTP_200_OK, summary="Get current user info")
async def get_user_info(user: UserInternal = Depends(kc_admin.get_current_user)):
    """
    Returns information about the currently authenticated user.
    """
    return {
        "user_id": user.sub,
        "email": user.email,
        "username": user.username,
        "roles": user.roles,
    }


# Additional API endpoints for user info, will be added soon
