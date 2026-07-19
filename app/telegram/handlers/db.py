import uuid
from collections.abc import AsyncGenerator
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.models.gratitude import GratitudeEntry
from app.models.preference import UserPreference
from app.models.prompt import Prompt
from app.models.user import User


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session_factory() as session:
        yield session


async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
) -> User:
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    if user is None:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        session.add(user)
        await session.flush()
    return user


async def get_or_create_preferences(
    session: AsyncSession,
    user_id: uuid.UUID,
) -> UserPreference:
    result = await session.execute(
        select(UserPreference).where(UserPreference.user_id == user_id)
    )
    pref = result.scalar_one_or_none()
    if pref is None:
        pref = UserPreference(user_id=user_id)
        session.add(pref)
        await session.flush()
    return pref


async def get_random_prompt(session: AsyncSession) -> str:
    result = await session.execute(
        select(Prompt).order_by(func.random()).limit(1)
    )
    prompt = result.scalar_one_or_none()
    return prompt.text if prompt else "What are you grateful for today?"


async def create_entry(
    session: AsyncSession,
    user_id: uuid.UUID,
    content: str,
    source: str = "telegram",
) -> GratitudeEntry:
    entry = GratitudeEntry(user_id=user_id, content=content, source=source)
    session.add(entry)
    await session.flush()
    return entry


async def get_random_entry(
    session: AsyncSession,
    user_id: uuid.UUID,
) -> GratitudeEntry | None:
    result = await session.execute(
        select(GratitudeEntry).where(
            GratitudeEntry.user_id == user_id
        ).order_by(func.random()).limit(1)
    )
    return result.scalar_one_or_none()


async def get_entry_by_id(
    session: AsyncSession,
    entry_id: uuid.UUID,
) -> GratitudeEntry | None:
    return await session.get(GratitudeEntry, entry_id)


async def get_entries(
    session: AsyncSession,
    user_id: uuid.UUID,
    year: int | None = None,
    month: int | None = None,
    day: int | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[GratitudeEntry]:
    query = select(GratitudeEntry).where(
        GratitudeEntry.user_id == user_id
    )
    if year:
        query = query.where(
            func.extract("year", GratitudeEntry.created_at) == year
        )
    if month:
        query = query.where(
            func.extract("month", GratitudeEntry.created_at) == month
        )
    if day:
        query = query.where(
            func.extract("day", GratitudeEntry.created_at) == day
        )
    query = query.order_by(GratitudeEntry.created_at.desc()).limit(limit).offset(offset)
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_distinct_years(
    session: AsyncSession,
    user_id: uuid.UUID,
) -> list[int]:
    result = await session.execute(
        select(
            func.distinct(
                func.extract("year", GratitudeEntry.created_at)
            ).label("year")
        )
        .where(GratitudeEntry.user_id == user_id)
        .order_by(func.extract("year", GratitudeEntry.created_at).desc())
    )
    return [int(row[0]) for row in result.all() if row[0] is not None]


async def get_distinct_months(
    session: AsyncSession,
    user_id: uuid.UUID,
    year: int,
) -> list[int]:
    result = await session.execute(
        select(
            func.distinct(
                func.extract("month", GratitudeEntry.created_at)
            ).label("month")
        )
        .where(
            GratitudeEntry.user_id == user_id,
            func.extract("year", GratitudeEntry.created_at) == year,
        )
        .order_by(func.extract("month", GratitudeEntry.created_at).desc())
    )
    return [int(row[0]) for row in result.all() if row[0] is not None]


async def get_distinct_days(
    session: AsyncSession,
    user_id: uuid.UUID,
    year: int,
    month: int,
) -> list[int]:
    result = await session.execute(
        select(
            func.distinct(
                func.extract("day", GratitudeEntry.created_at)
            ).label("day")
        )
        .where(
            GratitudeEntry.user_id == user_id,
            func.extract("year", GratitudeEntry.created_at) == year,
            func.extract("month", GratitudeEntry.created_at) == month,
        )
        .order_by(func.extract("day", GratitudeEntry.created_at).desc())
    )
    return [int(row[0]) for row in result.all() if row[0] is not None]


async def delete_entry(
    session: AsyncSession,
    entry_id: uuid.UUID,
) -> bool:
    entry = await session.get(GratitudeEntry, entry_id)
    if entry:
        await session.delete(entry)
        await session.flush()
        return True
    return False


async def star_entry(
    session: AsyncSession,
    entry_id: uuid.UUID,
    starred: bool = True,
) -> bool:
    entry = await session.get(GratitudeEntry, entry_id)
    if entry:
        entry.starred = starred
        await session.flush()
        return True
    return False


async def update_user(
    session: AsyncSession,
    telegram_id: int,
    **kwargs,
) -> User | None:
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    if user:
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        await session.flush()
    return user


async def update_preference(
    session: AsyncSession,
    user_id: uuid.UUID,
    **kwargs,
) -> UserPreference | None:
    result = await session.execute(
        select(UserPreference).where(UserPreference.user_id == user_id)
    )
    pref = result.scalar_one_or_none()
    if pref:
        for key, value in kwargs.items():
            if hasattr(pref, key) and value is not None:
                setattr(pref, key, value)
        await session.flush()
    return pref


async def has_entry_today(
    session: AsyncSession,
    user_id: uuid.UUID,
    today: datetime | None = None,
) -> bool:
    if today is None:
        today = datetime.now()
    result = await session.execute(
        select(func.count()).where(
            GratitudeEntry.user_id == user_id,
            func.date(GratitudeEntry.created_at) == today.date(),
        )
    )
    return result.scalar() > 0


async def export_entries(
    session: AsyncSession,
    user_id: uuid.UUID,
) -> list[GratitudeEntry]:
    result = await session.execute(
        select(GratitudeEntry)
        .where(GratitudeEntry.user_id == user_id)
        .order_by(GratitudeEntry.created_at.asc())
    )
    return list(result.scalars().all())


async def complete_onboarding(
    session: AsyncSession,
    user_id: uuid.UUID,
) -> UserPreference | None:
    result = await session.execute(
        select(UserPreference).where(UserPreference.user_id == user_id)
    )
    pref = result.scalar_one_or_none()
    if pref:
        pref.onboarding_completed = True
        await session.flush()
    return pref
