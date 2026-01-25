from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, Enum
from sqlalchemy.orm import relationship
from database.models.base import Base
from database.enum import ContentType


class UserFavorite(Base):
    __tablename__ = "user_favorites"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    item_id = Column(
        Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True
    )
    content_type = Column(Enum(ContentType), nullable=False, index=True)

    user = relationship("User", back_populates="favorites")
    item = relationship("Item", back_populates="favorited_by")

    __table_args__ = (
        UniqueConstraint("user_id", "item_id", "content_type", name="uq_user_favorite"),
    )
