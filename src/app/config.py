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
    app_name: str = "Gratitude Bot"

    telegram_bot_token: str = ""
    telegram_webhook_url: str = ""

    secret_key: str = "change-me-in-production"
    cors_origins: list[str] = ["*"]


env_name = resolve_env()

_overrides = _get_env_overrides(env_name)

settings = Settings(
    **{"env": env_name, **_overrides},
    _env_file=_resolve_env_file(env_name),
)

_try_ssm_overrides(settings, "shared.ssm")
