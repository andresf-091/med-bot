import json
import os
import copy
from log import get_logger

logger = get_logger(__name__)


class TextService:

    def __init__(self, locale: str = "ru"):
        self.locale = locale
        self._text = self._load_text()
        logger.info(f"TextService initialized for locale: {self.locale}")

    def _load_text(self) -> dict:
        path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "locales", f"{self.locale}.json"
        )
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    def get(self, key: str, copy_obj=False, **kwargs):
        keys = key.split(".")
        value = self._text
        for k in keys:
            if isinstance(value, dict):
                value = value[k]
            if isinstance(value, str):
                value = value.format(**kwargs)
        return copy.deepcopy(value) if copy_obj else value


text_service = TextService(locale="ru")

MD2_ESCAPE = (
    "_",
    "*",
    "[",
    "]",
    "(",
    ")",
    "~",
    "`",
    ">",
    "#",
    "+",
    "-",
    "=",
    "|",
    "{",
    "}",
    ".",
    "!",
)


def escape_md2(s):
    if s is None:
        return ""
    out = str(s)
    for c in MD2_ESCAPE:
        out = out.replace(c, "\\" + c)
    return out


def format_date(date):
    if date is None:
        return "Нет"
    formatted = date.strftime("%d.%m.%Y %H:%M")
    return formatted.replace("-", "\\-").replace(".", "\\.")
