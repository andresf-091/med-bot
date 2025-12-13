import os
from telethon import TelegramClient
from bot.config import Config
from log import get_logger

client = TelegramClient(
    session=Config.SESSION_NAME, api_id=Config.API_ID, api_hash=Config.API_HASH
)
