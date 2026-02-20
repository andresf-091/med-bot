from abc import ABC, abstractmethod
from aiogram import Router
from aiogram.enums import ParseMode, ContentType


class BaseHandler(ABC):
    DEFAULT_SEND_PARAMS: dict = {
        "protect_content": True,
        "parse_mode": ParseMode.MARKDOWN,
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
        if self.handler_type == "pre_checkout_query":
            filter_func = self.get_filter()
            if filter_func:
                self.router.pre_checkout_query.register(self._wrapper, filter_func)
            else:
                self.router.pre_checkout_query.register(self._wrapper)
        elif self.handler_type == "callback_query":
            filter_func = self.get_filter()
            if filter_func:
                self.router.callback_query.register(self._wrapper, filter_func)
            else:
                self.router.callback_query.register(self._wrapper)
        elif self.handler_type == "successful_payment":
            from aiogram import F

            filter_func = self.get_filter()
            filters = [F.content_type == ContentType.SUCCESSFUL_PAYMENT]
            if filter_func:
                filters.append(filter_func)
            self.router.message.register(self._wrapper, *filters)
        else:
            filter_func = self.get_filter()
            if filter_func:
                self.router.message.register(self._wrapper, filter_func)
            else:
                self.router.message.register(self._wrapper)

    async def _wrapper(self, update):
        if await self.filter(update):
            await self.handle(update)

    def get_filter(self):
        return None

    async def filter(self, update) -> bool:
        return True
