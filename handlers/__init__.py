from aiogram import Router
from handlers.commands.ping import PingCommand
from handlers.commands.start import StartCommand
from handlers.events.medication_list import (
    MedicationListStartEvent,
    MedicationListBackEvent,
    MedicationListSliderEvent,
    MedicationListSaveEvent,
    MedicationListUnsaveEvent,
)


def register_handlers(dp):
    router = Router()
    PingCommand(router).register()
    StartCommand(router).register()

    MedicationListStartEvent(router).register()

    MedicationListSliderEvent(router).register()
    MedicationListSaveEvent(router).register()
    MedicationListUnsaveEvent(router).register()

    MedicationListBackEvent(router).register()

    dp.include_router(router)
