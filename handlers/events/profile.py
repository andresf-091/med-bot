from aiogram import F
from aiogram.types import (
    CallbackQuery,
    LabeledPrice,
    PreCheckoutQuery,
    Message,
    SuccessfulPayment,
)
from bot.config import Config
from handlers.base import BaseHandler
from utils.keyboards import inline_kb
from utils.referral import give_referral_bonus
from utils.subscription import (
    activate_subscription,
    activate_trial,
    get_profile_subscription_content,
)
from services.text import text_service, format_date, escape_md2
from database import (
    db,
    UserService,
    SubscriptionService,
    UserSubscription,
    ReferralService,
    PaymentService,
    PaymentStatus,
)
from log import get_logger
import uuid

logger = get_logger(__name__)


class ProfileEvent(BaseHandler):

    def get_filter(self):
        return F.data.in_(
            [
                "start_1_0",
                "profilesubscription_1_0",
                "paymentsuccessful_0_0",
                "profilesubscriptiontrial_0_0",
                "referral_1_0",
                "referrallink_0_0",
            ]
        )

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

            senders = referral_service.get(referral_id=user_db.id)

        logger.info(f"Profile menu: {username}")

        buttons = text_service.get("events.profile.buttons")
        is_trial = (subscription.type == UserSubscription.FREE) and not senders
        keyboard = inline_kb(
            buttons,
            self._route,
            variants_map={(0, 0): int(is_trial)},
            include_variant_in_callback=True,
        )

        text = text_service.get(
            "events.profile.text",
            username=escape_md2(username),
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
        return F.data.in_(["profile_0_0_0", "profile_0_0_1", "subscribe_0_0"])

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name

        with db.session() as session:
            user_service = UserService(session)
            user_db = user_service.get(tg_id=user.id)[0]
            text, keyboard = get_profile_subscription_content(session, user_db)

        logger.info(f"Profile subscription menu: {username}")

        await callback.answer()
        await callback.message.edit_text(
            text,
            **self.DEFAULT_SEND_PARAMS,
            reply_markup=keyboard,
        )


class ProfileSubscriptionTrialEvent(BaseHandler):
    def get_filter(self):
        return F.data.in_(["profilesubscription_0_0_1"])

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name

        with db.session() as session:
            user_service = UserService(session)
            user_db = user_service.get(tg_id=user.id)[0]

            subscription_service = SubscriptionService(session)
            subscription = activate_trial(subscription_service, user_db)

        if not subscription:
            await callback.message.answer(
                "У вас уже есть/была подписка. Перезайдите в профиль"
            )
            return

        text = text_service.get(
            "events.profile_subscription_trial.text",
            expiration_date=format_date(subscription.expiration),
        )
        buttons = text_service.get("events.profile_subscription_trial.buttons")
        keyboard = inline_kb(buttons, self._route)

        await callback.message.answer(
            text, **self.DEFAULT_SEND_PARAMS, reply_markup=keyboard
        )
        await callback.message.delete()


class PaymentEvent(BaseHandler):
    def get_filter(self):
        return F.data.in_(["profilesubscription_0_0_0", "profilesubscription_0_0_2"])

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name

        title = text_service.get("events.payment.text.title")
        description = text_service.get("events.payment.text.description")

        with db.session() as session:
            user_service = UserService(session)
            user_db = user_service.get(tg_id=user.id)[0]

            transaction_id = str(uuid.uuid4())

            payment_service = PaymentService(session)
            payments = payment_service.get(user_id=user_db.id)
            for payment in payments:
                if payment.status == PaymentStatus.PENDING:
                    payment_service.update(payment.id, status=PaymentStatus.CANCELLED)

            payment = payment_service.create(
                user_id=user_db.id,
                status=PaymentStatus.PENDING,
                amount=199,
                transaction_id=transaction_id,
            )

        logger.info(f"Payment requested for payment {payment.id} for user {username}")

        buttons = text_service.get("events.payment.buttons")
        keyboard = inline_kb(
            buttons,
            self._route,
            button_kwargs_map={(0, 0): {"pay": True, "callback_data": None}},
        )

        await callback.message.answer_invoice(
            title=title,
            description=description,
            payload=transaction_id,
            provider_token=Config.PAYMENT_TOKEN,
            currency="RUB",
            prices=[
                LabeledPrice(label=title, amount=19900),
            ],
            start_parameter="payment",
            is_flexible=False,
            reply_markup=keyboard,
        )
        await callback.message.delete()


class PaymentPreCheckoutEvent(BaseHandler):
    def __init__(self, router):
        super().__init__(router)
        self.handler_type = "pre_checkout_query"

    def get_filter(self):
        return None

    async def handle(self, pre_checkout_query: PreCheckoutQuery):
        user = pre_checkout_query.from_user
        username = user.username or user.first_name

        transaction_id = pre_checkout_query.invoice_payload

        with db.session() as session:
            user_service = UserService(session)
            user_db = user_service.get(tg_id=user.id)[0]

            payment_service = PaymentService(session)
            payments = payment_service.get(transaction_id=transaction_id)

        if not payments:
            await pre_checkout_query.answer(ok=False, error_message="Платеж не найден")
            return

        payment = payments[0]

        if payment.user_id != user_db.id:
            await pre_checkout_query.answer(
                ok=False, error_message="Неверный пользователь"
            )
            payment_service.update(payment.id, status=PaymentStatus.FAILED)
            return

        if payment.status != PaymentStatus.PENDING:
            await pre_checkout_query.answer(
                ok=False, error_message="Платеж уже обработан"
            )
            payment_service.update(payment.id, status=PaymentStatus.FAILED)
            return

        await pre_checkout_query.answer(ok=True)
        logger.info(
            f"Pre-checkout approved for payment {payment.id} for user {username}"
        )


class PaymentSuccessfulEvent(BaseHandler):
    def __init__(self, router):
        super().__init__(router)
        self.handler_type = "successful_payment"

    def get_filter(self):
        return None

    async def handle(self, message: Message):
        successful_payment: SuccessfulPayment = message.successful_payment
        transaction_id = successful_payment.invoice_payload
        user = message.from_user
        username = user.username or user.first_name

        with db.session() as session:
            user_service = UserService(session)
            user_db = user_service.get(tg_id=user.id)[0]

            payment_service = PaymentService(session)
            payments = payment_service.get(transaction_id=transaction_id)
            if payments:
                payment = payments[0]
                if payment.user_id == user_db.id:
                    payment_service.update(payment.id, status=PaymentStatus.COMPLETED)

                    subscription_service = SubscriptionService(session)
                    referral_service = ReferralService(session)

                    activate_subscription(subscription_service, user_db)
                    give_referral_bonus(referral_service, subscription_service, user_db)

        if not payments:
            logger.error(
                f"Платеж не найден {transaction_id} для пользователя {username}"
            )
            return
        if payment.user_id != user_db.id:
            logger.error(
                f"Пользователь не соответствует платежу {payment.user_id} != {user_db.id}"
            )
            return

        logger.info(f"Payment successful: {transaction_id} for user {user_db.id}")

        text = text_service.get("events.payment_successful.text")
        buttons = text_service.get("events.payment_successful.buttons")
        keyboard = inline_kb(buttons, self._route)

        await message.answer(text, **self.DEFAULT_SEND_PARAMS, reply_markup=keyboard)
        await message.delete()


class PaymentCancelEvent(BaseHandler):
    def get_filter(self):
        return F.data.in_(["payment_1_0"])

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name

        with db.session() as session:
            user_service = UserService(session)
            user_db = user_service.get(tg_id=user.id)[0]

            payment_service = PaymentService(session)
            payments = payment_service.get(user_id=user_db.id)
            for payment in payments:
                if payment.status == PaymentStatus.PENDING:
                    payment_service.update(payment.id, status=PaymentStatus.CANCELLED)

            text, keyboard = get_profile_subscription_content(session, user_db)

        logger.info(f"Payment cancelled for user {username} {user_db.id}")

        await callback.message.answer(
            text,
            **self.DEFAULT_SEND_PARAMS,
            reply_markup=keyboard,
        )
        await callback.message.delete()
