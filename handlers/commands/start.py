from aiogram import F
from aiogram.types import Message
from services.text import text_service
from database import db, UserService
from handlers.base import BaseHandler
from utils.keyboards import inline_kb
from log import get_logger

logger = get_logger(__name__)


class StartCommand(BaseHandler):

    def __init__(self, router):
        super().__init__(router)
        self.handler_type = "message"

    def get_filter(self):
        return F.text == "/start"

    async def handle(self, message: Message):
        user = message.from_user
        username = user.username or user.first_name

        logger.info(f"Start command: {username}")

        buttons = text_service.get("commands.start.buttons")
        keyboard = inline_kb(buttons, self._route)
        text = text_service.get("commands.start.text", username=username)

        await message.reply(
            text,
            **self.DEFAULT_SEND_PARAMS,
            reply_markup=keyboard,
        )
