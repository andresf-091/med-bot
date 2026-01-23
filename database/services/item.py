from sqlalchemy.orm import Session
from sqlalchemy import cast, String
from database.models.item import Item
from database.enum import ContentType


class ItemService:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, item_id):
        return self.session.query(Item).filter(Item.id == item_id).first()

    def get_by_theme(self, theme_id, content_type, only_relevant=True):
        query = self.session.query(Item).filter(
            Item.theme_id == theme_id,
            Item.type == content_type,
        )
        if only_relevant:
            query = query.filter(Item.relevant == True)
        return query.order_by(Item.order).all()

    def create(
        self,
        theme_id,
        content_type,
        title=None,
        content=None,
        explanation=None,
        options=None,
        difficulty=1,
        other=None,
        order=0,
        relevant=True,
    ):
        item = Item(
            theme_id=theme_id,
            type=content_type,
            title=title,
            content=content,
            explanation=explanation,
            options=options,
            difficulty=difficulty,
            other=other,
            order=order,
            relevant=relevant,
        )
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def set_relevant(self, item_id, relevant):
        item = self.get_by_id(item_id)
        if not item:
            return None
        item.relevant = relevant
        self.session.commit()
        self.session.refresh(item)
        return item
