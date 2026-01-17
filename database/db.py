"""Настройка подключения к базе данных PostgreSQL"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from bot.config import Config
from database.models.base import Base
from log import get_logger

logger = get_logger(__name__)


class Database:
    """Класс для управления подключением к БД"""

    def __init__(self, database_url: str):
        """
        Args:
            database_url: PostgreSQL connection string
                format: postgresql://user:password@host:port/dbname
        """
        self.engine = create_engine(
            database_url,
            poolclass=NullPool,  # Для простоты, можно использовать pool для production
            echo=False,  # Логировать SQL запросы (включить для отладки)
        )
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def create_tables(self):
        """Создать все таблицы"""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created")

    def drop_tables(self):
        """Удалить все таблицы (осторожно!)"""
        Base.metadata.drop_all(bind=self.engine)
        logger.warning("Database tables dropped")

    def get_session(self) -> Session:
        """Получить новую сессию БД"""
        return self.SessionLocal()

    def close(self):
        """Закрыть подключение"""
        self.engine.dispose()


# Глобальный экземпляр (инициализируется в main)
db: Database = None


def init_db(database_url: str = None):
    """Инициализировать подключение к БД"""
    global db
    if database_url is None:
        # URL из конфига
        database_url = getattr(Config, "DATABASE_URL", None)
        if not database_url:
            raise ValueError("DATABASE_URL не указан в конфигурации")

    db = Database(database_url)
    return db
