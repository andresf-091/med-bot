from aiogram import F
from aiogram.types import CallbackQuery, InputMediaPhoto
from handlers.base import BaseHandler
from services.context import context_service
from services.text import text_service
from services.image_storage import LocalImageStorage
from database import db, ItemService, ContentType, ImageService
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

        if callback.data == "theorypagination_2_0":
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
        return (
            F.data.startswith("theoryvariants_") & (F.data != "theoryvariants_2_0")
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

        with db.session() as session:
            item_service = ItemService(session)
            items = item_service.get(theme_id=theme_id, type=ContentType.THEORY)

            if items:
                image_service = ImageService(session)
                images = image_service.get(item_id=items[0].id)

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

        buttons = text_service.get("events.theory_pagination.buttons")
        is_end = (page + 1) == total_pages
        is_start = page == 0
        keyboard = inline_kb(
            buttons,
            self._route,
            variants_map={(0, 0): int(is_end), (1, 0): int(is_start)},
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
            if (page != current_page) or (current_page is None):
                await callback.message.edit_text(
                    text,
                    **self.DEFAULT_SEND_PARAMS,
                    reply_markup=keyboard,
                )
                await callback.answer()

            else:
                await callback.answer("Это первая/последняя страница")
