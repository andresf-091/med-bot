import re

from aiogram import F
from aiogram.enums import ChatType
from aiogram.types import CallbackQuery, Message, ReactionTypeEmoji
from bot.config import Config
from handlers.base import BaseHandler
from services.text import text_service
from utils.keyboards import inline_kb
from log import get_logger

logger = get_logger(__name__)

_awaiting_support = set()


class ContactEvent(BaseHandler):
    def get_filter(self):
        return F.data == "start_2_1"

    async def handle(self, callback: CallbackQuery):
        if not Config.SUPPORT_GROUP_ID:
            await callback.answer()
            await callback.message.edit_text(
                text_service.get("errors.support_unavailable"),
                **self.DEFAULT_SEND_PARAMS,
            )
            return
        _awaiting_support.add(callback.from_user.id)
        logger.info(
            "Contact opened: user_id=%s username=%s",
            callback.from_user.id,
            callback.from_user.username or callback.from_user.full_name,
        )
        text = text_service.get("events.contact.prompt")
        buttons = text_service.get("events.contact.buttons")
        keyboard = inline_kb(buttons, "support")
        await callback.answer()
        await callback.message.edit_text(
            text, **self.DEFAULT_SEND_PARAMS, reply_markup=keyboard
        )


class SupportCancelEvent(BaseHandler):
    def __init__(self, router):
        super().__init__(router)
        self.handler_type = "callback_query"

    def get_filter(self):
        return F.data == "support_0_0"

    async def handle(self, callback: CallbackQuery):
        _awaiting_support.discard(callback.from_user.id)
        logger.info("Support cancelled: user_id=%s", callback.from_user.id)
        await callback.answer()
        await callback.message.edit_text(
            text_service.get("events.contact.cancel"), **self.DEFAULT_SEND_PARAMS
        )


class SupportRequestEvent(BaseHandler):
    def __init__(self, router):
        super().__init__(router)
        self.handler_type = "message"

    def get_filter(self):
        return F.text

    async def filter(self, update: Message) -> bool:
        return (
            update.chat.type == ChatType.PRIVATE
            and update.from_user.id in _awaiting_support
        )

    async def handle(self, message: Message):
        user = message.from_user
        _awaiting_support.discard(user.id)
        if not Config.SUPPORT_GROUP_ID:
            await message.reply(
                text_service.get("errors.support_unavailable"),
                **self.DEFAULT_SEND_PARAMS,
            )
            return
        name = (user.full_name or user.username or str(user.id)).replace("|", "/")
        username = (user.username or "-").replace("|", "/")
        header = f"📩 От @{username} (ID: {user.id})\nИмя: {name}\n\n"
        await message.bot.send_message(
            Config.SUPPORT_GROUP_ID,
            f"{header}{message.text}",
        )
        await message.bot.set_message_reaction(
            chat_id=message.chat.id,
            message_id=message.message_id,
            reaction=[ReactionTypeEmoji(emoji="👍")],
        )
        logger.info(
            "Support request forwarded: user_id=%s username=%s text_len=%s",
            user.id,
            user.username or user.full_name,
            len(message.text or ""),
        )


USER_ID_PATTERN = re.compile(r"\(ID:\s*(\d+)\)")


class SupportReplyToMessageEvent(BaseHandler):
    def __init__(self, router):
        super().__init__(router)
        self.handler_type = "message"

    def get_filter(self):
        return F.reply_to_message & F.text

    async def filter(self, update: Message) -> bool:
        if not Config.SUPPORT_GROUP_ID or update.chat.id != Config.SUPPORT_GROUP_ID:
            return False
        if update.from_user.id not in Config.ADMIN_IDS:
            return False
        reply_to = update.reply_to_message
        if not reply_to or not reply_to.from_user:
            return False
        if reply_to.from_user.id != update.bot.id:
            return False
        if not reply_to.text or "(ID:" not in reply_to.text:
            return False
        return True

    async def handle(self, message: Message):
        reply_to = message.reply_to_message
        match = USER_ID_PATTERN.search(reply_to.text)
        if not match:
            await message.reply(
                "Не удалось определить пользователя в сообщении.",
                **self.DEFAULT_SEND_PARAMS,
            )
            return
        user_id = int(match.group(1))
        await message.bot.send_message(
            user_id,
            f"Ответ поддержки:\n\n{message.text}",
        )
        await message.bot.set_message_reaction(
            chat_id=message.chat.id,
            message_id=message.message_id,
            reaction=[ReactionTypeEmoji(emoji="👍")],
        )
        logger.info(
            "Support reply sent: target_user_id=%s admin_id=%s text_len=%s",
            user_id,
            message.from_user.id,
            len(message.text or ""),
        )
