from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.orm import relationship
from database.models.base import Base
from datetime import datetime


class Referral(Base):
    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    referral_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    created_at = Column(DateTime(timezone=True), nullable=True, default=datetime.now)

    user = relationship("User", foreign_keys=[user_id], back_populates="referrals")
    referral = relationship(
        "User", foreign_keys=[referral_id], back_populates="invites"
    )

    __table_args__ = (
        UniqueConstraint("user_id", "referral_id", name="uq_user_referral"),
    )

    def __repr__(self):
        return f"<Referral(id={self.id}, user_id={self.user_id}, referral_id={self.referral_id}, created_at={self.created_at})>"
