from aiogram import F
from aiogram.types import CallbackQuery
from handlers.base import BaseHandler
from services.text import text_service
from utils.keyboards import inline_kb
from log import get_logger

logger = get_logger(__name__)


class FaqEvent(BaseHandler):
    def get_filter(self):
        return F.data.in_(["start_2_0"])

    async def handle(self, callback: CallbackQuery):
        await callback.answer("В разработке")
        pass
