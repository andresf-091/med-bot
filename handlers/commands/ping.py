from aiogram import F
from aiogram.types import Message
from handlers.base import BaseHandler
from bot.text import text_manager
from log import get_logger

logger = get_logger(__name__)


class PingCommand(BaseHandler):

    def get_filter(self):
        return F.text == "/ping"

    async def handle(self, message: Message):
        user = message.from_user
        username = user.username or user.first_name

        logger.info(f"Ping received from {username}")

        await message.reply(
            "pong",
            **self.DEFAULT_SEND_PARAMS,
        )
