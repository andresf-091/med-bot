from sqlalchemy.orm import Session
from database.models.item import Item
from database.models.image import Image
from database.models.user_favorites import UserFavorite
from database.enum import ContentType


class FavoriteService:
    def __init__(self, session: Session):
        self.session = session

    def get(self, user_id, content_type: ContentType):
        return (
            self.session.query(UserFavorite)
            .filter(
                UserFavorite.user_id == user_id,
                UserFavorite.content_type == content_type,
            )
            .all()
        )

    def add(self, user_id, content_type: ContentType, item_id: int):
        # Проверка существования записи
        existing = (
            self.session.query(UserFavorite)
            .filter(
                UserFavorite.user_id == user_id,
                UserFavorite.item_id == item_id,
                UserFavorite.content_type == content_type,
            )
            .first()
        )
        if existing:
            return True

        # Проверка существования item
        item = self.session.query(Item).filter(Item.id == item_id).first()
        if not item:
            return False

        favorite = UserFavorite(
            user_id=user_id, item_id=item_id, content_type=content_type
        )
        self.session.add(favorite)
        self.session.commit()
        return True

    def remove(self, user_id, content_type: ContentType, item_id: int):
        favorite = (
            self.session.query(UserFavorite)
            .filter(
                UserFavorite.user_id == user_id,
                UserFavorite.item_id == item_id,
                UserFavorite.content_type == content_type,
            )
            .first()
        )
        if not favorite:
            return False

        self.session.delete(favorite)
        self.session.commit()
        return True

    def is_favorite(self, user_id, content_type: ContentType, item_id: int):
        return (
            self.session.query(UserFavorite)
            .filter(
                UserFavorite.user_id == user_id,
                UserFavorite.item_id == item_id,
                UserFavorite.content_type == content_type,
            )
            .first()
            is not None
        )
