from aiogram import F
from aiogram.types import CallbackQuery
from bot.text import text_manager
from handlers.base import BaseHandler
from utils.keyboards import inline_kb
from log import get_logger

logger = get_logger(__name__)

isSave = False  # временно
medication_name = "test"
medication_description = "test"


class MedicationListStartEvent(BaseHandler):

    def get_filter(self):
        return F.data.in_(["start_0_0", "medicationlistback_0_0"])

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name

        logger.info(f"Medication list start: {username}")

        buttons = text_manager.get("events.medication_list_start.buttons")
        keyboard = inline_kb(buttons, self._route)
        text = text_manager.get("events.medication_list_start.text", username=username)

        await callback.answer()
        await callback.message.edit_text(
            text,
            **self.DEFAULT_SEND_PARAMS,
            reply_markup=keyboard,
        )


class MedicationListSliderEvent(BaseHandler):

    def get_filter(self):
        return F.data == "medicationliststart_0_0"

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name

        logger.info(f"Medication list slider: {username}")

        buttons = text_manager.get("events.medication_list_slider.buttons")
        keyboard = inline_kb(
            buttons, self._route, variant=int(isSave), include_variant_in_callback=True
        )
        text = text_manager.get(
            "events.medication_list_slider.text",
            medication_name=medication_name,
            medication_description=medication_description,
        )

        await callback.answer()
        await callback.message.edit_text(
            text,
            **self.DEFAULT_SEND_PARAMS,
            reply_markup=keyboard,
        )


class MedicationListSaveEvent(BaseHandler):

    def get_filter(self):
        return F.data.in_(["medicationlistunsave_1_1_0", "medicationlistslider_1_1_0"])

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name
        isSave = True

        logger.info(f"Save medication: {username}")

        buttons = text_manager.get("events.medication_list_slider.buttons")
        keyboard = inline_kb(
            buttons, self._route, variant=int(isSave), include_variant_in_callback=True
        )

        await callback.answer()
        await callback.message.edit_reply_markup(
            reply_markup=keyboard,
        )


class MedicationListUnsaveEvent(BaseHandler):

    def get_filter(self):
        return F.data.in_(["medicationlistsave_1_1_1", "medicationlistslider_1_1_1"])

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name
        isSave = False

        logger.info(f"Unsave medication: {username}")

        buttons = text_manager.get("events.medication_list_slider.buttons")
        keyboard = inline_kb(
            buttons, self._route, variant=int(isSave), include_variant_in_callback=True
        )

        await callback.answer()
        await callback.message.edit_reply_markup(
            reply_markup=keyboard,
        )


class MedicationListBackEvent(BaseHandler):

    def get_filter(self):
        return F.data.in_(
            [
                "medicationlistsave_1_0",
                "medicationlistunsave_1_0",
                "medicationlistslider_1_0",
                "medicationlistback_1_0",
            ]
        )

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name

        logger.info(f"Medication list back: {username}")

        buttons = text_manager.get("events.medication_list_back.buttons")
        keyboard = inline_kb(buttons, self._route, include_variant_in_callback=True)
        text = text_manager.get("events.medication_list_back.text", username=username)

        await callback.answer()
        await callback.message.edit_text(
            text,
            **self.DEFAULT_SEND_PARAMS,
            reply_markup=keyboard,
        )
