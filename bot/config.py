import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()


class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    SESSION_NAME: str = os.getenv("SESSION_NAME", "bot")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "medbot")
    POSTGRES_PORT: int = os.getenv("POSTGRES_PORT", 5432)
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    DATABASE_URL: str = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )

    ADMIN_IDS: list[int] = [
        int(x) for x in os.getenv("ADMIN_IDS", "").split() if x.strip()
    ]
    SUPPORT_GROUP_ID: Optional[int] = (
        int(x) if (x := os.getenv("SUPPORT_GROUP_ID", "").strip()) else None
    )
    PAYMENT_TOKEN: str = os.getenv("PAYMENT_TOKEN", "")

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    REFERRAL_BONUS: int = int(os.getenv("REFERRAL_BONUS", 10))
    TRIAL_PERIOD: int = int(os.getenv("TRIAL_PERIOD", 10))

    @classmethod
    def validate(cls) -> bool:
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN обязателен")
        if not cls.PAYMENT_TOKEN:
            raise ValueError("PAYMENT_TOKEN обязателен")
        return True
