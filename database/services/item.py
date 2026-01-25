from sqlalchemy.orm import Session
from sqlalchemy import cast, String
from database.models.item import Item
from database.enum import ContentType


class ItemService:
    def __init__(self, session: Session):
        self.session = session

    def get(self, **kwargs):
        return self.session.query(Item).filter_by(**kwargs).order_by(Item.order).all()
