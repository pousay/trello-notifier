"""Application configuration via pydantic-settings."""

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All runtime configuration loaded from environment / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Telegram
    telegram_bot_token: str = Field(..., description="Telegram bot token from BotFather")
    telegram_chat_id: int = Field(..., description="Target Telegram chat/group ID")

    # Trello
    trello_api_key: str = Field(..., description="Trello REST API key")
    trello_api_token: str = Field(..., description="Trello OAuth token")
    trello_board_id: str = Field(..., description="Trello board ID")
    trello_workspace: str = Field("", description="Trello workspace slug (optional)")

    # Polling
    poll_interval_seconds: int = Field(30, ge=10, description="Seconds between polls")

    # Logging
    log_level: str = Field("INFO", description="Logging level")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached Settings instance."""
    return Settings()
