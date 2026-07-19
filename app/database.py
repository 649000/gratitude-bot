from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

TIMEZONE = "Asia/Singapore"
_CONNECT_ARGS = {
    "server_settings": {
        "timezone": TIMEZONE,
        "search_path": settings.db_schema,
    }
}

if settings.env == "prod":
    engine = create_async_engine(
        settings.database_url,
        echo=settings.database_echo,
        connect_args=_CONNECT_ARGS,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_pre_ping=True,
    )
else:
    engine = create_async_engine(
        settings.database_url,
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
