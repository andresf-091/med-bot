import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from alembic.config import Config as AlembicConfig
from alembic import command
from bot.config import Config
from log import get_logger

logger = get_logger(__name__)


def main():
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"Ошибка конфигурации: {e}")
        sys.exit(1)

    try:
        logger.info("Applying database migrations...")
        alembic_cfg = AlembicConfig("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations applied successfully!")
        logger.info(
            f"Database URL: {Config.DATABASE_URL.split('@')[1] if '@' in Config.DATABASE_URL else 'hidden'}"
        )
    except Exception as e:
        logger.error(f"Error applying migrations: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
