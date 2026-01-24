from aiogram import F
from aiogram.types import CallbackQuery, InputMediaPhoto
from handlers.base import BaseHandler
from utils.keyboards import inline_kb
from services.context import context_service
from services.text import text_service
from services.image_storage import LocalImageStorage
from database import db, ItemService, ThemeService, ContentType, ImageService
from log import get_logger

logger = get_logger(__name__)


class SlidesListEvent(BaseHandler):

    def get_filter(self):
        return F.data.in_(["studytheme_1_0", "slide_0_0"])

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name
        theme_id = context_service.get(user.id, "study_theme")

        with db.session() as session:
            theme_service = ThemeService(session)
            theme = theme_service.get(id=theme_id)
            if not theme:
                await callback.answer("Тема не найдена")
                return
            theme_name = theme[0].name

            item_service = ItemService(session)
            slides = item_service.get(theme_id=theme_id, type=ContentType.SLIDE)
            if not slides:
                await callback.answer("Препараты для этой темы не найдены")
                return
            slide_titles = [slide.title for slide in slides]

        logger.info(f"Slides list for theme {theme_id}: {username}")

        buttons = text_service.get("events.slides_list.buttons", copy_obj=True)
        for slide_title in slide_titles:
            buttons.append([slide_title.replace("\\", "")])
        keyboard = inline_kb(buttons, self._route)
        text = text_service.get("events.slides_list.text", theme=theme_name)

        await callback.answer()
        await callback.message.edit_text(
            text,
            **self.DEFAULT_SEND_PARAMS,
            reply_markup=keyboard,
        )


class SlidePaginationEvent(BaseHandler):

    def get_filter(self):
        return F.data.startswith("slideslist_") & (
            F.data != "slideslist_0_0"
        ) | F.data.startswith("slidepagination_") & (~F.data.endswith("_2_0")) & (
            ~F.data.endswith("_1_1")
        )

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name
        theme_id = context_service.get(user.id, "study_theme")
        slide_order = int(callback.data.split("_")[1]) - int(
            callback.data.startswith("slideslist_")
        )

        current_page = context_service.get(user.id, f"slide_page_{slide_order}", 0)

        if callback.data.startswith("slideslist_"):
            page = 0
            context_service.clear_key(user.id, f"slide_page_{slide_order}")
        elif callback.data.endswith("_1_0"):
            page = max(0, current_page - 1)
        else:
            page = current_page + 1

        with db.session() as session:
            item_service = ItemService(session)
            slides = item_service.get(
                theme_id=theme_id, type=ContentType.SLIDE, order=slide_order
            )

            if slides:
                image_service = ImageService(session)
                images = image_service.get(item_id=slides[0].id)

        if not slides:
            await callback.answer("Препараты не найдены")
            return
        if not images:
            await callback.answer("Изображения не найдены")
            return

        slide = slides[0]
        total_pages = len(images)
        page = min(page, total_pages - 1)
        context_service.set(user.id, f"slide_page_{slide_order}", page)

        image = images[page]
        local_image_storage = LocalImageStorage()

        if image.file_id:
            image_input = image.file_id
        else:
            image_input = local_image_storage.get_input_file(
                relative_path=image.content
            )

        description = image.caption if image.caption else slide.content
        text = text_service.get(
            "events.slide_pagination.text",
            page=page + 1,
            total_pages=total_pages,
            slide=slide.title,
            description=description,
        )

        buttons = text_service.get("events.slide_pagination.buttons")
        is_end = (page + 1) == total_pages
        is_start = page == 0
        keyboard = inline_kb(
            buttons,
            self._route + f"_{slide_order}",
            variants_map={(0, 0): int(is_end), (1, 0): int(is_start)},
        )

        logger.info(
            f"Slide pagination page {page + 1} / {total_pages} for slide {slide.title}: {username}"
        )

        if callback.data.startswith("slideslist_"):
            msg = await callback.message.answer_photo(
                photo=image_input,
                caption=text,
                **self.DEFAULT_SEND_PARAMS,
                reply_markup=keyboard,
            )
            await callback.answer()

            if not image.file_id and msg.photo:
                file_id = msg.photo[-1].file_id
                with db.session() as session:
                    image_service = ImageService(session)
                    image_service.update(image.id, file_id=file_id)
        else:
            if (page != current_page) or (current_page is None):
                upd_msg = await callback.message.edit_media(
                    media=InputMediaPhoto(
                        media=image_input, caption=text, **self.DEFAULT_SEND_PARAMS
                    ),
                    reply_markup=keyboard,
                )
                await callback.answer()

                if not image.file_id and upd_msg.photo:
                    file_id = upd_msg.photo[-1].file_id
                    with db.session() as session:
                        image_service = ImageService(session)
                        image_service.update(image.id, file_id=file_id)
            else:
                await callback.answer("Это первая/последняя страница")


class SlidePaginationDeleteEvent(BaseHandler):

    def get_filter(self):
        return F.data.startswith("slidepagination_") & F.data.endswith("_2_0")

    async def handle(self, callback: CallbackQuery):
        slide_order = int(callback.data.split("_")[1])
        context_service.clear_key(callback.from_user.id, f"slide_page_{slide_order}")
        await callback.answer()
        await callback.message.delete()
