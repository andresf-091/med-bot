from aiogram import F
from aiogram.types import CallbackQuery
from handlers.base import BaseHandler
from utils.keyboards import inline_kb
from services.text import text_service
from database import (
    db,
    UserService,
    SubscriptionService,
    UserSubscription,
)
from datetime import datetime
from log import get_logger

logger = get_logger(__name__)


class ProfileEvent(BaseHandler):

    def get_filter(self):
        return F.data == "start_1_0"

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name

        with db.session() as session:
            user_service = UserService(session)
            user_db = user_service.get(tg_id=user.id)[0]

            subscription_service = SubscriptionService(session)
            subscriptions = subscription_service.get(user_id=user_db.id)
            if not subscriptions:
                subscription = subscription_service.create(
                    user_id=user_db.id, type=UserSubscription.FREE
                )
            else:
                subscription = subscriptions[0]

        logger.info(f"Profile menu: {username}")

        buttons = text_service.get("events.profile.buttons")
        keyboard = inline_kb(buttons, self._route)

        text = text_service.get("events.profile.text", username=username)

        await callback.answer()
        await callback.message.edit_text(
            text,
            **self.DEFAULT_SEND_PARAMS,
            reply_markup=keyboard,
        )
