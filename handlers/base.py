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
        self._route = (
            self.__class__.__name__.lower().replace("event", "").replace("command", "")
        )
        self.handler_type: str = "callback_query"

    @abstractmethod
    async def handle(self, update):
        pass

    def register(self):
        if self.handler_type == "callback_query":
            self.router.callback_query.register(self._wrapper, self.get_filter())
        else:
            self.router.message.register(self._wrapper, self.get_filter())

    async def _wrapper(self, update):
        if await self.filter(update):
            await self.handle(update)

    def get_filter(self):
        return None

    async def filter(self, update) -> bool:
        return True
