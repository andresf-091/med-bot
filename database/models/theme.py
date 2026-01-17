from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from database.models.base import Base


class Theme(Base):
    __tablename__ = "themes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    order = Column(Integer, nullable=False, default=0)

    # Relationships
    items = relationship("Item", back_populates="theme", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Theme(id={self.id}, name='{self.name}', order={self.order})>"
