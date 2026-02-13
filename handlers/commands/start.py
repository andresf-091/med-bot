from aiogram import F
from aiogram.types import Message
from services.text import text_service, escape_md2
from database import db, UserService, ReferralService
from handlers.base import BaseHandler
from utils.keyboards import inline_kb
from utils.referral import validate_referral_code, extract_ref_code
from utils.subscription import get_profile_subscription_content
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

        validated = False
        senders = []
        is_new_via_referral = False

        with db.session() as session:
            user_service = UserService(session)
            users = user_service.get(tg_id=user.id)
            if not users:
                if referral_code:
                    validated = validate_referral_code(referral_code)
                    if validated:
                        ref_code = extract_ref_code(referral_code)
                        senders = user_service.get(ref_code=ref_code)
                        if senders:
                            sender_db = senders[0]
                            new_user = user_service.create(
                                tg_id=user.id, username=username
                            )
                            referral_service = ReferralService(session)
                            referral_service.create(
                                user_id=sender_db.id, referral_id=new_user.id
                            )
                            is_new_via_referral = True
                if not users and not (referral_code and validated and senders):
                    user_service.create(tg_id=user.id, username=username)
            else:
                user_db = users[0]
                if not user_db.username:
                    user_service.update(id=user_db.id, username=username)

        if referral_code and not users and not (validated and senders):
            logger.warning(
                f"Invalid referral code: {referral_code} by user {user.id} {username}"
            )
            await message.reply(
                text_service.get("errors.invalid_referral_code.text"),
                **self.DEFAULT_SEND_PARAMS,
            )
            return

        logger.info(f"Start command: {username}")

        if is_new_via_referral:
            with db.session() as session:
                user_service = UserService(session)
                users = user_service.get(tg_id=user.id)
                user_db = users[0]
                text, keyboard = get_profile_subscription_content(session, user_db)
            await message.reply(
                text,
                **self.DEFAULT_SEND_PARAMS,
                reply_markup=keyboard,
            )
            return

        buttons = text_service.get("commands.start.buttons")
        keyboard = inline_kb(buttons, self._route)
        text = text_service.get("commands.start.text", username=escape_md2(username))

        await message.reply(
            text,
            **self.DEFAULT_SEND_PARAMS,
            reply_markup=keyboard,
        )
