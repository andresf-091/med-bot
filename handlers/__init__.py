from aiogram import Router
from handlers.commands.ping import PingCommand
from handlers.commands.start import StartCommand


def register_handlers(dp):
    router = Router()
    PingCommand(router).register()
    StartCommand(router).register()
    dp.include_router(router)
