from abc import ABC, abstractmethod
from telethon import events
from typing import Optional

class BaseHandler(ABC):
   
    def __init__(self, client):
        self.client = client
    
    @abstractmethod
    async def handle(self, event):
        pass
    
    def register(self):
        @self.client.on(self.get_event_type())
        async def wrapper(event):
            if await self.filter(event):
                await self.handle(event)
        return wrapper
    
    def get_event_type(self):
        return events.NewMessage
    
    async def filter(self, event) -> bool:
        return True