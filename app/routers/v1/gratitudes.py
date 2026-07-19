import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_session
from app.schemas.gratitude import GratitudeCreate, GratitudeRead
from app.services import gratitude_service, user_service

router = APIRouter(prefix="/gratitudes", tags=["gratitudes"])


@router.post("", response_model=GratitudeRead, status_code=status.HTTP_201_CREATED)
async def create_gratitude(
    user_id: uuid.UUID,
    data: GratitudeCreate,
    session: AsyncSession = Depends(get_session),
):
    user = await user_service.get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    entry = await gratitude_service.create_gratitude(session, user_id, data)
    return entry


@router.get("", response_model=list[GratitudeRead])
async def list_gratitudes(
    user_id: uuid.UUID,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    entries = await gratitude_service.get_gratitudes_by_user(
        session, user_id, limit=limit, offset=offset
    )
    return entries
