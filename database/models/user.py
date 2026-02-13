from sqlalchemy import (
    Column,
    Integer,
    Enum,
    ForeignKey,
    UniqueConstraint,
    BigInteger,
    String,
    DateTime,
)
from sqlalchemy.orm import relationship
from database.models.base import Base
from database.enum import UserRole, UserLanguage
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(
        BigInteger, unique=True, nullable=False, index=True
    )
    username = Column(String, unique=True, nullable=True)
    ref_code = Column(String(32), unique=True, nullable=True, index=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.USER)
    language = Column(Enum(UserLanguage), nullable=False, default=UserLanguage.RU)
    created_at = Column(DateTime(timezone=True), nullable=True, default=datetime.now)

    # Relationships
    favorites = relationship(
        "UserFavorite", back_populates="user", cascade="all, delete-orphan"
    )
    subscriptions = relationship(
        "Subscription", back_populates="user", cascade="all, delete-orphan"
    )
    referrals = relationship(
        "Referral",
        foreign_keys="[Referral.user_id]",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    invites = relationship(
        "Referral",
        foreign_keys="[Referral.referral_id]",
        back_populates="referral",
        cascade="all, delete-orphan",
    )
    payments = relationship(
        "Payment", back_populates="user", cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint("tg_id", name="uq_user_tg_id"),)

    def __repr__(self):
        return f"<User(id={self.id}, tg_id={self.tg_id}, role={self.role})>"
