from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "Gratitude Bot"
    app_env: str = "development"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/gratitude_bot"
    database_echo: bool = False

    telegram_bot_token: str = ""
    telegram_webhook_url: str = ""
    telegram_webhook_secret: str = ""

    secret_key: str = "change-me-in-production"
    cors_origins: list[str] = ["*"]

    log_level: str = "INFO"


settings = Settings()
