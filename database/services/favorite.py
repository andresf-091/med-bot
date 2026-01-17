from sqlalchemy.orm import Session
from database.models.item import Item
from database.models.user_favorites import UserFavoriteTheory, UserFavoriteExam, UserFavoriteTask
from database.enum import ContentType


class FavoriteService:
    def __init__(self, session: Session):
        self.session = session
    
    def get_favorite_theory(self, user_id):
        return self.session.query(Item).join(
            UserFavoriteTheory, Item.id == UserFavoriteTheory.item_id
        ).filter(UserFavoriteTheory.user_id == user_id).order_by(Item.order).all()
    
    def get_favorite_exam(self, user_id):
        return self.session.query(Item).join(
            UserFavoriteExam, Item.id == UserFavoriteExam.item_id
        ).filter(UserFavoriteExam.user_id == user_id).order_by(Item.order).all()
    
    def get_favorite_task(self, user_id):
        return self.session.query(Item).join(
            UserFavoriteTask, Item.id == UserFavoriteTask.item_id
        ).filter(UserFavoriteTask.user_id == user_id).order_by(Item.order).all()
    
    def add_favorite_theory(self, user_id, item_id):
        item = self.session.query(Item).filter(
            Item.id == item_id, Item.type == ContentType.THEORY
        ).first()
        if not item:
            return False
        existing = self.session.query(UserFavoriteTheory).filter(
            UserFavoriteTheory.user_id == user_id,
            UserFavoriteTheory.item_id == item_id,
        ).first()
        if existing:
            return True
        favorite = UserFavoriteTheory(user_id=user_id, item_id=item_id)
        self.session.add(favorite)
        self.session.commit()
        return True
    
    def add_favorite_exam(self, user_id, item_id):
        item = self.session.query(Item).filter(
            Item.id == item_id, Item.type == ContentType.QUESTION
        ).first()
        if not item:
            return False
        existing = self.session.query(UserFavoriteExam).filter(
            UserFavoriteExam.user_id == user_id,
            UserFavoriteExam.item_id == item_id,
        ).first()
        if existing:
            return True
        favorite = UserFavoriteExam(user_id=user_id, item_id=item_id)
        self.session.add(favorite)
        self.session.commit()
        return True
    
    def add_favorite_task(self, user_id, item_id):
        item = self.session.query(Item).filter(
            Item.id == item_id, Item.type == ContentType.TASK
        ).first()
        if not item:
            return False
        existing = self.session.query(UserFavoriteTask).filter(
            UserFavoriteTask.user_id == user_id,
            UserFavoriteTask.item_id == item_id,
        ).first()
        if existing:
            return True
        favorite = UserFavoriteTask(user_id=user_id, item_id=item_id)
        self.session.add(favorite)
        self.session.commit()
        return True
    
    def remove_favorite_theory(self, user_id, item_id):
        favorite = self.session.query(UserFavoriteTheory).filter(
            UserFavoriteTheory.user_id == user_id,
            UserFavoriteTheory.item_id == item_id,
        ).first()
        if not favorite:
            return False
        self.session.delete(favorite)
        self.session.commit()
        return True
    
    def remove_favorite_exam(self, user_id, item_id):
        favorite = self.session.query(UserFavoriteExam).filter(
            UserFavoriteExam.user_id == user_id,
            UserFavoriteExam.item_id == item_id,
        ).first()
        if not favorite:
            return False
        self.session.delete(favorite)
        self.session.commit()
        return True
    
    def remove_favorite_task(self, user_id, item_id):
        favorite = self.session.query(UserFavoriteTask).filter(
            UserFavoriteTask.user_id == user_id,
            UserFavoriteTask.item_id == item_id,
        ).first()
        if not favorite:
            return False
        self.session.delete(favorite)
        self.session.commit()
        return True
    
    def is_favorite_theory(self, user_id, item_id):
        return self.session.query(UserFavoriteTheory).filter(
            UserFavoriteTheory.user_id == user_id,
            UserFavoriteTheory.item_id == item_id,
        ).first() is not None
    
    def is_favorite_exam(self, user_id, item_id):
        return self.session.query(UserFavoriteExam).filter(
            UserFavoriteExam.user_id == user_id,
            UserFavoriteExam.item_id == item_id,
        ).first() is not None
    
    def is_favorite_task(self, user_id, item_id):
        return self.session.query(UserFavoriteTask).filter(
            UserFavoriteTask.user_id == user_id,
            UserFavoriteTask.item_id == item_id,
        ).first() is not None

