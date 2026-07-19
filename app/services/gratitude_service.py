import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.gratitude import GratitudeEntry
from app.schemas.gratitude import GratitudeCreate


async def create_gratitude(
    session: AsyncSession,
    user_id: uuid.UUID,
    data: GratitudeCreate,
) -> GratitudeEntry:
    entry = GratitudeEntry(
        user_id=user_id,
        content=data.content,
        source=data.source,
    )
    session.add(entry)
    await session.flush()
    return entry


async def get_gratitudes_by_user(
    session: AsyncSession,
    user_id: uuid.UUID,
    limit: int = 50,
    offset: int = 0,
) -> list[GratitudeEntry]:
    result = await session.execute(
        select(GratitudeEntry)
        .where(GratitudeEntry.user_id == user_id)
        .order_by(GratitudeEntry.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())
