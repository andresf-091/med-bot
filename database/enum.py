from enum import Enum as PyEnum


class ContentType(PyEnum):
    THEORY = "theory"
    QUESTION = "question"
    TASK = "task"
    SLIDE = "slide"


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


class PaymentStatus(PyEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
