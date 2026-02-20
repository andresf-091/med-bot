from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database.models.base import Base


class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    theme_id = Column(
        Integer,
        ForeignKey("themes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    difficulty = Column(Integer, nullable=False)
    score = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)

    user = relationship("User")
    theme = relationship("Theme")

    def __repr__(self):
        return (
            f"<Result(id={self.id}, user_id={self.user_id}, "
            f"theme_id={self.theme_id}, score={self.score})>"
        )
