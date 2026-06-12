from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: str

    TRELLO_API_KEY: str
    TRELLO_TOKEN: str
    TRELLO_BOARD_ID: str

    POLL_INTERVAL: int = 60

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
