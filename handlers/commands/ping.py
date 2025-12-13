from aiogram import F
from aiogram.types import Message
from handlers.base import BaseHandler
from log import get_logger

logger = get_logger(__name__)


class PingCommand(BaseHandler):

    def get_filter(self):
        return F.text == "/ping"

    async def handle(self, message: Message):
        user = message.from_user
        logger.info(f"Ping received from {user.username or user.id}")
        await message.reply("pong", **self.DEFAULT_SEND_PARAMS)
