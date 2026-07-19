import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings  # noqa: E402
from app.models.base import Base  # noqa: E402

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

TIMEZONE = "Asia/Singapore"
_CONNECT_ARGS = {
    "server_settings": {
        "timezone": TIMEZONE,
        "search_path": settings.db_schema,
    },
    "statement_cache_size": 0,
}


def run_migrations_offline() -> None:
    url = settings.database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


def _ensure_async_url(url: str) -> str:
    if url.startswith("postgresql://") and "+asyncpg" not in url:
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


async def run_async_migrations() -> None:
    connectable = create_async_engine(
        _ensure_async_url(settings.database_url),
        poolclass=pool.NullPool,
        connect_args=_CONNECT_ARGS,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
