from aiogram import F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from handlers.base import BaseHandler
from database import db, ThemeService, UserService
from utils.keyboards import inline_kb
from utils.subscription import if_not_premium
from services.context import context_service
from services.text import text_service
from log import get_logger

logger = get_logger(__name__)


class StudyThemesEvent(BaseHandler):

    def get_filter(self):
        return F.data.in_(["start_0_0", "studytheme_4_0"]) | (
            F.data.startswith("studytheme_") & F.data.endswith("_4_0")
        )

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name

        context_service.clear(user.id)

        with db.session() as session:
            user_service = UserService(session)
            user_db = user_service.get(tg_id=user.id)[0]
            is_premium = user_service.is_premium(user_db.id)

            if is_premium:
                theme_service = ThemeService(session)
                themes = theme_service.get()

        if not is_premium:
            await if_not_premium(callback, username, self.DEFAULT_SEND_PARAMS)
            return
        if not themes:
            await callback.answer("Темы не найдены")
            return

        logger.info(f"Study themes: {username}")

        buttons = text_service.get("events.study_themes.buttons", copy_obj=True)
        first_row = inline_kb([buttons[0]], self._route).inline_keyboard[0]
        theme_rows = [
            [
                InlineKeyboardButton(
                    text=t.name, callback_data=f"studythemes_{t.id}_{i+1}_0"
                )
            ]
            for i, t in enumerate(themes)
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[first_row] + theme_rows)
        text = text_service.get("events.study_themes.text", username=username)

        await callback.answer()
        await callback.message.edit_text(
            text,
            **self.DEFAULT_SEND_PARAMS,
            reply_markup=keyboard,
        )


class StudyThemeEvent(BaseHandler):

    def get_filter(self):
        cond_1 = (F.data.startswith("theoryvariants_") & F.data.endswith("_2_0")) | (
            F.data.startswith("slideslist_") & F.data.endswith("_0_0")
        )
        cond_2 = F.data.startswith("studythemes_") & (F.data != "studythemes_0_0")
        cond_3 = F.data.startswith("taskpagination_") & F.data.endswith("_3_0")
        return cond_1 | cond_2 | cond_3

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name

        parts = callback.data.split("_")
        theme_id = int(parts[1])

        with db.session() as session:
            user_service = UserService(session)
            user_db = user_service.get(tg_id=user.id)[0]
            is_premium = user_service.is_premium(user_db.id)

            if is_premium:
                theme_service = ThemeService(session)
                themes = theme_service.get(id=theme_id)

        if not is_premium:
            await if_not_premium(callback, username, self.DEFAULT_SEND_PARAMS)
            return
        if not themes:
            await callback.answer("Тема не найдена")
            return

        logger.info(f"Study theme {theme_id}: {username}")

        buttons = text_service.get("events.study_theme.buttons")
        keyboard = inline_kb(buttons, f"studytheme_{theme_id}")
        text = text_service.get("events.study_theme.text")

        await callback.answer()
        await callback.message.edit_text(
            text,
            **self.DEFAULT_SEND_PARAMS,
            reply_markup=keyboard,
        )
