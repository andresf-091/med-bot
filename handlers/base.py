from abc import ABC, abstractmethod
from aiogram import Router
from aiogram.enums import ParseMode


class BaseHandler(ABC):
    DEFAULT_SEND_PARAMS: dict = {
        "protect_content": True,
        "parse_mode": ParseMode.MARKDOWN_V2,
        "link_preview": False,
    }

    def __init__(self, router: Router):
        self.router = router
        self._route = self.__class__.__name__.lower()

    @abstractmethod
    async def handle(self, message):
        pass

    def register(self):
        self.router.message.register(self._wrapper, self.get_filter())

    async def _wrapper(self, message):
        if await self.filter(message):
            await self.handle(message)

    def get_filter(self):
        return None

    async def filter(self, message) -> bool:
        return True
