from sqlalchemy.orm import Session
from database.models.referral import Referral
from database.models.user import User


class ReferralService:
    def __init__(self, session: Session):
        self.session = session

    def get(self, **kwargs):
        return self.session.query(Referral).filter_by(**kwargs).all()

    def create(self, user_id: int, referral_id: int):
        referral = Referral(user_id=user_id, referral_id=referral_id)
        self.session.add(referral)
        self.session.commit()
        self.session.refresh(referral)
        return referral

    def count(self, user_id: int, **kwargs):
        return self.session.query(Referral).filter_by(user_id=user_id, **kwargs).count()
