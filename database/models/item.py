from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    JSON,
    Enum,
    CheckConstraint,
    Boolean,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from database.models.base import Base
from database.enum import ContentType


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(Enum(ContentType), nullable=False, index=True)
    title = Column(String(500), nullable=True)
    content = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)
    options = Column(JSON, nullable=True)  # List[str] для вопросов теста
    difficulty = Column(Integer, nullable=True)  # 1-5
    is_full = Column(Boolean, nullable=False, default=True)
    other = Column(JSON, nullable=True)  # Дополнительные данные в JSON
    relevant = Column(Boolean, nullable=False, default=True)

    # Relationships
    theme_items = relationship(
        "ThemeItem", back_populates="item", cascade="all, delete-orphan"
    )
    themes = association_proxy("theme_items", "theme")
    images = relationship(
        "Image",
        back_populates="item",
        cascade="all, delete-orphan",
        order_by="Image.order",
    )

    # Many-to-many через таблицу связи
    favorited_by = relationship(
        "UserFavorite", back_populates="item", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "difficulty >= 1 AND difficulty <= 5", name="ck_item_difficulty_range"
        ),
    )

    def __repr__(self):
        return f"<Item(id={self.id}, type={self.type})>"
