from datetime import datetime
from typing import List

import pandas as pd
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCalendarWidget, QLabel, QLineEdit, QPushButton, QFileDialog, \
    QInputDialog, QHBoxLayout

from src.config_manager import GENERAL_KEY, DROP_DATA_KEY
from src.data_processing.data_analysis import categorize, extract_labels
from src.data_processing.data_filtering import filter_data
from src.data_processing.data_preprocessing import DataPreprocessor
from src.gui.dialog_boxes import show_warning
from src.gui.widgets import FloatLineEdit, TextLineEdit
from src.utils import load_json, save_json


class SideBar(QWidget):
    data_loaded_signal = pyqtSignal(pd.DataFrame)
    data_filtered_signal = pyqtSignal(pd.DataFrame)
    new_category_created_signal = pyqtSignal(tuple)
    new_label_created_signal = pyqtSignal(tuple)

    def __init__(self, config):
        super().__init__()

        self.data_preprocessor = DataPreprocessor()
        self.config = config
        self.cleaned_data = None
        self.filtered_data = None
        self.min_value = None
        self.max_value = None
        self.min_value_is_valid = True
        self.max_value_is_valid = True
        self.is_data_loaded = False
        self.filter_values = None

        self.cleaned_data = None
        self.min_date_selector = QCalendarWidget(self)
        self.max_date_selector = QCalendarWidget(self)
        self.target_line = TextLineEdit(self)
        self.account_number_line = TextLineEdit(self)
        self.message_line = TextLineEdit(self)
        self.event_line = TextLineEdit(self)
        self.category_line = TextLineEdit(self)
        self.labels_line = TextLineEdit(self)
        self.id_line = TextLineEdit(self)
        self.notes_line = TextLineEdit(self)
        self.is_duplicate_line = QLineEdit(self)
        self.min_value_line = FloatLineEdit(self)
        self.max_value_line = FloatLineEdit(self)
        self.load_button = QPushButton('Load data')
        self.create_label_button = QPushButton('Create label from existing filters')
        self.create_category_button = QPushButton('Create category from existing filters')
        self._set_layout()
        self._set_connections()

    def set_config(self, config):
        self.config = config
        self.cleaned_data = self.data_preprocessor.update_notes_categories_labels(self.cleaned_data, self.config)

    def _create_hbox_with_text(self, text, widget):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(text, widget))
        layout.addWidget(widget)
        return layout

    def _set_layout(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel('Min date'))
        self.layout.addWidget(self.min_date_selector)
        self.layout.addWidget(QLabel('Max date'))
        self.layout.addWidget(self.max_date_selector)
        layout = QHBoxLayout()
        layout.addWidget(QLabel('Min value'))
        layout.addWidget(self.min_value_line)
        layout.addWidget(QLabel('Max value'))
        layout.addWidget(self.max_value_line)
        self.layout.addLayout(layout)

        hbox_widgets = [
            ("Target:", self.target_line),
            ("Account:", self.account_number_line),
            ("Message:", self.message_line),
            ("Event:", self.event_line),
            ("Category:", self.category_line),
            ("Labels:", self.labels_line),
            ("Id:", self.id_line),
            ("Notes:", self.notes_line),
            ("Is duplicate:", self.is_duplicate_line)
        ]
        for item in hbox_widgets:
            layout = self._create_hbox_with_text(item[0], item[1])
            self.layout.addLayout(layout)

        self.layout.addWidget(self.load_button)
        self.layout.addWidget(self.create_label_button)
        self.layout.addWidget(self.create_category_button)

    def _set_connections(self):
        self.load_button.clicked.connect(self._handle_load_button_clicked)
        self.create_label_button.clicked.connect(self._handle_create_new_label)
        self.create_category_button.clicked.connect(self._handle_create_new_category)
        self.min_value_line.textChanged.connect(self._handle_min_value_changed)
        self.max_value_line.textChanged.connect(self._handle_max_value_changed)

        self.min_date_selector.selectionChanged.connect(self._handle_filter_data)
        self.max_date_selector.selectionChanged.connect(self._handle_filter_data)
        self.min_value_line.returnPressed.connect(self._handle_filter_data)
        self.max_value_line.returnPressed.connect(self._handle_filter_data)
        self.target_line.returnPressed.connect(self._handle_filter_data)
        self.account_number_line.returnPressed.connect(self._handle_filter_data)
        self.message_line.returnPressed.connect(self._handle_filter_data)
        self.event_line.returnPressed.connect(self._handle_filter_data)
        self.category_line.returnPressed.connect(self._handle_filter_data)
        self.labels_line.returnPressed.connect(self._handle_filter_data)
        self.id_line.returnPressed.connect(self._handle_filter_data)
        self.notes_line.returnPressed.connect(self._handle_filter_data)
        self.is_duplicate_line.returnPressed.connect(self._handle_filter_data)

    def _handle_load_button_clicked(self):
        self.file_paths = self._get_file_paths()
        if not self.file_paths:
            return None
        self.load_data()

    def load_data(self):
        self.cleaned_data, removed_data = self.data_preprocessor.get_data(file_paths=self.file_paths,
                                                                          drop_data=self.config[DROP_DATA_KEY])
        self.cleaned_data = self.data_preprocessor.update_notes_categories_labels(self.cleaned_data, self.config)
        removed_data = self.data_preprocessor.update_notes_categories_labels(removed_data, self.config)
        self._set_dates_based_on_data()
        self.is_data_loaded = True
        self.data_loaded_signal.emit(removed_data)
        self._handle_filter_data()

    def _set_dates_based_on_data(self):
        datetime_min = self.cleaned_data.time.min()
        datetime_max = self.cleaned_data.time.max()
        self.min_date_selector.setSelectedDate(QtCore.QDate(datetime_min.year, datetime_min.month, datetime_min.day))
        self.max_date_selector.setSelectedDate(QtCore.QDate(datetime_max.year, datetime_max.month, datetime_max.day))

    def _update_filtering_values(self):
        self.filter_values = self._get_filter_values()

    def _get_filter_values(self):
        return dict(
            min_date=self._get_min_date(),
            max_date=self._get_max_date(),
            target=self.target_line.get_value(),
            account_number=self.account_number_line.get_value(),
            message=self.message_line.get_value(),
            event=self.event_line.get_value(),
            min_value=self.min_value,
            max_value=self.max_value,
            category=self.category_line.get_value(),
            labels=self.labels_line.get_value(),
            id=self.id_line.get_value(),
            notes=self.notes_line.get_value(),
            is_duplicate=self._get_is_duplicate()
        )

    def _handle_filter_data(self):
        self._update_filtering_values()
        if self.cleaned_data is not None:
            self.filtered_data = filter_data(self.cleaned_data, **self.filter_values)
            if self.filtered_data.empty:
                show_warning("Warning", "No data to analyze")
            else:
                self.data_filtered_signal.emit(self.filtered_data)

    def _update_categories(self):
        self.cleaned_data["categories"] = categorize(self.cleaned_data, self.config["categories"])
        self._handle_filter_data()

    def _update_labels(self):
        labels = extract_labels(self.cleaned_data, self.config["labels"])
        self.cleaned_data["labels"] = [" ; ".join(l) for l in labels]
        self._handle_filter_data()

    def _handle_create_new_label(self):
        name, ok = QInputDialog.getText(self, 'New label', 'Type the name of new label')
        if not ok:
            return
        new_label_data = self._get_cleaned_filter_values()
        self.new_label_created_signal.emit((name, new_label_data))

    def _handle_create_new_category(self):
        name, ok = QInputDialog.getText(self, 'New category', 'Type the name of new category')
        if not ok:
            return
        new_category_data = self._get_cleaned_filter_values()
        self.new_category_created_signal.emit((name, new_category_data))

    def _get_cleaned_filter_values(self):
        filter_values = self._get_filter_values()
        filter_values = {k: v for k, v in filter_values.items() if v != "" and pd.notnull(v)}
        filter_values.pop("min_date", None)
        filter_values.pop("max_date", None)
        return filter_values

    def _write_filtering_values_to_file(self, file_path, name):
        self._update_filtering_values()
        filter_values = {k: v for k, v in self.filter_values.items() if v != "" and pd.notnull(v)}
        filter_values.pop("min_date", None)
        filter_values.pop("max_date", None)
        values = load_json(file_path)
        values[name] = filter_values
        save_json(file_path, values)
        return values

    def _get_file_paths(self) -> List[str]:
        file_paths, _ = QFileDialog.getOpenFileNames(caption='Choose files for analysis',
                                                     directory=self.config[GENERAL_KEY]["default_data_dir"])
        return file_paths

    def _get_min_date(self) -> datetime:
        return self.min_date_selector.selectedDate().toPyDate()

    def _get_max_date(self) -> datetime:
        return self.max_date_selector.selectedDate().toPyDate()

    def _get_is_duplicate(self) -> bool:
        text = self.is_duplicate_line.text()
        if text == "True":
            return True
        elif text == "False":
            return False
        else:
            return None

    def _handle_min_value_changed(self):
        self.min_value, self.min_value_is_valid = self.min_value_line.get_value()

    def _handle_max_value_changed(self):
        self.max_value, self.max_value_is_valid = self.max_value_line.get_value()
