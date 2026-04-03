from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional


# корень проекта (где лежит папка app/)
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "AI Telegram News Bot"
    debug: bool = True

    # АБСОЛЮТНЫЙ путь к БД
    database_url: str = f"sqlite:///{BASE_DIR}/aibot.db"

    openai_api_key: str = "mock-key"

    telegram_bot_token: str
    telegram_chat_id: str

    redis_url: Optional[str] = None

    model_config = ConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()
