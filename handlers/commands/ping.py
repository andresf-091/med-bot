from aiogram import F
from aiogram.types import Message
from handlers.base import BaseHandler
from log import get_logger

logger = get_logger(__name__)


class PingCommand(BaseHandler):

    def __init__(self, router):
        super().__init__(router)
        self.handler_type = "message"

    def get_filter(self):
        return F.text == "/ping"

    async def handle(self, message: Message):
        user = message.from_user
        username = user.username or user.first_name

        logger.info(f"Ping command: {username}")

        await message.reply(
            "pong",
            **self.DEFAULT_SEND_PARAMS,
        )
