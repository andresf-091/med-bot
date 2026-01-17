from sqlalchemy.orm import Session
from database.models.theme import Theme


class ThemeService:
    def __init__(self, session: Session):
        self.session = session
    
    def get_all(self):
        return self.session.query(Theme).order_by(Theme.order).all()
    
    def get_by_id(self, theme_id):
        return self.session.query(Theme).filter(Theme.id == theme_id).first()
    
    def get_by_name(self, name):
        return self.session.query(Theme).filter(Theme.name == name).first()
    
    def create(self, name, order=0):
        theme = Theme(name=name, order=order)
        self.session.add(theme)
        self.session.commit()
        self.session.refresh(theme)
        return theme

