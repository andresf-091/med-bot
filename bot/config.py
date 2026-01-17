import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()


class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    SESSION_NAME: str = os.getenv("SESSION_NAME", "bot")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/med_bot"
    )

    ADMIN_IDS: list[int] = [int(id) for id in os.getenv("ADMIN_IDS", "").split() if id]

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls) -> bool:
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN обязателен")
        return True
