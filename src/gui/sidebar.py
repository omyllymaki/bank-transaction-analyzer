from datetime import datetime
from typing import List

import pandas as pd
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCalendarWidget, QLabel, QLineEdit, QPushButton, QFileDialog, \
    QInputDialog

from src.data_processing.bank_selection import get_bank
from src.data_processing.data_filtering import DataFilter
from src.data_processing.prepare_data import prepare_data
from src.gui.dialog_boxes import show_warning
from src.gui.widgets import FloatLineEdit


class SideBar(QWidget):
    analyze_button_clicked = pyqtSignal(pd.DataFrame)
    new_indicator_created = pyqtSignal()

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

        self.filter = DataFilter()
        self.cleaned_data = pd.DataFrame()
        self.min_date_selector = QCalendarWidget(self)
        self.max_date_selector = QCalendarWidget(self)
        self.target_line = QLineEdit(self)
        self.account_number_line = QLineEdit(self)
        self.message_line = QLineEdit(self)
        self.event_line = QLineEdit(self)
        self.min_value_line = FloatLineEdit(self)
        self.max_value_line = FloatLineEdit(self)
        self.filter_button = QPushButton('Filter data')
        self.load_button = QPushButton('Load data')
        self.create_indicator_button = QPushButton('Create indicator from existing filters')
        self.filter_button.setDisabled(True)
        self.create_indicator_button.setDisabled(True)
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
        self.layout.addWidget(QLabel('Event contains (regexp pattern)'))
        self.layout.addWidget(self.event_line)
        self.layout.addWidget(self.load_button)
        self.layout.addWidget(self.filter_button)
        self.layout.addWidget(self.create_indicator_button)

    def _set_connections(self):
        self.load_button.clicked.connect(self._handle_load_data)
        self.filter_button.clicked.connect(self._handle_filter_data)
        self.create_indicator_button.clicked.connect(self._handle_create_new_indicator)
        self.min_value_line.textChanged.connect(self._handle_min_value_changed)
        self.max_value_line.textChanged.connect(self._handle_max_value_changed)

    def _handle_load_data(self):
        file_paths = self._get_file_paths()
        if not file_paths:
            return None

        bank = get_bank(self.config["bank"])
        self.cleaned_data = prepare_data(file_paths=file_paths,
                                         data_loader=bank.loader,
                                         data_transformer=bank.transformer,
                                         drop_data=self.config["drop_data"])
        self._set_dates_based_on_data()
        self.is_data_loaded = True
        self._set_analyse_button_disabled_or_enabled()
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
            max_value=self.max_value
        )

    def _handle_filter_data(self):
        self._update_filtering_values()
        self.filtered_data = self.filter.filter(self.cleaned_data, **self.filter_values)
        if self.filtered_data.empty:
            show_warning("Warning", "No data to analyze")
        else:
            self.analyze_button_clicked.emit(self.filtered_data)
        self.create_indicator_button.setDisabled(False)

    def _handle_create_new_indicator(self):
        self._update_filtering_values()
        indicator_name, ok = QInputDialog.getText(self, 'New indicator', 'Type the name of new indicator')
        if not ok:
            return
        try:
            filter_values = self.filter_values.copy()
            filter_values.pop("min_date")
            filter_values.pop("max_date")
            filter_values["name"] = indicator_name
            df_indicators = pd.read_csv(self.config["indicators"])
            df_indicators = df_indicators.append(filter_values, ignore_index=True)
            df_indicators.to_csv(self.config["indicators"], index=False)
            self.new_indicator_created.emit()
        except Exception as e:
            print(e)
            show_warning("Indicator creation failure", "Something went wrong")

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

    def _handle_min_value_changed(self):
        self.min_value, self.min_value_is_valid = self.min_value_line.get_value()
        self._set_analyse_button_disabled_or_enabled()

    def _handle_max_value_changed(self):
        self.max_value, self.max_value_is_valid = self.max_value_line.get_value()
        self._set_analyse_button_disabled_or_enabled()

    def _set_analyse_button_disabled_or_enabled(self):
        if self.max_value_is_valid and self.min_value_is_valid and self.is_data_loaded:
            self.filter_button.setDisabled(False)
        else:
            self.filter_button.setDisabled(True)
