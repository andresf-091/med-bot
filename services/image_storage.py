from pathlib import Path
from aiogram.types import FSInputFile
from bot.config import Config


class LocalImageStorage:
    def __init__(self, base_dir=None):
        root = base_dir or "storage/images"
        self.base_path = Path(root)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def build_path(self, relative_path):
        return self.base_path / relative_path

    def get_input_file(self, relative_path):
        path = self.build_path(relative_path)
        return FSInputFile(path)
