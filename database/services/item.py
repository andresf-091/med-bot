from sqlalchemy.orm import Session
from database.models.item import Item
from database.models.theme_item import ThemeItem
from database.enum import ContentType


class ItemService:
    def __init__(self, session: Session):
        self.session = session

    def get(self, **kwargs):
        theme_id = kwargs.pop("theme_id", None)
        order = kwargs.pop("order", None)
        q = self.session.query(Item).filter_by(**kwargs)
        if theme_id is not None:
            q = q.join(ThemeItem).filter(ThemeItem.theme_id == theme_id)
            if order is not None:
                q = q.filter(ThemeItem.order == order)
            q = q.order_by(ThemeItem.order)
        return q.all()
