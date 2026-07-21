from scheduler.common.config import settings
from shared.database import create_engine as _create_engine
from shared.database import create_session_factory

engine = _create_engine(settings)
async_session_factory = create_session_factory(engine)
