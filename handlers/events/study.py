from aiogram import F
from aiogram.types import CallbackQuery
from handlers.base import BaseHandler
from utils.keyboards import inline_kb
from services.context import context_service
from services.text import text_service
from log import get_logger

logger = get_logger(__name__)


class StudyThemesEvent(BaseHandler):

    def get_filter(self):
        return F.data.in_(["start_0_0", "studytheme_3_0"])

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name

        context_service.clear(user.id)

        logger.info(f"Study themes: {username}")

        buttons = text_service.get("events.study_themes.buttons")
        keyboard = inline_kb(buttons, self._route)
        text = text_service.get("events.study_themes.text", username=username)

        await callback.answer()
        await callback.message.edit_text(
            text,
            **self.DEFAULT_SEND_PARAMS,
            reply_markup=keyboard,
        )


class StudyThemeEvent(BaseHandler):

    def get_filter(self):
        return F.data.in_(["studythemes_0_0", "studythemes_1_0", "theoryvariants_2_0"])

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name

        theme = context_service.get(user.id, "study_theme")
        if theme is None:
            theme = callback.data.split("_")[1]
            context_service.set(user.id, "study_theme", theme)

        logger.info(f"Study theme {theme}: {username}")

        buttons = text_service.get("events.study_theme.buttons")
        keyboard = inline_kb(buttons, self._route)
        text = text_service.get("events.study_theme.text")

        await callback.answer()
        await callback.message.edit_text(
            text,
            **self.DEFAULT_SEND_PARAMS,
            reply_markup=keyboard,
        )
