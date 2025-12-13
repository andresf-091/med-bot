from handlers.commands.ping import PingCommand
from handlers.commands.start import StartCommand


def register_handlers(client):
    PingCommand(client).register()
    StartCommand(client).register()
