from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    UniqueConstraint,
    JSON,
    Enum,
    CheckConstraint,
    Boolean,
)
from sqlalchemy.orm import relationship
from database.models.base import Base
from database.enum import ContentType


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(Enum(ContentType), nullable=False, index=True)
    theme_id = Column(
        Integer, ForeignKey("themes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title = Column(String(500), nullable=True)
    content = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)
    options = Column(JSON, nullable=True)  # List[str] для вопросов теста
    difficulty = Column(Integer, nullable=True)  # 1-5
    other = Column(JSON, nullable=True)  # Дополнительные данные в JSON
    order = Column(Integer, nullable=False, default=0)
    relevant = Column(Boolean, nullable=False, default=True)

    # Relationships
    theme = relationship("Theme", back_populates="items")
    images = relationship(
        "Image",
        back_populates="item",
        cascade="all, delete-orphan",
        order_by="Image.order",
    )

    # Many-to-many через таблицы связи
    favorited_by_theory = relationship(
        "UserFavoriteTheory", back_populates="item", cascade="all, delete-orphan"
    )
    favorited_by_exam = relationship(
        "UserFavoriteExam", back_populates="item", cascade="all, delete-orphan"
    )
    favorited_by_task = relationship(
        "UserFavoriteTask", back_populates="item", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("theme_id", "order", "type", name="uq_item_theme_order_type"),
        CheckConstraint(
            "difficulty >= 1 AND difficulty <= 5", name="ck_item_difficulty_range"
        ),
    )

    def __repr__(self):
        return f"<Item(id={self.id}, type={self.type}, theme_id={self.theme_id}, order={self.order})>"
