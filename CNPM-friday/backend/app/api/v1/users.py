from fastapi import APIRouter, Depends

from app.api import deps
from app.models.all_models import User
from app.schemas import user as user_schema

router = APIRouter()


@router.get("/me", response_model=user_schema.UserResponse, tags=["users"])
async def read_current_user(current_user: User = Depends(deps.get_current_user)) -> user_schema.UserResponse:
    """Return the currently authenticated user's profile."""
    return current_user
