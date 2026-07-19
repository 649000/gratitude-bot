from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_session
from app.schemas.user import UserCreate, UserRead
from app.services import user_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserCreate,
    session: AsyncSession = Depends(get_session),
):
    existing = await user_service.get_user_by_telegram_id(session, data.telegram_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this Telegram ID already exists",
        )
    user = await user_service.create_user(session, data)
    return user


@router.get("/me", response_model=UserRead)
async def get_me(
    telegram_id: int,
    session: AsyncSession = Depends(get_session),
):
    user = await user_service.get_user_by_telegram_id(session, telegram_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user
