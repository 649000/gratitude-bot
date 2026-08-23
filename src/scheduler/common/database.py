import asyncio

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from scheduler.common.config import settings
from shared.database import create_engine as _create_engine
from shared.database import create_session_factory as _make_factory


class _LazySessionFactory:
    def __init__(self):
        self._engine: AsyncEngine | None = None
        self._factory: async_sessionmaker[AsyncSession] | None = None
        self._loop_id: int | None = None

    def _ensure(self):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        loop_id = id(loop) if loop else None
        if self._engine is None or self._loop_id != loop_id:
            if self._engine is not None:
                self._engine.sync_engine.dispose()
            self._engine = _create_engine(settings)
            self._factory = _make_factory(self._engine)
            self._loop_id = loop_id

    def __call__(self):
        self._ensure()
        assert self._factory is not None
        return self._factory()

    async def dispose(self):
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._factory = None
            self._loop_id = None


async_session_factory = _LazySessionFactory()
