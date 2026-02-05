from aiogram import F
from aiogram.types import CallbackQuery
from handlers.base import BaseHandler
from database import db, ThemeService
from utils.keyboards import inline_kb
from services.context import context_service
from services.text import text_service
from log import get_logger

logger = get_logger(__name__)


class StudyThemesEvent(BaseHandler):

    def get_filter(self):
        return F.data.in_(["start_0_0", "studytheme_4_0"])

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name

        context_service.clear(user.id)

        with db.session() as session:
            theme_service = ThemeService(session)
            themes = theme_service.get()

        if not themes:
            await callback.answer("Темы не найдены")
            return

        logger.info(f"Study themes: {username}")

        buttons = text_service.get("events.study_themes.buttons", copy_obj=True)
        for theme in themes:
            buttons.append([theme.name])
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
        cond_1 = F.data.in_(
            [
                "theoryvariants_2_0",
                "slideslist_0_0",
            ]
        )
        cond_2 = F.data.startswith("studythemes_") & (~F.data.endswith("_0_0"))
        cond_3 = F.data.startswith("taskpagination_") & F.data.endswith("_3_0")
        return cond_1 | cond_2 | cond_3

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name

        theme_id = context_service.get(user.id, "study_theme")
        if theme_id is None:
            theme_id = int(callback.data.split("_")[1]) - 1
            context_service.set(user.id, "study_theme", theme_id)

        with db.session() as session:
            theme_service = ThemeService(session)
            theme = theme_service.get(id=theme_id)
            if not theme:
                await callback.answer("Тема не найдена")
                return

        logger.info(f"Study theme {theme_id}: {username}")

        buttons = text_service.get("events.study_theme.buttons")
        keyboard = inline_kb(buttons, self._route)
        text = text_service.get("events.study_theme.text")

        await callback.answer()
        await callback.message.edit_text(
            text,
            **self.DEFAULT_SEND_PARAMS,
            reply_markup=keyboard,
        )
