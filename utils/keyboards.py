from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def inline_kb(
    matrix_texts: list[list[str]], callback_prefix: str
) -> InlineKeyboardMarkup:
    rows = []
    for r, row in enumerate(matrix_texts):
        buttons_row = []
        for c, text in enumerate(row):
            buttons_row.append(
                InlineKeyboardButton(
                    text=text, callback_data=f"{callback_prefix}_{r}_{c}"
                )
            )
        rows.append(buttons_row)
    return InlineKeyboardMarkup(inline_keyboard=rows)
