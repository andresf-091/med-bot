from aiogram import F
from aiogram.types import CallbackQuery
import random
from handlers.base import BaseHandler
from services.context import context_service
from services.text import text_service, escape_md2
from utils.keyboards import inline_kb
from utils.subscription import if_not_premium
from database import (
    db,
    ContentType,
    UserService,
    ItemService,
    ThemeService,
    ResultService,
)
from log import get_logger

logger = get_logger(__name__)


def _parse_question(item):
    options_raw = item.options if isinstance(item.options, list) else []
    options = []
    correct_idx = None

    for option in options_raw:
        if isinstance(option, dict):
            text = option.get("text")
            if text is None:
                continue
            options.append(str(text))
            if option.get("is_correct") is True:
                correct_idx = len(options) - 1
        else:
            options.append(str(option))

    if not item.content or len(options) < 2 or correct_idx is None:
        return None

    return {
        "id": item.id,
        "question": item.content,
        "options": options,
        "correct_idx": correct_idx,
    }


def _shuffle_question(question_data: dict, rng: random.Random):
    options = list(question_data["options"])
    indices = list(range(len(options)))
    rng.shuffle(indices)

    shuffled_options = [options[i] for i in indices]
    shuffled_correct_idx = indices.index(question_data["correct_idx"])

    return {
        "id": question_data["id"],
        "question": question_data["question"],
        "options": shuffled_options,
        "correct_idx": shuffled_correct_idx,
    }


class ExamInstructionEvent(BaseHandler):

    def get_filter(self):
        return (F.data.startswith("studytheme_") & F.data.endswith("_2_0")) | (
            F.data.startswith("examinstruction_")
        )

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name

        parts = callback.data.split("_")
        theme_id = int(parts[1])

        with db.session() as session:
            user_service = UserService(session)
            user_db = user_service.get(tg_id=user.id)[0]
            is_premium = user_service.is_premium(user_db.id)

            if is_premium:
                theme_service = ThemeService(session)
                themes = theme_service.get(id=theme_id)

                item_service = ItemService(session)
                questions = item_service.get(
                    theme_id=theme_id,
                    type=ContentType.QUESTION,
                )

        if not is_premium:
            await if_not_premium(callback, username, self.DEFAULT_SEND_PARAMS)
            return
        if not themes:
            await callback.answer(
                text_service.get("events.exam.messages.theme_not_found")
            )
            return
        if not questions:
            await callback.answer(text_service.get("events.exam.messages.no_questions"))
            return

        difficulties = sorted(
            {
                int(question.difficulty)
                for question in questions
                if question.difficulty is not None and _parse_question(question)
            }
        )

        if not difficulties:
            await callback.answer(
                text_service.get("events.exam.messages.invalid_questions")
            )
            return

        logger.info(
            f"Exam instruction for theme {theme_id}, levels {difficulties}: {username}"
        )

        instruction = text_service.get(
            "events.exam.instruction_body",
            levels=", ".join(map(str, difficulties)),
        )
        text = text_service.get("events.exam_instruction.text", instruction=instruction)

        buttons = [
            [text_service.get("events.exam.buttons.difficulty", difficulty=difficulty)]
            for difficulty in difficulties
        ]
        buttons.append([text_service.get("events.exam.buttons.back")])

        button_kwargs_map = {
            (i, 0): {"callback_data": f"examstart_{theme_id}_{difficulty}"}
            for i, difficulty in enumerate(difficulties)
        }
        button_kwargs_map[(len(buttons) - 1, 0)] = {
            "callback_data": f"studythemes_{theme_id}_0_0"
        }
        keyboard = inline_kb(
            buttons,
            f"examinstruction_{theme_id}",
            button_kwargs_map=button_kwargs_map,
        )

        await callback.answer()
        await callback.message.edit_text(
            text,
            **self.DEFAULT_SEND_PARAMS,
            reply_markup=keyboard,
        )


class ExamPaginationEvent(BaseHandler):

    def get_filter(self):
        return F.data.startswith("examstart_") | F.data.startswith("exampagination_")

    def _question_keyboard(
        self, theme_id: int, difficulty: int, q_idx: int, q_data: dict
    ):
        rows = [[option] for option in q_data["options"]]
        rows.append([text_service.get("events.exam.buttons.to_menu")])

        button_kwargs_map = {}
        for i, _ in enumerate(q_data["options"]):
            button_kwargs_map[(i, 0)] = {
                "callback_data": (
                    f"exampagination_{theme_id}_{difficulty}_{q_idx}_{q_data['id']}_{i}"
                )
            }
        button_kwargs_map[(len(rows) - 1, 0)] = {
            "callback_data": f"studythemes_{theme_id}_0_0"
        }
        return inline_kb(
            rows,
            f"exampagination_{theme_id}_{difficulty}_{q_idx}",
            button_kwargs_map=button_kwargs_map,
        )

    async def handle(self, callback: CallbackQuery):
        user = callback.from_user
        username = user.username or user.first_name

        if callback.data.startswith("examstart_"):
            _, theme_id_s, difficulty_s = callback.data.split("_")
            theme_id = int(theme_id_s)
            difficulty = int(difficulty_s)

            with db.session() as session:
                user_service = UserService(session)
                user_db = user_service.get(tg_id=user.id)[0]
                is_premium = user_service.is_premium(user_db.id)

                if is_premium:
                    item_service = ItemService(session)
                    questions_raw = item_service.get(
                        theme_id=theme_id,
                        type=ContentType.QUESTION,
                        difficulty=difficulty,
                    )

            if not is_premium:
                await if_not_premium(callback, username, self.DEFAULT_SEND_PARAMS)
                return
            if not questions_raw:
                await callback.answer(
                    text_service.get("events.exam.messages.level_no_questions")
                )
                return

            questions = []
            rng = random.SystemRandom()
            for item in questions_raw:
                question_data = _parse_question(item)
                if question_data:
                    questions.append(_shuffle_question(question_data, rng))

            rng.shuffle(questions)

            if not questions:
                await callback.answer(
                    text_service.get("events.exam.messages.level_invalid_questions")
                )
                return

            exam_state = {
                "theme_id": theme_id,
                "difficulty": difficulty,
                "questions": questions,
                "current_index": 0,
                "score": 0,
            }
            context_service.set(user.id, "exam_state", exam_state)

            q_data = questions[0]
            text = text_service.get(
                "events.exam_pagination.text",
                question_number=1,
                total_questions=len(questions),
                question=q_data["question"],
            )
            keyboard = self._question_keyboard(theme_id, difficulty, 0, q_data)

            logger.info(
                f"Exam started theme={theme_id}, difficulty={difficulty}, questions={len(questions)}: {username}"
            )

            await callback.answer()
            await callback.message.edit_text(
                text,
                **self.DEFAULT_SEND_PARAMS,
                reply_markup=keyboard,
            )
            return

        parts = callback.data.split("_")
        if len(parts) != 6:
            await callback.answer()
            return

        theme_id = int(parts[1])
        difficulty = int(parts[2])
        question_index = int(parts[3])
        question_id = int(parts[4])
        answer_index = int(parts[5])

        exam_state = context_service.get(user.id, "exam_state")
        if not exam_state:
            await callback.answer(
                text_service.get("events.exam.messages.state_not_found")
            )
            return

        if (
            exam_state.get("theme_id") != theme_id
            or exam_state.get("difficulty") != difficulty
            or exam_state.get("current_index") != question_index
        ):
            await callback.answer(
                text_service.get("events.exam.messages.question_already_updated")
            )
            return

        questions = exam_state["questions"]
        if question_index >= len(questions):
            await callback.answer(
                text_service.get("events.exam.messages.already_finished")
            )
            return

        current_question = questions[question_index]
        if current_question["id"] != question_id:
            await callback.answer(
                text_service.get("events.exam.messages.question_outdated")
            )
            return

        is_correct = answer_index == current_question["correct_idx"]
        exam_state["score"] += 1 if is_correct else -1
        next_index = question_index + 1

        if next_index >= len(questions):
            with db.session() as session:
                user_service = UserService(session)
                user_db = user_service.get(tg_id=user.id)[0]

                result_service = ResultService(session)
                result_service.create(
                    user_id=user_db.id,
                    theme_id=theme_id,
                    difficulty=difficulty,
                    score=exam_state["score"],
                    total_questions=len(questions),
                )

            final_score = exam_state["score"]
            context_service.clear_key(user.id, "exam_state")

            logger.info(
                f"Exam finished theme={theme_id}, difficulty={difficulty}, score={final_score}/{len(questions)}: {username}"
            )

            finish_text = text_service.get(
                "events.exam.finish_text",
                difficulty=difficulty,
                score=final_score,
                total_questions=len(questions),
            )
            keyboard = inline_kb(
                [
                    [text_service.get("events.exam.buttons.to_theme")],
                    [text_service.get("events.exam.buttons.retry_level")],
                ],
                f"examfinish_{theme_id}_{difficulty}",
                button_kwargs_map={
                    (0, 0): {"callback_data": f"studythemes_{theme_id}_0_0"},
                    (1, 0): {"callback_data": f"examstart_{theme_id}_{difficulty}"},
                },
            )
            await callback.answer(
                text_service.get("events.exam.messages.answer_accepted")
            )
            await callback.message.edit_text(
                finish_text,
                **self.DEFAULT_SEND_PARAMS,
                reply_markup=keyboard,
            )
            return

        exam_state["current_index"] = next_index
        context_service.set(user.id, "exam_state", exam_state)

        next_question = questions[next_index]
        text = text_service.get(
            "events.exam_pagination.text",
            question_number=next_index + 1,
            total_questions=len(questions),
            question=next_question["question"],
        )
        keyboard = self._question_keyboard(
            theme_id, difficulty, next_index, next_question
        )

        await callback.answer(
            text_service.get("events.exam.messages.answer_correct")
            if is_correct
            else text_service.get("events.exam.messages.answer_wrong")
        )
        await callback.message.edit_text(
            text,
            **self.DEFAULT_SEND_PARAMS,
            reply_markup=keyboard,
        )
