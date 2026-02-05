from aiogram import F
from aiogram.types import CallbackQuery
from handlers.base import BaseHandler
from services.text import text_service
from utils.keyboards import inline_kb
from log import get_logger

logger = get_logger(__name__)


class ExamInstructionEvent(BaseHandler):

    def get_filter(self):
        return (
            (F.data.startswith("studytheme_") & F.data.endswith("_2_0"))
            | (F.data.startswith("examinstruction_") & F.data.endswith("_1_0"))
        )

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name
        theme_id = int(callback.data.split("_")[1])

        logger.info(f"Exam instruction for theme {theme_id}: {username}")

        buttons = text_service.get("events.exam_instruction.buttons")
        keyboard = inline_kb(buttons, f"examinstruction_{theme_id}")
        text = text_service.get("events.exam_instruction.text")

        await callback.answer()
        await callback.message.edit_text(
            text,
            **self.DEFAULT_SEND_PARAMS,
            reply_markup=keyboard,
        )


class ExamPaginationEvent(BaseHandler):

    def get_filter(self):
        return (
            (F.data.startswith("examinstruction_") & F.data.endswith("_0_0"))
            | F.data.startswith("exampagination_")
        )

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name
        theme_id = int(callback.data.split("_")[1])

        logger.info(f"Exam for theme {theme_id}: {username}")

        buttons = text_service.get("events.exam_pagination.buttons")
        keyboard = inline_kb(buttons, f"exampagination_{theme_id}")
        text = text_service.get("events.exam_pagination.text")

        await callback.answer()
        await callback.message.edit_text(
            text,
            **self.DEFAULT_SEND_PARAMS,
            reply_markup=keyboard,
        )
