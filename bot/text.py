import json
import os
from log import get_logger

logger = get_logger(__name__)


class TextManager:

    def __init__(self, locale: str = "ru"):
        self.locale = locale
        self._text = self._load_text()
        logger.info(f"TextManager initialized for locale: {self.locale}")

    def _load_text(self) -> dict:
        path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "locales", f"{self.locale}.json"
        )
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    def get(self, key: str, **kwargs):
        keys = key.split(".")
        value = self._text
        for k in keys:
            if isinstance(value, dict):
                value = value[k]
            if isinstance(value, str):
                value = value.format(**kwargs)
        return value


text_manager = TextManager(locale="ru")
