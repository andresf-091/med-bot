from aiogram import F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot.text import text_manager
from handlers.base import BaseHandler
from utils.keyboards import inline_kb
from log import get_logger

logger = get_logger(__name__)


class StartCommand(BaseHandler):

    def get_filter(self):
        return F.text == "/start"

    async def handle(self, message: Message):
        user = message.from_user
        username = user.username or user.first_name

        logger.info(f"{username} started bot")

        buttons = text_manager.get("commands.start.buttons")
        keyboard = inline_kb(buttons, self._route)
        text = text_manager.get("commands.start.text", username=username)

        await message.reply(
            text,
            **self.DEFAULT_SEND_PARAMS,
            reply_markup=keyboard,
        )
