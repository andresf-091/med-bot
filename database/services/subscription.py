from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timezone
from database.models.subscription import Subscription
from database.enum import UserSubscription


class SubscriptionService:
    def __init__(self, session: Session):
        self.session = session

    def get(self, **kwargs):
        return self.session.query(Subscription).filter_by(**kwargs).all()

    def update(self, id, **kwargs):
        subscriptions = self.get(id=id)
        if subscriptions:
            subscription = subscriptions[0]
            for key, value in kwargs.items():
                setattr(subscription, key, value)
            self.session.commit()
            self.session.refresh(subscription)
            return subscription
        return None

    def create(self, user_id, type, **kwargs):
        subscription = Subscription(user_id=user_id, type=type, **kwargs)
        self.session.add(subscription)
        self.session.commit()
        self.session.refresh(subscription)
        return subscription
