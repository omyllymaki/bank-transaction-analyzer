from datetime import datetime
from typing import List

import pandas as pd
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCalendarWidget, QLabel, QLineEdit, QPushButton, QFileDialog

from config import DEFAULT_DATA_DIR, DROP_DATA
from data_processing.data_filtering import DataFilter
from data_processing.load_clean_prefilter_data import load_clean_and_prefilter_data
from gui.widgets import FloatLineEdit
from gui.dialog_boxes import show_warning


class SideBar(QWidget):
    analyze_button_clicked = pyqtSignal(pd.DataFrame)

    def __init__(self):
        super().__init__()

        self.cleaned_data = None
        self.filtered_data = None
        self.min_value = None
        self.max_value = None
        self.min_value_is_valid = True
        self.max_value_is_valid = True
        self.is_data_loaded = False

        self.filter = DataFilter()
        self.cleaned_data = pd.DataFrame()
        self.min_date_selector = QCalendarWidget(self)
        self.max_date_selector = QCalendarWidget(self)
        self.target_line = QLineEdit(self)
        self.account_number_line = QLineEdit(self)
        self.message_line = QLineEdit(self)
        self.min_value_line = FloatLineEdit(self)
        self.max_value_line = FloatLineEdit(self)
        self.analyze_button = QPushButton('Analyze data')
        self.load_button = QPushButton('Load data')
        self.analyze_button.setDisabled(True)
        self._set_layout()
        self._set_connections()

    def _set_layout(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel('Min date'))
        self.layout.addWidget(self.min_date_selector)
        self.layout.addWidget(QLabel('Max date'))
        self.layout.addWidget(self.max_date_selector)
        self.layout.addWidget(QLabel('Min value'))
        self.layout.addWidget(self.min_value_line)
        self.layout.addWidget(QLabel('Max value'))
        self.layout.addWidget(self.max_value_line)
        self.layout.addWidget(QLabel('Target contains (regexp pattern)'))
        self.layout.addWidget(self.target_line)
        self.layout.addWidget(QLabel('Account number contains (regexp pattern)'))
        self.layout.addWidget(self.account_number_line)
        self.layout.addWidget(QLabel('Message contains (regexp pattern)'))
        self.layout.addWidget(self.message_line)
        self.layout.addWidget(self.analyze_button)
        self.layout.addWidget(self.load_button)

    def _set_connections(self):
        self.load_button.clicked.connect(self._handle_load_data)
        self.analyze_button.clicked.connect(self._handle_analyze_data)
        self.min_value_line.textChanged.connect(self._handle_min_value_changed)
        self.max_value_line.textChanged.connect(self._handle_max_value_changed)

    def _handle_load_data(self):
        file_paths = self._get_file_paths()
        if not file_paths:
            return None
        self.cleaned_data = load_clean_and_prefilter_data(file_paths, DROP_DATA)
        self._set_dates_based_on_data()
        self.is_data_loaded = True
        self._set_analyse_button_disabled_or_enabled()

    def _set_dates_based_on_data(self):
        datetime_min = self.cleaned_data.time.min()
        datetime_max = self.cleaned_data.time.max()
        self.min_date_selector.setSelectedDate(QtCore.QDate(datetime_min.year, datetime_min.month, datetime_min.day))
        self.max_date_selector.setSelectedDate(QtCore.QDate(datetime_max.year, datetime_max.month, datetime_max.day))

    def _handle_analyze_data(self):
        self.filtered_data = self.filter.filter(self.cleaned_data,
                                                min_date=self._get_min_date(),
                                                max_date=self._get_max_date(),
                                                target=self._get_target(),
                                                account_number=self._get_account_number(),
                                                message=self._get_message(),
                                                min_value=self.min_value,
                                                max_value=self.max_value
                                                )
        if self.filtered_data.empty:
            show_warning("Warning", "No data to analyze")
        else:
            self.analyze_button_clicked.emit(self.filtered_data)

    def _get_file_paths(self) -> List[str]:
        file_paths, _ = QFileDialog.getOpenFileNames(caption='Choose files for analysis', directory=DEFAULT_DATA_DIR)
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

    def _handle_min_value_changed(self):
        self.min_value, self.min_value_is_valid = self.min_value_line.get_value()
        self._set_analyse_button_disabled_or_enabled()

    def _handle_max_value_changed(self):
        self.max_value, self.max_value_is_valid = self.max_value_line.get_value()
        self._set_analyse_button_disabled_or_enabled()

    def _set_analyse_button_disabled_or_enabled(self):
        if self.max_value_is_valid and self.min_value_is_valid and self.is_data_loaded:
            self.analyze_button.setDisabled(False)
        else:
            self.analyze_button.setDisabled(True)
