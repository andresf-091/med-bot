from aiogram import F
from aiogram.types import CallbackQuery
from handlers.base import BaseHandler
from utils.subscription import if_not_premium
from utils.keyboards import inline_kb
from services.text import text_service
from database import (
    db,
    ItemService,
    ContentType,
    UserService,
    FavoriteService,
)
from log import get_logger

logger = get_logger(__name__)


class FavoritesEvent(BaseHandler):

    def get_filter(self):
        return F.data == "start_1_1"

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name

        items_data = []
        favorites = []

        with db.session() as session:
            user_service = UserService(session)
            user_db = user_service.get(tg_id=user.id)[0]
            is_premium = user_service.is_premium(user_db.id)

            if is_premium:
                favorite_service = FavoriteService(session)
                favorites = favorite_service.get(user_db.id)

                if favorites:
                    item_service = ItemService(session)

                    for favorite in favorites:
                        item = item_service.get(id=favorite.item_id)[0]
                        theme_id = (
                            item.theme_items[0].theme_id if item.theme_items else None
                        )
                        order = item.theme_items[0].order if item.theme_items else None
                        task_page = None
                        if item.type == ContentType.TASK and theme_id is not None:
                            tasks = item_service.get(
                                theme_id=theme_id, type=ContentType.TASK
                            )
                            for idx, t in enumerate(tasks):
                                if t.id == item.id:
                                    task_page = idx
                                    break
                        items_data.append(
                            {
                                "item_id": item.id,
                                "type": item.type,
                                "title": item.title,
                                "is_full": item.is_full,
                                "theme_id": theme_id,
                                "order": order,
                                "task_page": task_page,
                            }
                        )

        if not is_premium:
            await if_not_premium(callback, username, self.DEFAULT_SEND_PARAMS)
            return
        if not favorites:
            await callback.answer("Избранные не найдены")
            return

        logger.debug(f"Favorites: {username}")

        section_headers = {
            ContentType.TASK: "📜 Задачи 📜",
            ContentType.THEORY: "📚 Теория 📚",
            ContentType.SLIDE: "🔬 Препараты 🔬",
            ContentType.QUESTION: "❔ Вопросы тестов ❔",
        }
        section_order = (
            ContentType.TASK,
            ContentType.THEORY,
            ContentType.SLIDE,
            ContentType.QUESTION,
        )

        by_type = {}
        for data in items_data:
            t = data["type"]
            by_type.setdefault(t, []).append(data)

        text = text_service.get("events.favorites.text")
        buttons = text_service.get("events.favorites.buttons", copy_obj=True)
        base_len = len(buttons)
        button_kwargs_map = {}
        row = base_len

        for content_type in section_order:
            block = by_type.get(content_type)
            if not block:
                continue
            buttons.append([section_headers[content_type]])
            row += 1
            for data in block:
                buttons.append([data["title"]])
                if content_type == ContentType.THEORY and data["theme_id"] is not None:
                    button_kwargs_map[(row, 0)] = {
                        "callback_data": f"theorypagination_{data['theme_id']}_0_{int(data['is_full'])}_1_0_0"
                    }
                elif (
                    content_type == ContentType.SLIDE
                    and data["theme_id"] is not None
                    and data.get("order") is not None
                ):
                    button_kwargs_map[(row, 0)] = {
                        "callback_data": f"slideslist_{data['theme_id']}_{data['order'] + 1}_1"
                    }
                elif (
                    content_type == ContentType.TASK
                    and data["theme_id"] is not None
                    and data.get("task_page") is not None
                ):
                    button_kwargs_map[(row, 0)] = {
                        "callback_data": f"taskpagination_{data['theme_id']}_{data['task_page']}_1"
                    }
                elif content_type == ContentType.QUESTION:
                    button_kwargs_map[(row, 0)] = {
                        "callback_data": f"examquestion_{data['item_id']}"
                    }
                row += 1

        keyboard = inline_kb(
            buttons, self._route, button_kwargs_map=button_kwargs_map or None
        )

        await callback.answer()
        await callback.message.edit_text(
            text, **self.DEFAULT_SEND_PARAMS, reply_markup=keyboard
        )
