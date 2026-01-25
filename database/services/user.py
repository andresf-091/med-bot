from sqlalchemy.orm import Session
from database.models.user import User
from database.enum import UserRole, UserSubscription, UserLanguage


class UserService:
    def __init__(self, session: Session):
        self.session = session

    def get(self, **kwargs):
        return self.session.query(User).filter_by(**kwargs).all()

    def update(self, tg_id, **kwargs):
        user = self.get(tg_id=tg_id)
        if not user:
            return None
        for key, value in kwargs.items():
            setattr(user, key, value)
        self.session.commit()
        self.session.refresh(user)
        return user

    def create(self, tg_id, **kwargs):
        user = User(tg_id=tg_id, **kwargs)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def is_premium(self, tg_id):
        user = self.get(tg_id=tg_id)
        if not user:
            return False
        return user.subscription in (UserSubscription.PREMIUM, UserSubscription.TRIAL)
