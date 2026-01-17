from aiogram import F
from aiogram.types import CallbackQuery
from bot.text import text_manager
from handlers.base import BaseHandler
from services.context import context_service
from utils.keyboards import inline_kb
from log import get_logger

logger = get_logger(__name__)


class TheoryVariantsEvent(BaseHandler):

    def get_filter(self):
        return F.data.in_(["studytheme_0_0", "theorypagination_2_0"])

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name
        theme = context_service.get(user.id, "study_theme")

        logger.info(f"Theory variants for theme {theme}: {username}")

        buttons = text_manager.get("events.theory_variants.buttons")
        keyboard = inline_kb(buttons, self._route)
        text = text_manager.get("events.theory_variants.text")

        await callback.answer()
        await callback.message.edit_text(
            text,
            **self.DEFAULT_SEND_PARAMS,
            reply_markup=keyboard,
        )


class TheoryPaginationEvent(BaseHandler):

    def get_filter(self):
        return F.data.in_(["theoryvariants_0_0", "theoryvariants_1_0"])

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name
        variant = callback.data.split("_")[1]
        theme = context_service.get(user.id, "study_theme")

        logger.info(
            f"Theory pagination for variant {variant} and theme {theme}: {username}"
        )

        buttons = text_manager.get("events.theory_pagination.buttons")
        keyboard = inline_kb(buttons, self._route)
        text = text_manager.get("events.theory_pagination.text")

        await callback.answer()
        await callback.message.edit_text(
            text,
            **self.DEFAULT_SEND_PARAMS,
            reply_markup=keyboard,
        )
