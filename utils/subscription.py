from aiogram.types import CallbackQuery
from database.models.user import User
from services.text import text_service
from utils.keyboards import inline_kb


async def if_not_premium(
    callback: CallbackQuery, username: str, default_send_params: dict
):
    text = text_service.get("events.if_not_premium.text", username=username)
    buttons = text_service.get("events.if_not_premium.buttons")
    keyboard = inline_kb(buttons, "subscribe")

    await callback.message.answer(text, reply_markup=keyboard, **default_send_params)
    await callback.message.delete()
