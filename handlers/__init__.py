from aiogram import Router
from handlers.commands.ping import PingCommand
from handlers.commands.start import StartCommand
from handlers.events.start_menu import StartMenuEvent, CheckEvent
from handlers.events.study import StudyThemesEvent, StudyThemeEvent
from handlers.events.theory import (
    TheoryVariantsEvent,
    TheoryPaginationEvent,
    TheoryFavoriteEvent,
)
from handlers.events.slides import (
    SlidesListEvent,
    SlidePaginationEvent,
    SlidePaginationDeleteEvent,
    SlideFavoriteEvent,
)
from handlers.events.exam import ExamInstructionEvent, ExamPaginationEvent
from handlers.events.tasks import (
    TaskPaginationEvent,
    TaskAnswerEvent,
    TaskFavoriteEvent,
)
from handlers.events.favorites import FavoritesEvent
from handlers.events.profile import ProfileEvent, ProfileSubscriptionEvent


def register_handlers(dp):
    router = Router()
    PingCommand(router).register()
    StartCommand(router).register()

    StartMenuEvent(router).register()

    StudyThemesEvent(router).register()
    StudyThemeEvent(router).register()

    TheoryVariantsEvent(router).register()
    TheoryPaginationEvent(router).register()
    TheoryFavoriteEvent(router).register()

    ExamInstructionEvent(router).register()
    ExamPaginationEvent(router).register()

    SlidesListEvent(router).register()
    SlidePaginationEvent(router).register()
    SlidePaginationDeleteEvent(router).register()
    SlideFavoriteEvent(router).register()

    TaskPaginationEvent(router).register()
    TaskAnswerEvent(router).register()
    TaskFavoriteEvent(router).register()

    FavoritesEvent(router).register()

    ProfileEvent(router).register()
    ProfileSubscriptionEvent(router).register()

    dp.include_router(router)
