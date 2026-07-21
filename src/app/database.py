from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from shared.database import create_engine as _create_engine
from shared.database import create_session_factory

engine = _create_engine(settings)
async_session_factory = create_session_factory(engine)


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
