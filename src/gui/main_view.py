import glob
import logging
import os

import pandas as pd
from PyQt5.QtWidgets import QWidget, QHBoxLayout

from src.config_manager import GENERAL_KEY, DROP_DATA_KEY, CATEGORIES_KEY, LABELS_KEY
from src.data_processing.data_filtering import filter_data
from src.data_processing.data_preprocessing import DataPreprocessor
from src.gui.sidebar import SideBar
from src.gui.tabs.tab_handler import TabHandler

logger = logging.getLogger(__name__)


class MainView(QWidget):
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.data_processor = DataPreprocessor()
        self.data_all = None
        self.data_not_removed = None
        self.data_removed = None
        self.data_filtered = None

        self.tab_handler = TabHandler()
        self.sidebar = SideBar(self.config_manager.config[GENERAL_KEY]["default_data_dir"])
        self._set_layout()
        self._set_connections()

        if self.config_manager.config[GENERAL_KEY]["auto_load"]:
            logger.info(f"Auto load selected. Loading the data")
            pattern = self.config_manager.config[GENERAL_KEY]["auto_load_match_pattern"]
            paths = glob.glob(pattern)
            if len(paths) == 0:
                logger.info(f"Pattern {pattern} doesn't match any file. Auto loading will not be performed.")
                return
            self._handle_load_data(paths)

    def _set_layout(self):
        layout = QHBoxLayout()
        layout.addLayout(self.sidebar.layout, 1)
        layout.addLayout(self.tab_handler.layout, 6)
        self.setLayout(layout)

    def _set_connections(self):
        self.sidebar.load_data_signal.connect(self._handle_load_data)
        self.sidebar.filter_values_changed_signal.connect(self._handle_filtered_data_changed)
        self.sidebar.new_category_created_signal.connect(self._handle_new_category_created)
        self.sidebar.new_label_created_signal.connect(self._handle_new_label_created)

        self.tab_handler.events_tab.drop_data_added_signal.connect(self._handle_drop_data_added)
        self.tab_handler.events_tab.notes_edited_signal.connect(self._handle_filtered_data_notes_edited)
        self.tab_handler.events_filtered_out_tab.notes_edited_signal.connect(self._handle_removed_data_notes_edited)

    def _handle_load_data(self, file_paths):
        self.data_all = self.data_processor.get_data(file_paths)
        self.data_processor.update_extra_columns(self.data_all, self.config_manager.config)
        self.data_not_removed, self.data_removed = self.data_processor.drop_data(self.data_all,
                                                                                 self.config_manager.config[
                                                                                     DROP_DATA_KEY])
        self.data_filtered = self.data_not_removed.copy()
        self.tab_handler.handle_data(self.data_filtered)
        self.tab_handler.handle_removed_data(self.data_removed)

        datetime_min = self.data_not_removed.time.min()
        datetime_max = self.data_not_removed.time.max()
        self.sidebar.set_dates(datetime_min, datetime_max)

    def _handle_filtered_data_changed(self, filter_values):
        filter_values_nulls_removed = self._remove_null_values_from_dict(filter_values)
        self.data_filtered = filter_data(self.data_not_removed, **filter_values_nulls_removed)
        self.tab_handler.handle_data(self.data_filtered)

    def _handle_drop_data_added(self, data: tuple):
        name = data[0]
        value = data[1]

        self.config_manager.add_drop_data(name, value)
        self.data_processor.update_extra_columns(self.data_all, self.config_manager.config)
        drop_data = self.config_manager.config[DROP_DATA_KEY]
        self.data_not_removed, self.data_removed = self.data_processor.drop_data(self.data_all, drop_data)
        current_filter_values = self.sidebar.get_filter_values()
        filter_values_nulls_removed = self._remove_null_values_from_dict(current_filter_values)
        self.data_filtered = filter_data(self.data_not_removed, **filter_values_nulls_removed)

        self.tab_handler.handle_data(self.data_filtered)
        self.tab_handler.handle_removed_data(self.data_removed)
        self.config_manager.save_config()

    def _handle_new_category_created(self, data: tuple):
        name = data[0]
        filter_values = data[1]
        filter_values_nulls_removed = self._remove_null_values_from_dict(filter_values)
        filter_values_nulls_removed.pop("min_date")
        filter_values_nulls_removed.pop("max_date")

        self.config_manager.add_category(name, filter_values_nulls_removed)
        categories = self.config_manager.get_config()[CATEGORIES_KEY]
        self.data_processor.add_categories(self.data_filtered, categories)
        self.data_processor.add_categories(self.data_not_removed, categories)
        self.data_processor.add_categories(self.data_removed, categories)

        self.tab_handler.handle_data(self.data_filtered)
        self.tab_handler.handle_removed_data(self.data_removed)
        self.config_manager.save_config()

    def _handle_new_label_created(self, data: tuple):
        name = data[0]
        filter_values = data[1]
        filter_values_nulls_removed = self._remove_null_values_from_dict(filter_values)
        filter_values_nulls_removed.pop("min_date")
        filter_values_nulls_removed.pop("max_date")

        self.config_manager.add_label(name, filter_values_nulls_removed)
        labels = self.config_manager.get_config()[LABELS_KEY]
        self.data_processor.add_labels(self.data_filtered, labels)
        self.data_processor.add_labels(self.data_not_removed, labels)
        self.data_processor.add_labels(self.data_removed, labels)

        self.tab_handler.handle_data(self.data_filtered)
        self.tab_handler.handle_removed_data(self.data_removed)
        self.config_manager.save_config()

    def _handle_filtered_data_notes_edited(self, data: tuple):
        event_id = data[0]
        note = data[1]

        if note == "":
            self.config_manager.remove_note_if_exist(event_id)
        else:
            self.config_manager.update_note(event_id, note)
        self.data_not_removed.loc[self.data_not_removed.id == event_id, "notes"] = note
        self.data_filtered.loc[self.data_not_removed.id == event_id, "notes"] = note

        self.tab_handler.handle_data(self.data_filtered)
        self.config_manager.save_config()

    def _handle_removed_data_notes_edited(self, data: tuple):
        event_id = data[0]
        note = data[1]

        if note == "":
            self.config_manager.remove_note_if_exist(event_id)
        else:
            self.config_manager.update_note(event_id, note)
        self.data_removed.loc[self.data_removed.id == event_id, "notes"] = note

        self.tab_handler.handle_removed_data(self.data_removed)
        self.config_manager.save_config()

    @staticmethod
    def _remove_null_values_from_dict(d):
        return {k: v for k, v in d.items() if v != "" and pd.notnull(v)}
