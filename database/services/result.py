from sqlalchemy.orm import Session
from database.models.result import Result


class ResultService:
    def __init__(self, session: Session):
        self.session = session

    def get(self, **kwargs):
        return self.session.query(Result).filter_by(**kwargs).all()

    def create(self, user_id, theme_id, difficulty, score, total_questions):
        result = Result(
            user_id=user_id,
            theme_id=theme_id,
            difficulty=difficulty,
            score=score,
            total_questions=total_questions,
        )
        self.session.add(result)
        self.session.commit()
        self.session.refresh(result)
        return result
