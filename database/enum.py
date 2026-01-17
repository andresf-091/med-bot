from enum import Enum as PyEnum


class ContentType(PyEnum):
    THEORY = "theory"
    QUESTION = "question"
    TASK = "task"


class UserRole(PyEnum):
    USER = "user"
    ADMIN = "admin"


class UserSubscription(PyEnum):
    PREMIUM = "premium"
    FREE = "free"
    TRIAL = "trial"
    EXPIRED = "expired"


class UserLanguage(PyEnum):
    RU = "ru"
    EN = "en"
