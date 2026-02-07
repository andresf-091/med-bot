from aiogram import F
from aiogram.types import Message
from services.text import text_service
from database import db, UserService, ReferralService
from handlers.base import BaseHandler
from utils.keyboards import inline_kb
from utils.referral import validate_referral_code, get_sender_id
from log import get_logger

logger = get_logger(__name__)


class StartCommand(BaseHandler):

    def __init__(self, router):
        super().__init__(router)
        self.handler_type = "message"

    def get_filter(self):
        return F.text.startswith("/start")

    async def handle(self, message: Message):
        user = message.from_user
        username = user.username or user.first_name

        msg_text = message.text or ""
        referral_code = None
        if len(msg_text.split()) > 1:
            referral_code = msg_text.split()[1]

        with db.session() as session:
            user_service = UserService(session)
            users = user_service.get(tg_id=user.id)
            if not users:
                if referral_code:
                    referral_service = ReferralService(session)
                    validated = validate_referral_code(referral_code)
                    if validated:
                        user_service.create(tg_id=user.id, username=username)
                        sender_id = get_sender_id(referral_code)
                        referral_service.create(user_id=user.id, referral_id=sender_id)
                    else:
                        logger.warning(
                            f"Invalid referral code: {referral_code} by user {user.id} {username}"
                        )
                else:
                    user_service.create(tg_id=user.id, username=username)
            else:
                user_db = users[0]
                if not user_db.username:
                    user_service.update(id=user_db.id, username=username)

        if referral_code and not validated:
            await message.reply(
                text_service.get("errors.invalid_referral_code.text"),
                **self.DEFAULT_SEND_PARAMS,
            )
            return

        logger.info(f"Start command: {username}")

        buttons = text_service.get("commands.start.buttons")
        keyboard = inline_kb(buttons, self._route)
        text = text_service.get("commands.start.text", username=username)

        await message.reply(
            text,
            **self.DEFAULT_SEND_PARAMS,
            reply_markup=keyboard,
        )
