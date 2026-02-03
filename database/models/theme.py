from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from database.models.base import Base


class Theme(Base):
    __tablename__ = "themes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    order = Column(Integer, nullable=False, default=0)

    # Relationships
    theme_items = relationship(
        "ThemeItem",
        back_populates="theme",
        cascade="all, delete-orphan",
        order_by="ThemeItem.order",
    )
    items = association_proxy("theme_items", "item")

    def __repr__(self):
        return f"<Theme(id={self.id}, name='{self.name}', order={self.order})>"
