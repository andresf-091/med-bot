from sqlalchemy.orm import Session
from database.models.payment import Payment
from database.enum import PaymentStatus


class PaymentService:
    def __init__(self, session: Session):
        self.session = session

    def get(self, **kwargs):
        return self.session.query(Payment).filter_by(**kwargs).all()

    def update(self, id, **kwargs):
        payments = self.get(id=id)
        if payments:
            payment = payments[0]
            for key, value in kwargs.items():
                setattr(payment, key, value)
            self.session.commit()
            self.session.refresh(payment)
            return payment
        return None

    def create(self, transaction_id, user_id, status, amount, **kwargs):
        payment = Payment(
            transaction_id=transaction_id,
            user_id=user_id,
            status=status,
            amount=amount,
            **kwargs,
        )
        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)
        return payment
