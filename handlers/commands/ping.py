from telethon import events

from bot.client import client
from handlers.base import BaseHandler
from log import get_logger

logger = get_logger(__name__)

class PingCommand(BaseHandler):
    
    def get_event_type(self):
        return events.NewMessage(pattern=r'^/ping$')

    async def handle(self, event):
        sender = await event.get_sender()
        logger.info(f"Ping received from {sender.username or sender.id}")
        await event.reply("pong")
