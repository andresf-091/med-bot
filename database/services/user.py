import uuid
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timezone
from database.models.user import User
from database.models.subscription import Subscription
from database.enum import UserRole, UserSubscription, UserLanguage


class UserService:
    def __init__(self, session: Session):
        self.session = session

    def get(self, **kwargs):
        return self.session.query(User).filter_by(**kwargs).all()

    def ensure_ref_code(self, user):
        if user.ref_code:
            return user.ref_code
        code = uuid.uuid4().hex
        self.update(id=user.id, ref_code=code)
        return code

    def update(self, id, **kwargs):
        users = self.get(id=id)
        if users:
            user = users[0]
            for key, value in kwargs.items():
                setattr(user, key, value)
            self.session.commit()
            self.session.refresh(user)
            return user
        return None

    def create(self, tg_id, **kwargs):
        user = User(tg_id=tg_id, **kwargs)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def expire_user_subscription(self, user_id):
        now = datetime.now(timezone.utc)
        expired_subscriptions = (
            self.session.query(Subscription)
            .filter(
                and_(
                    Subscription.user_id == user_id,
                    Subscription.expiration.isnot(None),
                    Subscription.expiration <= now,
                    Subscription.type != UserSubscription.EXPIRED,
                )
            )
            .all()
        )
        for subscription in expired_subscriptions:
            subscription.type = UserSubscription.EXPIRED
        if expired_subscriptions:
            self.session.commit()
        return len(expired_subscriptions)

    def is_premium(self, id):
        users = self.get(id=id)
        if not users:
            return False

        user = users[0]
        self.expire_user_subscription(user.id)
        now = datetime.now(timezone.utc)

        active_subscription = (
            self.session.query(Subscription)
            .filter(
                and_(
                    Subscription.user_id == user.id,
                    or_(
                        Subscription.activation.is_(None),
                        Subscription.activation <= now,
                    ),
                    or_(
                        Subscription.expiration.is_(None), Subscription.expiration > now
                    ),
                )
            )
            .order_by(Subscription.activation.desc().nullslast())
            .first()
        )

        if active_subscription:
            return active_subscription.type in (
                UserSubscription.PREMIUM,
                UserSubscription.TRIAL,
            )
        return False
