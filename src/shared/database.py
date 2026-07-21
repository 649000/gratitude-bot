from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from shared.config import SharedSettings

TIMEZONE = "Asia/Singapore"


def _ensure_async_url(url: str) -> str:
    if url.startswith("postgresql://") and "+asyncpg" not in url:
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def create_engine(settings: SharedSettings) -> AsyncEngine:
    connect_args: dict[str, object] = {
        "server_settings": {
            "timezone": TIMEZONE,
            "search_path": settings.db_schema,
        },
        "statement_cache_size": 0,
    }
    db_url = _ensure_async_url(settings.database_url)

    kwargs: dict[str, object] = {
        "echo": settings.database_echo,
        "connect_args": connect_args,
    }
    if settings.env == "prod":
        kwargs["pool_size"] = settings.db_pool_size
        kwargs["max_overflow"] = settings.db_max_overflow
        kwargs["pool_pre_ping"] = True

    return create_async_engine(db_url, **kwargs)


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
