from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database.models.base import Base


class ThemeItem(Base):
    __tablename__ = "theme_items"

    theme_id = Column(
        Integer, ForeignKey("themes.id", ondelete="CASCADE"), primary_key=True
    )
    item_id = Column(
        Integer, ForeignKey("items.id", ondelete="CASCADE"), primary_key=True
    )
    order = Column(Integer, nullable=False, default=0)

    theme = relationship("Theme", back_populates="theme_items")
    item = relationship("Item", back_populates="theme_items")
