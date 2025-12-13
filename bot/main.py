import asyncio
from bot.client import bot, dp
from handlers import register_handlers
from log import get_logger


logger = get_logger(__name__)


async def main():
    try:
        bot_info = await bot.get_me()
        logger.info(f"Bot started as {bot_info.username}")

        register_handlers(dp)
        logger.info("Handlers registered")

        await dp.start_polling(bot, skip_updates=True)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
