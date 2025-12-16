from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def inline_kb(
    matrix_texts: list[list[object]],
    callback_prefix: str,
    *,
    variant: int = 0,
    variants_map: dict[tuple[int, int], int] | None = None,
    variant_resolver=None,
    include_variant_in_callback: bool = False,
) -> InlineKeyboardMarkup:
    """
    Строит InlineKeyboardMarkup из "матрицы".

    Поддерживаемые элементы матрицы:
    - "Текст" (str) -> обычная кнопка
    - ["Вариант 1", "Вариант 2", ...] -> альтернативные тексты для одной кнопки

    Выбор активного варианта (если элемент - список):
    - variant: общий индекс по умолчанию
    - variants_map: точечный выбор по координатам (row, col) -> idx
    - variant_resolver: функция (row, col, options_list) -> idx

    callback_data по умолчанию: f"{callback_prefix}_{row}_{col}"
    если include_variant_in_callback=True:
      - для обычной кнопки: остается f"{callback_prefix}_{row}_{col}"
      - для варианта списка: f"{callback_prefix}_{row}_{col}_{variant_idx}"
    """
    rows = []
    for r, row in enumerate(matrix_texts):
        buttons_row = []
        for c, cell in enumerate(row):
            # cell может быть строкой или списком вариантов
            idx_for_callback = 0
            has_variants = False
            if isinstance(cell, list):
                has_variants = True
                if variant_resolver is not None:
                    idx = int(variant_resolver(r, c, cell))
                elif variants_map is not None and (r, c) in variants_map:
                    idx = int(variants_map[(r, c)])
                else:
                    idx = int(variant)

                if not cell:
                    text = ""
                else:
                    idx = max(0, min(idx, len(cell) - 1))
                    text = str(cell[idx])
                idx_for_callback = idx
            else:
                text = str(cell)

            if include_variant_in_callback and has_variants:
                cb = f"{callback_prefix}_{r}_{c}_{idx_for_callback}"
            else:
                cb = f"{callback_prefix}_{r}_{c}"

            buttons_row.append(InlineKeyboardButton(text=text, callback_data=cb))
        rows.append(buttons_row)
    return InlineKeyboardMarkup(inline_keyboard=rows)
