from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from database.models.base import Base


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String(500), nullable=False)  # URL или путь к изображению
    file_id = Column(String(500), nullable=True)
    caption = Column(Text, nullable=True)
    item_id = Column(
        Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True
    )
    order = Column(Integer, nullable=False, default=0)

    # Relationships
    item = relationship("Item", back_populates="images")

    def __repr__(self):
        return f"<Image(id={self.id}, item_id={self.item_id}, order={self.order})>"
