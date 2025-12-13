from handlers.base import BaseHandler
from telethon import events
from log import get_logger

logger = get_logger(__name__)

class StartCommand(BaseHandler):
    """Обработчик команды /ping"""
    
    def get_event_type(self):
        return events.NewMessage(pattern=r'^/start$')
    
    async def handle(self, event):
        sender = await event.get_sender()
        logger.info(f"{sender.username or sender.first_name} started bot")
        await event.reply(f"Hello, {sender.username or sender.first_name}")