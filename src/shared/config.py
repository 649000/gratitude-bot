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


def _try_ssm_overrides(s: "SharedSettings", ssm_module_name: str) -> None:
    if not s.ssm_enabled:
        logger.info("SSM overrides disabled")
        return
    try:
        from importlib import import_module

        ssm_mod = import_module(ssm_module_name)
        params = ssm_mod.load_parameters(s.env, s.ssm_parameter_path)
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
                logger.warning("SSM key %r not found on Settings or value is None", key)
    except Exception as exc:
        logger.warning("SSM override failed: %s: %s", type(exc).__name__, exc)


class SharedSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    env: Literal["dev", "sit", "prod", "test"] = Field(
        default="dev",
        validation_alias="APP_ENV",
    )
    debug: bool = False

    database_url: str = ""
    database_echo: bool = False
    db_schema: str = "gratitude_bot"
    db_pool_size: int = Field(default=5, ge=1)
    db_max_overflow: int = Field(default=0, ge=0)

    log_level: str = "INFO"

    ssm_enabled: bool = True
    ssm_parameter_path: str = "/gratitude-bot"


_ENV_OVERRIDES: dict[str, dict[str, object]] = {
    "prod": {"log_level": "WARNING", "db_pool_size": 10, "db_max_overflow": 20},
    "sit": {"log_level": "INFO"},
}


def _get_env_overrides(env_name: str) -> dict[str, object]:
    overrides: dict[str, object] = {}
    overrides.update(_ENV_OVERRIDES.get(env_name, {}))
    return overrides


def resolve_env() -> str:
    return os.environ.get("APP_ENV", "dev")
