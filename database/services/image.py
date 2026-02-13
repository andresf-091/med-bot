from sqlalchemy.orm import Session
from database.models.image import Image


class ImageService:
    def __init__(self, session: Session):
        self.session = session

    def get(self, **kwargs):
        return self.session.query(Image).filter_by(**kwargs).order_by(Image.order).all()

    def update(self, image_id, **kwargs):
        images = self.get(id=image_id)
        if images:
            image = images[0]
            for key, value in kwargs.items():
                setattr(image, key, value)
            self.session.commit()
            self.session.refresh(image)
            return image
        return None
