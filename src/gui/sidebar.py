from datetime import datetime
from typing import List

import pandas as pd
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCalendarWidget, QLabel, QLineEdit, QPushButton, QFileDialog, \
    QInputDialog, QHBoxLayout

from src.data_processing.bank_selection import get_bank
from src.data_processing.data_analysis import categorize
from src.data_processing.data_filtering import filter_data
from src.data_processing.loaders.new_nordea_loader import NewNordeaLoader
from src.data_processing.prepare_data import prepare_data
from src.data_processing.transformers.new_nordea_transformer import NewNordeaTransformer
from src.gui.dialog_boxes import show_warning
from src.gui.widgets import FloatLineEdit
from src.utils import load_json, save_json


class SideBar(QWidget):
    data_filtered_signal = pyqtSignal(pd.DataFrame)
    new_indicator_created_signal = pyqtSignal()

    def __init__(self, config):
        super().__init__()

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
        self.target_line = QLineEdit(self)
        self.account_number_line = QLineEdit(self)
        self.message_line = QLineEdit(self)
        self.event_line = QLineEdit(self)
        self.category_line = QLineEdit(self)
        self.min_value_line = FloatLineEdit(self)
        self.max_value_line = FloatLineEdit(self)
        self.load_button = QPushButton('Load data')
        self.create_indicator_button = QPushButton('Create indicator from existing filters')
        self.create_category_button = QPushButton('Create category from existing filters')
        self._set_layout()
        self._set_connections()

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
        self.layout.addWidget(QLabel('Target contains (regexp pattern)'))
        self.layout.addWidget(self.target_line)
        self.layout.addWidget(QLabel('Account number contains (regexp pattern)'))
        self.layout.addWidget(self.account_number_line)
        self.layout.addWidget(QLabel('Message contains (regexp pattern)'))
        self.layout.addWidget(self.message_line)
        self.layout.addWidget(QLabel('Event contains (regexp pattern)'))
        self.layout.addWidget(self.event_line)
        self.layout.addWidget(QLabel('Category contains (regexp pattern)'))
        self.layout.addWidget(self.category_line)
        self.layout.addWidget(self.load_button)
        self.layout.addWidget(self.create_indicator_button)
        self.layout.addWidget(self.create_category_button)

    def _set_connections(self):
        self.load_button.clicked.connect(self._handle_load_button_clicked)
        self.create_indicator_button.clicked.connect(self._handle_create_new_indicator)
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

    def _handle_load_button_clicked(self):
        self.file_paths = self._get_file_paths()
        if not self.file_paths:
            return None
        self.load_data()

    def load_data(self):
        self.cleaned_data = prepare_data(file_paths=self.file_paths,
                                         drop_data=self.config["drop_data"],
                                         categories=self.config["categories"])
        self._set_dates_based_on_data()
        self.is_data_loaded = True
        self._handle_filter_data()

    def _set_dates_based_on_data(self):
        datetime_min = self.cleaned_data.time.min()
        datetime_max = self.cleaned_data.time.max()
        self.min_date_selector.setSelectedDate(QtCore.QDate(datetime_min.year, datetime_min.month, datetime_min.day))
        self.max_date_selector.setSelectedDate(QtCore.QDate(datetime_max.year, datetime_max.month, datetime_max.day))

    def _update_filtering_values(self):
        self.filter_values = dict(
            min_date=self._get_min_date(),
            max_date=self._get_max_date(),
            target=self._get_target(),
            account_number=self._get_account_number(),
            message=self._get_message(),
            event=self._get_event(),
            min_value=self.min_value,
            max_value=self.max_value,
            category=self._get_category()
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

    def _handle_create_new_indicator(self):
        name, ok = QInputDialog.getText(self, 'New indicator', 'Type the name of new indicator')
        if not ok:
            return
        try:
            new_indicators = self._write_filtering_values_to_file(self.config["paths"]["indicators"], name)
            self.config["indicators"] = new_indicators
            self.new_indicator_created_signal.emit()
        except Exception as e:
            print(e)
            show_warning("Indicator creation failure", "Something went wrong")

    def _handle_create_new_category(self):
        name, ok = QInputDialog.getText(self, 'New category', 'Type the name of new category')
        if not ok:
            return
        try:
            new_categories = self._write_filtering_values_to_file(self.config["paths"]["categories"], name)
            self.config["categories"] = new_categories
            self._update_categories()
        except Exception as e:
            print(e)
            show_warning("Category creation failure", "Something went wrong")

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
                                                     directory=self.config["default_data_dir"])
        return file_paths

    def _get_min_date(self) -> datetime:
        return self.min_date_selector.selectedDate().toPyDate()

    def _get_max_date(self) -> datetime:
        return self.max_date_selector.selectedDate().toPyDate()

    def _get_target(self) -> str:
        return self.target_line.text()

    def _get_account_number(self) -> str:
        return self.account_number_line.text()

    def _get_message(self) -> str:
        return self.message_line.text()

    def _get_event(self) -> str:
        return self.event_line.text()

    def _get_category(self) -> str:
        return self.category_line.text()

    def _handle_min_value_changed(self):
        self.min_value, self.min_value_is_valid = self.min_value_line.get_value()

    def _handle_max_value_changed(self):
        self.max_value, self.max_value_is_valid = self.max_value_line.get_value()
