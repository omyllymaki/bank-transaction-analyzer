import pandas as pd
from PyQt5.QtWidgets import QWidget, QHBoxLayout

from src.config_manager import GENERAL_KEY, DROP_DATA_KEY, CATEGORIES_KEY, LABELS_KEY
from src.data_processing.data_filtering import filter_data
from src.data_processing.data_preprocessing import DataPreprocessor
from src.gui.sidebar import SideBar
from src.gui.tabs.tab_handler import TabHandler


class MainView(QWidget):
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.data_processor = DataPreprocessor()
        self.all_data = None
        self.data = None
        self.removed_data = None
        self.filtered_data = None

        self.tab_handler = TabHandler()
        self.sidebar = SideBar(self.config_manager.get_config()[GENERAL_KEY]["default_data_dir"])
        self._set_layout()
        self._set_connections()

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
        self.all_data = self.data_processor.get_data(file_paths)
        config = self.config_manager.get_config()
        self.data_processor.update_extra_columns(self.all_data, config)
        self.data, self.removed_data = self.data_processor.drop_data(self.all_data, config[DROP_DATA_KEY])
        self.filtered_data = self.data.copy()
        self.tab_handler.handle_data(self.filtered_data)
        self.tab_handler.handle_removed_data(self.removed_data)

        datetime_min = self.data.time.min()
        datetime_max = self.data.time.max()
        self.sidebar.set_dates(datetime_min, datetime_max)

    def _handle_filtered_data_changed(self, filter_values):
        filter_values_nulls_removed = self._remove_null_values_from_dict(filter_values)
        self.filtered_data = filter_data(self.data, **filter_values_nulls_removed)
        self.tab_handler.handle_data(self.filtered_data)

    def _handle_drop_data_added(self, data: tuple):
        name = data[0]
        value = data[1]
        self.config_manager.add_drop_data(name, value)

        config = self.config_manager.get_config()
        self.data_processor.update_extra_columns(self.all_data, config)
        drop_data = config[DROP_DATA_KEY]
        self.data, self.removed_data = self.data_processor.drop_data(self.all_data, drop_data)
        current_filter_values = self.sidebar.get_filter_values()
        filter_values_nulls_removed = self._remove_null_values_from_dict(current_filter_values)
        self.filtered_data = filter_data(self.data, **filter_values_nulls_removed)

        self.tab_handler.handle_data(self.filtered_data)
        self.tab_handler.handle_removed_data(self.removed_data)
        self.config_manager.save_config()

    def _handle_new_category_created(self, data: tuple):
        name = data[0]
        filter_values = data[1]
        filter_values_nulls_removed = self._remove_null_values_from_dict(filter_values)
        filter_values_nulls_removed.pop("min_date")
        filter_values_nulls_removed.pop("max_date")
        self.config_manager.add_category(name, filter_values_nulls_removed)
        categories = self.config_manager.get_config()[CATEGORIES_KEY]
        self.data_processor.add_categories(self.filtered_data, categories)
        self.data_processor.add_categories(self.data, categories)
        self.data_processor.add_categories(self.removed_data, categories)
        self.tab_handler.handle_data(self.filtered_data)
        self.tab_handler.handle_removed_data(self.removed_data)
        self.config_manager.save_config()

    def _handle_new_label_created(self, data: tuple):
        name = data[0]
        filter_values = data[1]
        filter_values_nulls_removed = self._remove_null_values_from_dict(filter_values)
        filter_values_nulls_removed.pop("min_date")
        filter_values_nulls_removed.pop("max_date")
        self.config_manager.add_label(name, filter_values_nulls_removed)
        labels = self.config_manager.get_config()[LABELS_KEY]
        self.data_processor.add_labels(self.filtered_data, labels)
        self.data_processor.add_labels(self.data, labels)
        self.data_processor.add_labels(self.removed_data, labels)
        self.tab_handler.handle_data(self.filtered_data)
        self.tab_handler.handle_removed_data(self.removed_data)
        self.config_manager.save_config()

    def _handle_filtered_data_notes_edited(self, data: tuple):
        event_id = data[0]
        note = data[1]
        if note == "":
            self.config_manager.remove_note_if_exist(event_id)
        else:
            self.config_manager.update_note(event_id, note)
        self.data.loc[self.data.id == event_id, "notes"] = note
        self.filtered_data.loc[self.data.id == event_id, "notes"] = note
        self.tab_handler.handle_data(self.filtered_data)
        self.config_manager.save_config()

    def _handle_removed_data_notes_edited(self, data: tuple):
        event_id = data[0]
        note = data[1]
        if note == "":
            self.config_manager.remove_note_if_exist(event_id)
        else:
            self.config_manager.update_note(event_id, note)
        self.removed_data.loc[self.removed_data.id == event_id, "notes"] = note
        self.tab_handler.handle_removed_data(self.removed_data)
        self.config_manager.save_config()

    @staticmethod
    def _remove_null_values_from_dict(d):
        return {k: v for k, v in d.items() if v != "" and pd.notnull(v)}
