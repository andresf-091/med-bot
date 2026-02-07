from sqlalchemy import Column, Integer, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from database.models.base import Base
from database.enum import UserSubscription


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type = Column(Enum(UserSubscription), nullable=False)
    activation = Column(DateTime(timezone=True), nullable=True)
    expiration = Column(DateTime(timezone=True), nullable=True)
    renewal = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="subscriptions")

    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, type={self.type})>"
