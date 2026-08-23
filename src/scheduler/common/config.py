import logging

from shared.config import (
    SharedSettings,
    _get_env_overrides,
    _resolve_env_file,
    _try_ssm_overrides,
    resolve_env,
)

logger = logging.getLogger(__name__)


class Settings(SharedSettings):
    sqs_queue_url: str = ""

    digest_summarizer: str = "local"
    bedrock_model_id: str = "apac.amazon.nova-micro-v1:0"


env_name = resolve_env()

_overrides = _get_env_overrides(env_name)

settings = Settings(
    **{"env": env_name, **_overrides},
    _env_file=_resolve_env_file(env_name),
)

_try_ssm_overrides(settings, "shared.ssm")
