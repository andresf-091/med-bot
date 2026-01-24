from sqlalchemy.orm import Session
from database.models.theme import Theme


class ThemeService:
    def __init__(self, session: Session):
        self.session = session

    def get(self, **kwargs):
        return self.session.query(Theme).filter_by(**kwargs).order_by(Theme.order).all()

    def create(self, name, order=0):
        theme = Theme(name=name, order=order)
        self.session.add(theme)
        self.session.commit()
        self.session.refresh(theme)
        return theme
