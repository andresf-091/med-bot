from database import (
    db,
    UserService,
    SubscriptionService,
    UserSubscription,
    ReferralService,
    PaymentService,
    PaymentStatus,
)
from datetime import datetime, timedelta
from bot.config import Config


REF_CODE_LEN = 32


def validate_referral_code(referral_code: str):
    if not referral_code.startswith("ref"):
        return False
    suffix = referral_code[3:]
    if len(suffix) != REF_CODE_LEN:
        return False
    if not suffix.isalnum():
        return False
    return True


def extract_ref_code(referral_code: str):
    if not referral_code.startswith("ref"):
        return None
    return referral_code[3:]


def give_referral_bonus(
    referral_service: ReferralService,
    subscription_service: SubscriptionService,
    referral: int,
):
    now = datetime.now()
    referrals = referral_service.get(referral_id=referral.id)
    if referrals:
        referral = referrals[0]
        sender_id = referral.user_id
        subscriptions = subscription_service.get(user_id=sender_id)

        activation = now
        expiration = now + timedelta(days=Config.REFERRAL_BONUS)
        renewal = expiration

        if subscriptions:
            subscription = subscriptions[0]
            if subscription.type in [
                UserSubscription.PREMIUM,
                UserSubscription.TRIAL,
            ]:
                activation = subscription.activation
                expiration = subscription.expiration + timedelta(
                    days=Config.REFERRAL_BONUS
                )
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
                user_id=sender_id,
                type=UserSubscription.PREMIUM,
                activation=activation,
                expiration=expiration,
                renewal=renewal,
            )
