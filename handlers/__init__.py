from aiogram import Router
from handlers.commands.ping import PingCommand
from handlers.commands.start import StartCommand
from handlers.events.start_menu import StartMenuEvent
from handlers.events.study import StudyThemesEvent, StudyThemeEvent
from handlers.events.theory import TheoryVariantsEvent, TheoryPaginationEvent
from handlers.events.exam import ExamInstructionEvent, ExamPaginationEvent


def register_handlers(dp):
    router = Router()
    PingCommand(router).register()
    StartCommand(router).register()

    StartMenuEvent(router).register()

    StudyThemesEvent(router).register()
    StudyThemeEvent(router).register()

    TheoryVariantsEvent(router).register()
    TheoryPaginationEvent(router).register()

    ExamInstructionEvent(router).register()
    ExamPaginationEvent(router).register()

    dp.include_router(router)
