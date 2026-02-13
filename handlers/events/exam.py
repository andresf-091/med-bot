from aiogram import F
from aiogram.types import CallbackQuery
from handlers.base import BaseHandler
from services.text import text_service
from utils.keyboards import inline_kb
from log import get_logger

logger = get_logger(__name__)


class ExamInstructionEvent(BaseHandler):

    def get_filter(self):
        return (F.data.startswith("studytheme_") & F.data.endswith("_2_0")) | (
            F.data.startswith("examinstruction_") & F.data.endswith("_1_0")
        )

    async def handle(self, callback: CallbackQuery):
        await callback.answer("В разработке")
        pass


class ExamPaginationEvent(BaseHandler):

    def get_filter(self):
        return (
            F.data.startswith("examinstruction_") & F.data.endswith("_0_0")
        ) | F.data.startswith("exampagination_")

    async def handle(self, callback: CallbackQuery):
        await callback.answer("В разработке")
        pass
