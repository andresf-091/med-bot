from aiogram import F
from aiogram.types import CallbackQuery
from handlers.base import BaseHandler
from services.text import text_service
from services.context import context_service
from utils.keyboards import inline_kb
from log import get_logger

logger = get_logger(__name__)


class ExamInstructionEvent(BaseHandler):

    def get_filter(self):
        return F.data.in_(["studytheme_1_0", "examinstruction_1_0"])

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name
        theme = context_service.get(user.id, "study_theme")

        logger.info(f"Exam instruction for theme {theme}: {username}")

        buttons = text_service.get("events.exam_instruction.buttons")
        keyboard = inline_kb(buttons, self._route)
        text = text_service.get("events.exam_instruction.text")

        await callback.answer()
        await callback.message.edit_text(
            text,
            **self.DEFAULT_SEND_PARAMS,
            reply_markup=keyboard,
        )


class ExamPaginationEvent(BaseHandler):

    def get_filter(self):
        return F.data.in_(["examinstruction_0_0"])

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name
        theme = context_service.get(user.id, "study_theme")

        logger.info(f"Exam for theme {theme}: {username}")

        buttons = text_service.get("events.exam_pagination.buttons")
        keyboard = inline_kb(buttons, self._route)
        text = text_service.get("events.exam_pagination.text")

        await callback.answer()
        await callback.message.edit_text(
            text,
            **self.DEFAULT_SEND_PARAMS,
            reply_markup=keyboard,
        )
