import asyncio
from bot.client import client
from handlers import register_handlers
from log import get_logger


logger = get_logger(__name__)


async def main():
    try:
        await client.start()
        logger.info(f"Client started as {(await client.get_me()).username}")

        register_handlers(client)
        logger.info("Handlers registered")

        await client.run_until_disconnected()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
