from aiogram import F
from aiogram.types import CallbackQuery
from handlers.base import BaseHandler
from services.context import context_service
from services.text import text_service
from database import db, UserService
from utils.keyboards import inline_kb
from utils.subscription import if_not_premium
from log import get_logger

logger = get_logger(__name__)


class StartMenuEvent(BaseHandler):
    def get_filter(self):
        return F.data.in_(["studythemes_0_0"])

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name

        with db.session() as session:
            user_service = UserService(session)
            users = user_service.get(tg_id=user.id)
            if not users:
                user_service.create(tg_id=user.id, username=username)
            user_db = users[0]
            is_premium = user_service.is_premium(user_db.id)

        if not is_premium:
            await if_not_premium(callback, username, self.DEFAULT_SEND_PARAMS)
            return

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


class CheckEvent(BaseHandler):

    def get_filter(self):
        return F.data != "a"

    async def handle(self, callback: CallbackQuery):
        logger.debug(f"Check event: {callback.data}")
