from aiogram import F
from aiogram.types import CallbackQuery
from handlers.base import BaseHandler
from utils.keyboards import inline_kb
from services.text import text_service
from database import db, UserService
from log import get_logger

logger = get_logger(__name__)


class ReferralEvent(BaseHandler):
    def get_filter(self):
        return F.data == "profile_1_0"

    async def handle(self, callback: CallbackQuery):
        with db.session() as session:
            user_service = UserService(session)
            users = user_service.get(tg_id=callback.from_user.id)
            if not users:
                await callback.answer("Ошибка", show_alert=True)
                return
            user_db = users[0]

        text = text_service.get("events.referral.text")
        buttons = text_service.get("events.referral.buttons")
        keyboard = inline_kb(buttons, self._route)

        await callback.answer()
        await callback.message.edit_text(
            text,
            **self.DEFAULT_SEND_PARAMS,
            reply_markup=keyboard,
        )


class ReferralGetLinkEvent(BaseHandler):
    def get_filter(self):
        return F.data == "referral_0_0"

    async def handle(self, callback: CallbackQuery):
        bot_user = await callback.bot.get_me()
        with db.session() as session:
            user_service = UserService(session)
            users = user_service.get(tg_id=callback.from_user.id)
            if not users:
                await callback.answer("Ошибка", show_alert=True)
                return
            user_db = users[0]
            ref_code = user_service.ensure_ref_code(user_db)

        link = f"https://t.me/{bot_user.username}?start=ref{ref_code}"
        text = text_service.get("events.referral_link.text", link=link)

        await callback.answer()
        await callback.message.reply(
            text,
            **self.DEFAULT_SEND_PARAMS,
        )
