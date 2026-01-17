from sqlalchemy.orm import Session
from database.models.user import User
from database.enum import UserRole, UserSubscription, UserLanguage


class UserService:
    def __init__(self, session: Session):
        self.session = session

    def get_by_tg_id(self, tg_id):
        return self.session.query(User).filter(User.tg_id == tg_id).first()

    def get_by_id(self, user_id):
        return self.session.query(User).filter(User.id == user_id).first()

    def create_or_get(
        self,
        tg_id,
        role=UserRole.USER,
        subscription=UserSubscription.FREE,
        language=UserLanguage.RU,
    ):
        user = self.get_by_tg_id(tg_id)
        if user:
            return user
        user = User(
            tg_id=tg_id, role=role, subscription=subscription, language=language
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def update_subscription(self, tg_id, subscription):
        user = self.get_by_tg_id(tg_id)
        if not user:
            return None
        user.subscription = subscription
        self.session.commit()
        self.session.refresh(user)
        return user

    def update_language(self, tg_id, language):
        user = self.get_by_tg_id(tg_id)
        if not user:
            return None
        user.language = language
        self.session.commit()
        self.session.refresh(user)
        return user

    def is_premium(self, tg_id):
        user = self.get_by_tg_id(tg_id)
        if not user:
            return False
        return user.subscription in (UserSubscription.PREMIUM, UserSubscription.TRIAL)
