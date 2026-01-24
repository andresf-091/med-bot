from sqlalchemy.orm import Session
from database.models.image import Image


class ImageService:
    def __init__(self, session: Session):
        self.session = session

    def get(self, **kwargs):
        return self.session.query(Image).filter_by(**kwargs).order_by(Image.order).all()

    def create(self, item_id, content, caption=None, order=0):
        image = Image(item_id=item_id, content=content, caption=caption, order=order)
        self.session.add(image)
        self.session.commit()
        self.session.refresh(image)
        return image

    def delete(self, image_id):
        image = self.get(id=image_id)
        if not image:
            return False
        self.session.delete(image)
        self.session.commit()
        return True
