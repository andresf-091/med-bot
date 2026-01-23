import sys
import asyncio
from bot.config import Config
from bot.main import main
from database import db

try:
    Config.validate()
except ValueError as e:
    print(f"Ошибка конфигурации: {e}")
    sys.exit(1)

db.create_tables()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by user")
    finally:
        db.close()
