import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Config:
    API_ID: int = int(os.getenv('API_ID', '0'))
    API_HASH: str = os.getenv('API_HASH', '')
    SESSION_NAME: str = os.getenv('SESSION_NAME', 'bot')
    
    ADMIN_IDS: list[int] = [
        int(id) for id in os.getenv('ADMIN_IDS', '').split() if id
    ]

    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls) -> bool:
        if not cls.API_ID or not cls.API_HASH:
            raise ValueError("API_ID и/или API_HASH обязательны")
        return True
