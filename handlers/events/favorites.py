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

        items = []

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
                        items.append(item_service.get(id=favorite.item_id)[0])

        if not is_premium:
            await if_not_premium(callback, username, **self.DEFAULT_SEND_PARAMS)
            return
        if not favorites:
            await callback.answer("Избранные не найдены")
            return

        logger.debug(f"Favorites: {username}")

        text = text_service.get("events.favorites.text")
        buttons = text_service.get("events.favorites.buttons", copy_obj=True)
        for item in items:
            if item.type == ContentType.THEORY:
                buttons.append(["📚 Теория 📚"])
            elif item.type == ContentType.SLIDE:
                buttons.append(["🔬 Препараты 🔬"])
            elif item.type == ContentType.TASK:
                buttons.append(["📜 Задачи 📜"])
            elif item.type == ContentType.QUESTION:
                buttons.append(["❔ Вопросы тестов ❔"])
            buttons.append([item.title])
        keyboard = inline_kb(buttons, self._route)

        await callback.answer()
        await callback.message.edit_text(
            text, **self.DEFAULT_SEND_PARAMS, reply_markup=keyboard
        )
