from aiogram.types import CallbackQuery
from database import SubscriptionService, User, UserSubscription, ReferralService
from bot.config import Config
from services.text import text_service
from utils.keyboards import inline_kb
from datetime import datetime
from dateutil.relativedelta import relativedelta


async def if_not_premium(
    callback: CallbackQuery, username: str, default_send_params: dict
):
    text = text_service.get("events.if_not_premium.text", username=username)
    buttons = text_service.get("events.if_not_premium.buttons")
    keyboard = inline_kb(buttons, "subscribe")

    await callback.message.answer(text, reply_markup=keyboard, **default_send_params)
    await callback.message.delete()


def get_profile_subscription_content(session, user_db):
    subscription_service = SubscriptionService(session)
    subscriptions = subscription_service.get(user_id=user_db.id)
    if not subscriptions:
        subscription = subscription_service.create(
            user_id=user_db.id, type=UserSubscription.FREE
        )
    else:
        subscription = subscriptions[0]

    referral_service = ReferralService(session)
    senders = referral_service.get(referral_id=user_db.id)

    trial_text = ""
    if (subscription.type == UserSubscription.FREE) and not senders:
        subscription_variant = 1
        trial_text = (
            "*🎁 Пробный период:*\n\n*3 дня бесплатно* для новых пользователей\\!\n\n"
        )
    elif subscription.type in [UserSubscription.PREMIUM, UserSubscription.TRIAL]:
        subscription_variant = 2
    else:
        subscription_variant = 0

    buttons = text_service.get("events.profile_subscription.buttons")
    keyboard = inline_kb(
        buttons,
        "profilesubscription",
        variants_map={(0, 0): subscription_variant},
        include_variant_in_callback=True,
    )
    text = text_service.get("events.profile_subscription.text", trial_text=trial_text)
    return text, keyboard


def activate_subscription(subscription_service: SubscriptionService, user_db: User):
    now = datetime.now()
    activation = now
    expiration = now + relativedelta(months=1)
    renewal = expiration

    subscriptions = subscription_service.get(user_id=user_db.id)
    if subscriptions:
        subscription = subscriptions[0]
        if subscription.type in [UserSubscription.PREMIUM, UserSubscription.TRIAL]:
            activation = subscription.activation
            expiration = subscription.expiration + relativedelta(months=1)
            renewal = expiration
        subscription_service.update(
            subscription.id,
            type=UserSubscription.PREMIUM,
            activation=activation,
            expiration=expiration,
            renewal=renewal,
        )
    else:
        subscription_service.create(
            user_id=user_db.id,
            type=UserSubscription.PREMIUM,
            activation=activation,
            expiration=expiration,
            renewal=renewal,
        )


def activate_trial(subscription_service: SubscriptionService, user_db: User):
    now = datetime.now()
    activation = now
    expiration = now + relativedelta(days=Config.TRIAL_PERIOD)
    renewal = expiration

    subscriptions = subscription_service.get(user_id=user_db.id)
    if subscriptions:
        subscription = subscriptions[0]
        if subscription.type is UserSubscription.FREE:
            return subscription_service.update(
                subscription.id,
                type=UserSubscription.TRIAL,
                activation=activation,
                expiration=expiration,
                renewal=renewal,
            )
        else:
            return False
    else:
        return subscription_service.create(
            user_id=user_db.id,
            type=UserSubscription.TRIAL,
            activation=activation,
            expiration=expiration,
            renewal=renewal,
        )
