import logging
from typing import Dict, Union

from src.utils import load_json, save_json

DropData = Union[str, float]
Notes = Dict[str, str]
Category = Dict[str, dict]
Label = Dict[str, dict]

GENERAL_KEY = "general"
DROP_DATA_KEY = "drop_data"
LABELS_KEY = "labels"
CATEGORIES_KEY = "categories"
NOTES_KEY = "notes"

logger = logging.getLogger(__name__)


class ConfigManager:

    def __init__(self, path: str) -> None:
        self.path = path
        self.config = None
        self.load_config()

    def load_config(self) -> None:
        try:
            self.config = load_json(self.path)
        except Exception as e:
            logger.error(f"Cannot load config from file. Error: {e}")
            raise Exception("File I/O error")

    def save_config(self) -> None:
        try:
            save_json(self.path, self.config)
        except Exception as e:
            logger.error(f"Cannot save config to file. Error: {e}")
            raise Exception("File I/O error")

    def add_category(self, name: str, data: Category) -> None:
        self.config[CATEGORIES_KEY][name] = data

    def add_label(self, name: str, data: Label) -> None:
        self.config[LABELS_KEY][name] = data

    def add_drop_data(self, name: str, data: DropData) -> None:
        drop_data = self.config[DROP_DATA_KEY]
        values = drop_data.get(name)
        if values is None:
            values = [data]
        else:
            values += [data]
        drop_data[name] = values
        self.config[DROP_DATA_KEY] = drop_data

    def add_notes(self, notes: Notes) -> None:
        current_notes = self.config[NOTES_KEY]
        combined_notes = {**current_notes, **notes}
        self.config[NOTES_KEY] = combined_notes

    def get_config(self) -> dict:
        return self.config.copy()
