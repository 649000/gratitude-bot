from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

TIMEZONE = "Asia/Singapore"


def _ensure_async_url(url: str) -> str:
    if url.startswith("postgresql://") and "+asyncpg" not in url:
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


_CONNECT_ARGS = {
    "server_settings": {
        "timezone": TIMEZONE,
        "search_path": settings.db_schema,
    }
}

_DB_URL = _ensure_async_url(settings.database_url)

if settings.env == "prod":
    engine = create_async_engine(
        _DB_URL,
        echo=settings.database_echo,
        connect_args=_CONNECT_ARGS,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_pre_ping=True,
    )
else:
    engine = create_async_engine(
        _DB_URL,
        echo=settings.database_echo,
        connect_args=_CONNECT_ARGS,
    )

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
