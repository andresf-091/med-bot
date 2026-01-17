from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database.models.base import Base


class UserFavoriteTheory(Base):
    """Таблица связи пользователей и избранной теории"""
    __tablename__ = "user_favorite_theory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True)

    user = relationship("User", back_populates="favorite_theory")
    item = relationship("Item", back_populates="favorited_by_theory")

    __table_args__ = (
        UniqueConstraint('user_id', 'item_id', name='uq_user_favorite_theory'),
    )


class UserFavoriteExam(Base):
    """Таблица связи пользователей и избранных вопросов теста"""
    __tablename__ = "user_favorite_exam"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True)

    user = relationship("User", back_populates="favorite_exam")
    item = relationship("Item", back_populates="favorited_by_exam")

    __table_args__ = (
        UniqueConstraint('user_id', 'item_id', name='uq_user_favorite_exam'),
    )


class UserFavoriteTask(Base):
    """Таблица связи пользователей и избранных задач"""
    __tablename__ = "user_favorite_task"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True)

    user = relationship("User", back_populates="favorite_task")
    item = relationship("Item", back_populates="favorited_by_task")

    __table_args__ = (
        UniqueConstraint('user_id', 'item_id', name='uq_user_favorite_task'),
    )

