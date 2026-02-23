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
from handlers.events.exam import (
    ExamInstructionEvent,
    ExamPaginationEvent,
    ExamFavoriteEvent,
    ExamQuestionEvent,
    ExamQuestionAnswerEvent,
    ExamQuestionFavoriteEvent,
)
from handlers.events.tasks import (
    TaskPaginationEvent,
    TaskAnswerEvent,
    TaskFavoriteEvent,
)
from handlers.events.favorites import FavoritesEvent
from handlers.events.profile import (
    ProfileEvent,
    ProfileSubscriptionEvent,
    PaymentEvent,
    PaymentPreCheckoutEvent,
    PaymentSuccessfulEvent,
    PaymentCancelEvent,
    ProfileSubscriptionTrialEvent,
)
from handlers.events.referral import ReferralEvent, ReferralGetLinkEvent
from handlers.events.faq import FaqEvent
from handlers.events.contact import (
    ContactEvent,
    SupportCancelEvent,
    SupportRequestEvent,
    SupportReplyToMessageEvent,
)


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
    ExamFavoriteEvent(router).register()
    ExamQuestionEvent(router).register()
    ExamQuestionAnswerEvent(router).register()
    ExamQuestionFavoriteEvent(router).register()

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
    PaymentEvent(router).register()
    PaymentPreCheckoutEvent(router).register()
    PaymentSuccessfulEvent(router).register()
    PaymentCancelEvent(router).register()
    ProfileSubscriptionTrialEvent(router).register()
    ReferralEvent(router).register()
    ReferralGetLinkEvent(router).register()

    FaqEvent(router).register()
    ContactEvent(router).register()
    SupportCancelEvent(router).register()
    SupportReplyToMessageEvent(router).register()
    SupportRequestEvent(router).register()

    dp.include_router(router)
