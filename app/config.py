import logging
import os
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


def _resolve_env_file(env: str) -> list[str] | None:
    if env in ("test", "sit", "prod"):
        return None
    if env == "dev":
        return [".env.dev", ".env"]
    return None


def _try_ssm_overrides(s: "Settings") -> None:
    if not s.ssm_enabled:
        logger.info("SSM overrides disabled")
        return
    try:
        from app.infrastructure.ssm import load_parameters

        params = load_parameters(s.env, s.ssm_parameter_path)
        logger.info(
            "SSM returned %d parameters for env=%s path=%s",
            len(params),
            s.env,
            s.ssm_parameter_path,
        )
        for key, value in params.items():
            if hasattr(s, key) and value is not None:
                setattr(s, key, value)
                logger.info("Overrode %s from SSM Parameter Store", key)
            else:
                logger.warning(
                    "SSM key %r not found on Settings or value is None", key
                )
    except Exception as exc:
        logger.warning("SSM override failed: %s: %s", type(exc).__name__, exc)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    env: Literal["dev", "sit", "prod"] = Field(
        default="dev",
        validation_alias="APP_ENV",
    )
    debug: bool = False

    app_name: str = "Gratitude Bot"

    database_url: str = ""
    database_echo: bool = False
    db_schema: str = "gratitude_bot"
    db_pool_size: int = Field(default=5, ge=1)
    db_max_overflow: int = Field(default=0, ge=0)

    telegram_bot_token: str = ""
    telegram_webhook_url: str = ""
    telegram_webhook_secret: str = ""

    secret_key: str = "change-me-in-production"
    cors_origins: list[str] = ["*"]

    log_level: str = "INFO"

    ssm_enabled: bool = True
    ssm_parameter_path: str = "/gratitude-bot"


env_name = os.environ.get("APP_ENV", "dev")

_overrides: dict[str, object] = {}
if env_name == "prod":
    _overrides.setdefault("log_level", "WARNING")
    _overrides.setdefault("db_pool_size", 10)
    _overrides.setdefault("db_max_overflow", 20)
elif env_name == "sit":
    _overrides.setdefault("log_level", "INFO")

settings = Settings(
    **{"env": env_name, **_overrides},  # type: ignore[arg-type]
    _env_file=_resolve_env_file(env_name),
)

_try_ssm_overrides(settings)
