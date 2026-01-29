from sqlalchemy import Column, Integer, Enum, ForeignKey, UniqueConstraint, BigInteger
from sqlalchemy.orm import relationship
from database.models.base import Base
from database.enum import UserRole, UserSubscription, UserLanguage


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(
        BigInteger, unique=True, nullable=False, index=True
    )  # Telegram user ID
    role = Column(Enum(UserRole), nullable=False, default=UserRole.USER)
    subscription = Column(
        Enum(UserSubscription), nullable=False, default=UserSubscription.FREE
    )
    language = Column(Enum(UserLanguage), nullable=False, default=UserLanguage.RU)

    # Relationships (many-to-many через таблицу связи)
    favorites = relationship(
        "UserFavorite", back_populates="user", cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint("tg_id", name="uq_user_tg_id"),)

    def __repr__(self):
        return f"<User(id={self.id}, tg_id={self.tg_id}, role={self.role}, subscription={self.subscription})>"
