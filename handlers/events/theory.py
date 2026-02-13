from aiogram import F
from aiogram.types import CallbackQuery, InputMediaPhoto
from handlers.base import BaseHandler
from services.context import context_service
from services.text import text_service
from services.image_storage import LocalImageStorage
from database import (
    db,
    ItemService,
    ContentType,
    ImageService,
    UserService,
    FavoriteService,
)
from utils.keyboards import inline_kb
from utils.paginator import split_content
from utils.subscription import if_not_premium
from log import get_logger

logger = get_logger(__name__)


class TheoryVariantsEvent(BaseHandler):

    def get_filter(self):
        return (F.data.startswith("studytheme_") & F.data.endswith("_0_0")) | (
            F.data.startswith("theorypagination_") & F.data.endswith("_2_0")
        )

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name
        theme_id = int(callback.data.split("_")[1])

        logger.info(f"Theory variants for theme {theme_id}: {username}")

        buttons = text_service.get("events.theory_variants.buttons")
        keyboard = inline_kb(buttons, f"theoryvariants_{theme_id}")
        text = text_service.get("events.theory_variants.text")

        await callback.answer()

        if callback.data.startswith("theorypagination_"):
            media_ids = context_service.get(user.id, "theory_media_message_ids")
            if media_ids:
                chat_id, message_ids = media_ids
                bot = callback.bot
                for mid in message_ids:
                    try:
                        await bot.delete_message(chat_id, mid)
                    except Exception:
                        pass
                context_service.clear_key(user.id, "theory_media_message_ids")

        await callback.message.edit_text(
            text,
            **self.DEFAULT_SEND_PARAMS,
            reply_markup=keyboard,
        )


class TheoryPaginationEvent(BaseHandler):

    def get_filter(self):
        cond_1 = F.data.startswith("theoryvariants_") & ~F.data.endswith("_2_0")
        cond_2 = F.data.startswith("theorypagination_")
        cond_3 = F.data.endswith("_0_0_0") | F.data.endswith("_1_0_0")
        cond_4 = F.data.endswith("_0_0_1") | F.data.endswith("_1_0_1")
        return cond_1 | (cond_2 & (cond_3 | cond_4))

    async def handle(self, callback: CallbackQuery):
        if callback.data.endswith("_0_0_1") or callback.data.endswith("_1_0_1"):
            await callback.answer("Это первая/последняя страница")
            return

        user = callback.from_user
        username = user.username or user.first_name
        parts = callback.data.split("_")
        theme_id = int(parts[1])
        current_page = (
            int(parts[2]) if callback.data.startswith("theorypagination_") else 0
        )
        is_full = callback.data.endswith("_0_0")

        if callback.data.startswith("theoryvariants_"):
            page = 0
        elif callback.data.endswith("_1_0_0"):
            page = max(0, current_page - 1)
        else:
            page = current_page + 1

        with db.session() as session:
            user_service = UserService(session)
            user_db = user_service.get(tg_id=user.id)[0]
            is_premium = user_service.is_premium(user_db.id)

            if is_premium:
                item_service = ItemService(session)
                items = item_service.get(
                    theme_id=theme_id, type=ContentType.THEORY, is_full=is_full
                )

                if items:
                    image_service = ImageService(session)
                    images = image_service.get(item_id=items[0].id)

                    favorite_service = FavoriteService(session)
                    is_favorite = favorite_service.is_favorite(
                        user_id=user_db.id,
                        item_id=items[0].id,
                        content_type=ContentType.THEORY,
                    )

        if not is_premium:
            await if_not_premium(callback, username, self.DEFAULT_SEND_PARAMS)
            return
        if not items:
            await callback.answer("Теория не найдена")
            return

        if images:
            image_storage = LocalImageStorage()
            image_inputs = [
                (
                    image.file_id
                    if image.file_id
                    else image_storage.get_input_file(image.content)
                )
                for image in images
            ]

        content = items[0].content
        pages = split_content(content)

        total_pages = len(pages)
        page = min(page, total_pages - 1)

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

        buttons = text_service.get("events.theory_pagination.buttons")
        is_end = (page + 1) == total_pages
        is_start = page == 0
        keyboard = inline_kb(
            buttons,
            f"theorypagination_{theme_id}_{page}_{int(is_full)}",
            variants_map={
                (0, 0): int(is_end),
                (1, 0): int(is_start),
                (1, 1): int(is_favorite),
            },
            include_variant_in_callback=True,
        )

        if callback.data.startswith("theoryvariants_"):
            if images:
                msg = await callback.message.answer_media_group(
                    media=[
                        InputMediaPhoto(
                            media=image_input,
                            **self.DEFAULT_SEND_PARAMS,
                        )
                        for image_input in image_inputs
                    ],
                )
                if msg:
                    context_service.set(
                        user.id,
                        "theory_media_message_ids",
                        (callback.message.chat.id, [m.message_id for m in msg]),
                    )
                    need_save = msg and any(not img.file_id for img in images)
                    if need_save:
                        with db.session() as session:
                            image_service = ImageService(session)
                            for i, image in enumerate(images):
                                if not image.file_id and i < len(msg) and msg[i].photo:
                                    file_id = msg[i].photo[-1].file_id
                                    image_service.update(image.id, file_id=file_id)
            await callback.message.edit_text(
                text,
                **self.DEFAULT_SEND_PARAMS,
                reply_markup=keyboard,
            )
            await callback.answer()

        else:
            await callback.message.edit_text(
                text,
                **self.DEFAULT_SEND_PARAMS,
                reply_markup=keyboard,
            )
            await callback.answer()


class TheoryFavoriteEvent(BaseHandler):

    def get_filter(self):
        cond_1 = F.data.startswith("theorypagination_")
        cond_2 = F.data.endswith("_1_1_0")
        cond_3 = F.data.endswith("_1_1_1")
        return cond_1 & (cond_2 | cond_3)

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name
        parts = callback.data.split("_")
        theme_id = int(parts[1])
        page = int(parts[2])
        is_full = bool(parts[3])

        with db.session() as session:
            user_service = UserService(session)
            user_db = user_service.get(tg_id=user.id)[0]
            is_premium = user_service.is_premium(user_db.id)

            if is_premium:
                item_service = ItemService(session)
                items = item_service.get(
                    theme_id=theme_id, type=ContentType.THEORY, is_full=is_full
                )
                if items:
                    favorite_service = FavoriteService(session)
                    is_favorite = favorite_service.toggle(
                        user_id=user_db.id,
                        item_id=items[0].id,
                        content_type=ContentType.THEORY,
                    )

        if not is_premium:
            await if_not_premium(callback, username, self.DEFAULT_SEND_PARAMS)
            return
        if not items:
            await callback.answer("Теория не найдена")
            return

        content = items[0].content
        pages = split_content(content)

        total_pages = len(pages)

        logger.debug(
            f"Theory favorite toggled: {is_favorite} for theme {theme_id}: {username}"
        )

        theory_text = pages[page]
        text = text_service.get(
            "events.theory_pagination.text",
            page=page + 1,
            total_pages=total_pages,
            theory=theory_text,
        )

        buttons = text_service.get("events.theory_pagination.buttons")
        is_end = (page + 1) == total_pages
        is_start = page == 0
        keyboard = inline_kb(
            buttons,
            f"theorypagination_{theme_id}_{page}",
            variants_map={
                (0, 0): int(is_end),
                (1, 0): int(is_start),
                (1, 1): int(is_favorite),
            },
            include_variant_in_callback=True,
        )

        await callback.message.edit_text(
            text,
            **self.DEFAULT_SEND_PARAMS,
            reply_markup=keyboard,
        )
        await callback.answer()
