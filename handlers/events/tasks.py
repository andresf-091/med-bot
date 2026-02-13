from aiogram import F
from aiogram.types import CallbackQuery, InputMediaPhoto
from handlers.base import BaseHandler
from utils.keyboards import inline_kb
from utils.subscription import if_not_premium
from services.text import text_service
from services.image_storage import LocalImageStorage
from database import (
    UserService,
    db,
    ItemService,
    ThemeService,
    ContentType,
    ImageService,
    FavoriteService,
)
from log import get_logger

logger = get_logger(__name__)


class TaskPaginationEvent(BaseHandler):

    def get_filter(self):
        cond_1 = F.data.startswith("studytheme_") & F.data.endswith("_3_0")
        cond_2 = F.data.startswith("taskpagination_")
        cond_3 = F.data.endswith("_1_0_0") | F.data.endswith("_2_0_0")
        cond_4 = F.data.endswith("_1_0_1") | F.data.endswith("_2_0_1")
        cond_5 = F.data.func(
            lambda d: d.startswith("taskpagination_") and len(d.split("_")) == 4
        )
        return cond_1 | (cond_2 & (cond_3 | cond_4 | cond_5))

    async def handle(self, callback: CallbackQuery):
        parts = callback.data.split("_")
        if len(parts) > 5 and (
            callback.data.endswith("_1_0_1") or callback.data.endswith("_2_0_1")
        ):
            await callback.answer("Это первая/последняя страница")
            return

        user = callback.from_user
        username = user.username or user.first_name
        theme_id = int(parts[1])
        from_fav = (
            int(parts[3])
            if len(parts) >= 6
            else (1 if len(parts) == 4 else 0)
        )

        if callback.data.startswith("studytheme_"):
            page = 0
        elif len(parts) == 4:
            page = int(parts[2])
        else:
            current_page = int(parts[2])
            if callback.data.endswith("_2_0_0"):
                page = max(0, current_page - 1)
            else:
                page = current_page + 1

        with db.session() as session:
            user_service = UserService(session)
            user_db = user_service.get(tg_id=user.id)[0]
            is_premium = user_service.is_premium(user_db.id)

            if is_premium:
                item_service = ItemService(session)
                tasks = item_service.get(theme_id=theme_id, type=ContentType.TASK)
                total_pages = len(tasks)
                page = min(total_pages - 1, page)

                if tasks:
                    favorite_service = FavoriteService(session)
                    is_favorite = favorite_service.is_favorite(
                        user_id=user_db.id,
                        item_id=tasks[page].id,
                        content_type=ContentType.TASK,
                    )

        if not is_premium:
            await if_not_premium(callback, username, self.DEFAULT_SEND_PARAMS)
            return
        if not tasks:
            await callback.answer("Задач по этому теме не найдено")
            return

        task = tasks[page]

        logger.info(
            f"Task pagination: {page + 1} / {total_pages} for theme {theme_id}: {username}"
        )

        buttons = text_service.get("events.task_pagination.buttons")
        is_end = (page + 1) == total_pages
        is_start = page == 0
        prefix = f"taskpagination_{theme_id}_{page}_{from_fav}"
        button_kwargs_map = {}
        if from_fav:
            button_kwargs_map[(3, 0)] = {"callback_data": "start_1_1"}
        keyboard = inline_kb(
            buttons,
            prefix,
            variants_map={
                (0, 0): 0,
                (1, 0): int(is_end),
                (2, 0): int(is_start),
                (2, 1): int(is_favorite),
                (3, 0): from_fav,
            },
            include_variant_in_callback=True,
            button_kwargs_map=button_kwargs_map or None,
        )
        text = text_service.get(
            "events.task_pagination.text",
            page=page + 1,
            total_pages=total_pages,
            title=(task.title + "\n\n") if not task.content else "",
            task=task.content if task.content else "",
            answer="",
        )

        await callback.answer()
        await callback.message.edit_text(
            text,
            **self.DEFAULT_SEND_PARAMS,
            reply_markup=keyboard,
        )


class TaskAnswerEvent(BaseHandler):
    def get_filter(self):
        cond_1 = F.data.startswith("taskpagination_")
        cond_2 = F.data.endswith("_0_0_0")
        cond_3 = F.data.endswith("_0_0_1")
        return cond_1 & (cond_2 | cond_3)

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name
        parts = callback.data.split("_")
        theme_id = int(parts[1])
        page = int(parts[2])
        from_fav = int(parts[3]) if len(parts) >= 6 else 0

        is_show = callback.data.endswith("_0_0_0")

        with db.session() as session:
            user_service = UserService(session)
            user_db = user_service.get(tg_id=user.id)[0]
            is_premium = user_service.is_premium(user_db.id)

            if is_premium:
                item_service = ItemService(session)
                tasks = item_service.get(theme_id=theme_id, type=ContentType.TASK)
                if tasks:
                    favorite_service = FavoriteService(session)
                    is_favorite = favorite_service.is_favorite(
                        user_id=user_db.id,
                        item_id=tasks[page].id,
                        content_type=ContentType.TASK,
                    )

        if not is_premium:
            await if_not_premium(callback, username, self.DEFAULT_SEND_PARAMS)
            return
        if not tasks:
            await callback.answer("Задач по этому теме не найдено")
            return

        total_pages = len(tasks)
        task = tasks[page]

        logger.debug(
            f"Task show/hide answer: {is_show} for theme {theme_id} task {page + 1}: {username}"
        )

        if is_show:
            answer = task.explanation
        else:
            answer = ""

        buttons = text_service.get("events.task_pagination.buttons")
        is_end = (page + 1) == total_pages
        is_start = page == 0
        prefix = f"taskpagination_{theme_id}_{page}_{from_fav}"
        button_kwargs_map = {}
        if from_fav:
            button_kwargs_map[(3, 0)] = {"callback_data": "start_1_1"}
        keyboard = inline_kb(
            buttons,
            prefix,
            variants_map={
                (0, 0): int(is_show),
                (1, 0): int(is_end),
                (2, 0): int(is_start),
                (2, 1): int(is_favorite),
                (3, 0): from_fav,
            },
            include_variant_in_callback=True,
            button_kwargs_map=button_kwargs_map or None,
        )
        text = text_service.get(
            "events.task_pagination.text",
            page=page + 1,
            total_pages=total_pages,
            title=(task.title + "\n\n") if not task.content else "",
            task=task.content if task.content else "",
            answer=answer,
        )

        await callback.answer()
        await callback.message.edit_text(
            text,
            **self.DEFAULT_SEND_PARAMS,
            reply_markup=keyboard,
        )


class TaskFavoriteEvent(BaseHandler):
    def get_filter(self):
        cond_1 = F.data.startswith("taskpagination_")
        cond_2 = F.data.endswith("_2_1_0") | F.data.endswith("_2_1_1")
        return cond_1 & cond_2

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name
        parts = callback.data.split("_")
        theme_id = int(parts[1])
        page = int(parts[2])
        from_fav = int(parts[3]) if len(parts) >= 7 else 0

        with db.session() as session:
            user_service = UserService(session)
            user_db = user_service.get(tg_id=user.id)[0]
            is_premium = user_service.is_premium(user_db.id)

            if is_premium:
                item_service = ItemService(session)
                tasks = item_service.get(theme_id=theme_id, type=ContentType.TASK)
                if tasks:
                    favorite_service = FavoriteService(session)
                    is_favorite = favorite_service.toggle(
                        user_id=user_db.id,
                        item_id=tasks[page].id,
                        content_type=ContentType.TASK,
                    )

        if not is_premium:
            await if_not_premium(callback, username, self.DEFAULT_SEND_PARAMS)
            return
        if not tasks:
            await callback.answer("Задач по этой теме не найдено")
            return

        total_pages = len(tasks)

        logger.info(
            f"Task favorite toggled: {is_favorite} for task {page + 1}: {username}"
        )

        keyboard = callback.message.reply_markup.inline_keyboard
        is_show = keyboard[0][0].callback_data.endswith("_0_0_1")

        buttons = text_service.get("events.task_pagination.buttons")
        is_end = (page + 1) == total_pages
        is_start = page == 0
        prefix = f"taskpagination_{theme_id}_{page}_{from_fav}"
        button_kwargs_map = {}
        if from_fav:
            button_kwargs_map[(3, 0)] = {"callback_data": "start_1_1"}
        keyboard = inline_kb(
            buttons,
            prefix,
            variants_map={
                (0, 0): int(is_show),
                (1, 0): int(is_end),
                (2, 0): int(is_start),
                (2, 1): int(is_favorite),
                (3, 0): from_fav,
            },
            include_variant_in_callback=True,
            button_kwargs_map=button_kwargs_map or None,
        )

        await callback.answer()
        await callback.message.edit_reply_markup(reply_markup=keyboard)
        if is_favorite:
            await callback.answer("Задача добавлена в избранное")
        else:
            await callback.answer("Задача удалена из избранного")
