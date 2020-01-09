from datetime import datetime
from typing import List

import pandas as pd
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCalendarWidget, QLabel, QLineEdit, QPushButton, QFileDialog

from config import DEFAULT_DATA_DIR
from data_analyzer import DataAnalyzer
from gui.dialog_boxes import show_warning
from load_and_clean_data import load_and_clean_data


class SideBar(QWidget):
    analyze_button_clicked = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.analyzer = DataAnalyzer()
        self.cleaned_data = pd.DataFrame()
        self.min_date_selector = QCalendarWidget(self)
        self.max_date_selector = QCalendarWidget(self)
        self.target_line = QLineEdit(self)
        self.account_number_line = QLineEdit(self)
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
        self.layout.addWidget(QLabel('Target contains'))
        self.layout.addWidget(self.target_line)
        self.layout.addWidget(QLabel('Account number contains'))
        self.layout.addWidget(self.account_number_line)
        self.layout.addWidget(self.analyze_button)
        self.layout.addWidget(self.load_button)

    def _set_connections(self):
        self.load_button.clicked.connect(self._handle_load_data)
        self.analyze_button.clicked.connect(self._handle_analyze_data)

    def _handle_load_data(self):
        file_paths = self._get_file_paths()
        if not file_paths:
            return None
        self.cleaned_data = load_and_clean_data(file_paths)
        self._set_dates_based_on_data()
        self.analyze_button.setDisabled(False)
        self._handle_analyze_data()

    def _set_dates_based_on_data(self):
        datetime_min = self.cleaned_data.time.min()
        datetime_max = self.cleaned_data.time.max()
        self.min_date_selector.setSelectedDate(QtCore.QDate(datetime_min.year, datetime_min.month, datetime_min.day))
        self.max_date_selector.setSelectedDate(QtCore.QDate(datetime_max.year, datetime_max.month, datetime_max.day))

    def _handle_analyze_data(self):
        analyzed_data = self.analyzer.analyze_data(self.cleaned_data,
                                                   min_date=self._get_min_date(),
                                                   max_date=self._get_max_date(),
                                                   target=self._get_target(),
                                                   account_number=self._get_account_number())
        if analyzed_data["by_event"].empty:
            show_warning("Warning", "No data to analyze")
        else:
            self.analyze_button_clicked.emit(analyzed_data)

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
