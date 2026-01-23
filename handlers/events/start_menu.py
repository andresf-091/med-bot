from aiogram import F
from aiogram.types import CallbackQuery
from handlers.base import BaseHandler
from services.context import context_service
from services.text import text_service
from utils.keyboards import inline_kb
from log import get_logger

logger = get_logger(__name__)


class StartMenuEvent(BaseHandler):
    def get_filter(self):
        return F.data.in_(["studythemes_2_0"])

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name

        logger.info(f"Start menu: {username}")

        buttons = text_service.get("commands.start.buttons")
        keyboard = inline_kb(buttons, "start")
        text = text_service.get("commands.start.text", username=username)

        await callback.answer()
        await callback.message.edit_text(
            text,
            **self.DEFAULT_SEND_PARAMS,
            reply_markup=keyboard,
        )
