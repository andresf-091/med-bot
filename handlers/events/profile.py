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
    ReferralService,
)
from datetime import datetime
from log import get_logger

logger = get_logger(__name__)


def format_date(date):
    if date is None:
        return "Нет"
    formatted = date.strftime("%d.%m.%Y %H:%M")
    return formatted.replace("-", "\\-").replace(".", "\\.")


class ProfileEvent(BaseHandler):

    def get_filter(self):
        return F.data.in_(["start_1_0", "profilesubscription_1_0"])

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name

        referrals_active_count = 0

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

            referral_service = ReferralService(session)
            referrals = referral_service.get(user_id=user_db.id)
            for referral in referrals:
                if user_service.is_premium(referral.referral_id):
                    referrals_active_count += 1

        logger.info(f"Profile menu: {username}")

        buttons = text_service.get("events.profile.buttons")
        keyboard = inline_kb(buttons, self._route, include_variant_in_callback=True)

        text = text_service.get(
            "events.profile.text",
            username=username,
            created_at=format_date(user_db.created_at),
            subscription_type=subscription.type.value if subscription.type else "FREE",
            activation_date=format_date(subscription.activation),
            expiration_date=format_date(subscription.expiration),
            renewal_date=format_date(subscription.renewal),
            referrals_active=referrals_active_count,
            referrals_count=len(referrals),
        )

        await callback.answer()
        await callback.message.edit_text(
            text,
            **self.DEFAULT_SEND_PARAMS,
            reply_markup=keyboard,
        )


class ProfileSubscriptionEvent(BaseHandler):

    def get_filter(self):
        return F.data.in_(["profile_0_0_0", "profile_0_0_1"])

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name

        logger.info(f"Profile subscription menu: {username}")

        text = text_service.get("events.profile_subscription.text")
        buttons = text_service.get("events.profile_subscription.buttons")
        keyboard = inline_kb(buttons, self._route, include_variant_in_callback=True)

        await callback.answer()
        await callback.message.edit_text(
            text,
            **self.DEFAULT_SEND_PARAMS,
            reply_markup=keyboard,
        )
