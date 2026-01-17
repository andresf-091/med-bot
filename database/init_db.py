"""Скрипт для инициализации базы данных"""

import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.config import Config
from database.db import init_db
from log import get_logger

logger = get_logger(__name__)


def main():
    """Создать все таблицы в БД"""
    try:
        # Инициализация подключения
        db = init_db()

        # Создание таблиц
        logger.info("Creating database tables...")
        db.create_tables()

        logger.info("Database initialized successfully!")
        logger.info(
            f"Database URL: {Config.DATABASE_URL.split('@')[1] if '@' in Config.DATABASE_URL else 'hidden'}"
        )

    except Exception as e:
        logger.error(f"Error initializing database: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
