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
CHECKS_KEY = "checks"
NOTES_KEY = "notes"

logger = logging.getLogger(__name__)


class ConfigManager:

    def __init__(self, path: str) -> None:
        self.path = path
        self._config = None
        self.load_config()

    def load_config(self) -> None:
        try:
            self._config = load_json(self.path)
        except Exception as e:
            logger.error(f"Cannot load config from file. Error: {e}")
            raise Exception("File I/O error")

    def save_config(self) -> None:
        try:
            save_json(self.path, self._config)
        except Exception as e:
            logger.error(f"Cannot save config to file. Error: {e}")
            raise Exception("File I/O error")

    def add_category(self, name: str, data: Category) -> None:
        self._config[CATEGORIES_KEY][name] = data

    def add_label(self, name: str, data: Label) -> None:
        self._config[LABELS_KEY][name] = data

    def add_drop_data(self, name: str, data: DropData) -> None:
        drop_data = self._config[DROP_DATA_KEY]
        values = drop_data.get(name)
        if values is None:
            values = [data]
        else:
            values += [data]
        drop_data[name] = values
        self._config[DROP_DATA_KEY] = drop_data

    def add_notes(self, notes: Notes) -> None:
        for event_id, note in notes.items():
            self._config[NOTES_KEY][event_id] = note

    def update_note(self, event_id, note: str) -> None:
        self._config[NOTES_KEY][event_id] = note

    def remove_note_if_exist(self, event_id) -> None:
        self._config[NOTES_KEY].pop(event_id, None)

    def get_config(self) -> dict:
        return self._config.copy()
