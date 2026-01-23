from aiogram import F
from aiogram.types import CallbackQuery
from handlers.base import BaseHandler
from services.context import context_service
from services.text import text_service
from database import db, ItemService, ContentType
from utils.keyboards import inline_kb
from utils.paginator import split_content
from log import get_logger

logger = get_logger(__name__)


class TheoryVariantsEvent(BaseHandler):

    def get_filter(self):
        return F.data.in_(["studytheme_0_0", "theorypagination_2_0"])

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name
        theme = context_service.get(user.id, "study_theme")

        logger.info(f"Theory variants for theme {theme}: {username}")

        buttons = text_service.get("events.theory_variants.buttons")
        keyboard = inline_kb(buttons, self._route)
        text = text_service.get("events.theory_variants.text")

        await callback.answer()
        await callback.message.edit_text(
            text,
            **self.DEFAULT_SEND_PARAMS,
            reply_markup=keyboard,
        )


class TheoryPaginationEvent(BaseHandler):

    def get_filter(self):
        return (
            F.data.startswith("theoryvariants_")
            | F.data.startswith("theorypagination_0_")
            | F.data.startswith("theorypagination_1_0")
        )

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name
        theme_id = context_service.get(user.id, "study_theme")

        current_page = context_service.get(user.id, "theory_page", None)

        if callback.data.startswith("theoryvariants_"):
            page = 0
            context_service.set(user.id, "theory_page", None)
        elif callback.data.startswith("theorypagination_1_0"):
            page = max(0, current_page - 1)
        else:
            page = current_page + 1

        pages = context_service.get(user.id, "theory_pages")

        if pages is None:
            with db.session() as session:
                item_service = ItemService(session)
                items = item_service.get_by_theme(theme_id, ContentType.THEORY)
                if not items:
                    await callback.answer("Теория не найдена")
                    return
                content = items[0].content
            pages = split_content(content)
            context_service.set(user.id, "theory_pages", pages)

        total_pages = len(pages)
        page = min(page, total_pages - 1)

        context_service.set(user.id, "theory_page", page)

        logger.info(
            f"Theory pagination page {page + 1}/{total_pages} for theme {theme_id}: {username}"
        )

        theory_text = pages[page]
        text = text_service.get(
            "events.theory_pagination.text",
            page=page + 1,
            total_pages=total_pages,
            theory=theory_text,
        )

        buttons = text_service.get("events.theory_pagination.buttons", copy_obj=True)
        if (page + 1) == total_pages:
            buttons[0][0] = "✅ Конец"
        elif page == 0:
            buttons[1][0] = "🔄 Назад не получится"
        keyboard = inline_kb(buttons, self._route)

        if (page != current_page) or (current_page is None):
            await callback.answer()
            await callback.message.edit_text(
                text,
                **self.DEFAULT_SEND_PARAMS,
                reply_markup=keyboard,
            )
        else:
            await callback.answer("Это первая/последняя страница")
