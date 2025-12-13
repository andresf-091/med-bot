from aiogram import F
from aiogram.types import Message
from handlers.base import BaseHandler
from log import get_logger

logger = get_logger(__name__)


class StartCommand(BaseHandler):
    """Обработчик команды /start"""

    def get_filter(self):
        return F.text == "/start"

    async def handle(self, message: Message):
        user = message.from_user
        logger.info(f"{user.username or user.first_name} started bot")
        await message.reply(
            f"Hello, {user.username or user.first_name}", **self.DEFAULT_SEND_PARAMS
        )
