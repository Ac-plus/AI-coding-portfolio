from fastapi import APIRouter, Depends

from app.api.dependencies import get_user_service
from app.schemas.user import UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
def list_users(user_service: UserService = Depends(get_user_service)) -> list[UserResponse]:
    return [UserResponse(**user.to_dict()) for user in user_service.list_users()]
