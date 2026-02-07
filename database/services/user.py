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

    def is_premium(self, id):
        users = self.get(id=id)
        if not users:
            return False

        user = users[0]
        now = datetime.now(timezone.utc)

        active_subscription = (
            self.session.query(Subscription)
            .filter(
                and_(
                    Subscription.user_id == user.id,
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
