import sys
import asyncio
from bot.config import Config
from bot.main import main

try:
    Config.validate()
except ValueError as e:
    print(f"Ошибка конфигурации: {e}")
    sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by user")
