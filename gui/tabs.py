from typing import Dict

import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QRadioButton, QComboBox

from data_processing.data_analyzer import DataAnalyzer
from gui.canvases import IncomeAndOutcomeBarCanvas, IncomeAndOutcomeLineCanvas, ProfitBarCanvas, ProfitLineCanvas
from gui.dataframe_model import DataFrameModel

SHOW_COLUMNS = ["target", "account_number", "value", "time", "cumulative_income", "cumulative_outcome",
                "cumulative_value", "message"]


class TabHandler(QWidget):
    def __init__(self):
        super().__init__()

        self.content = QTabWidget()
        self.income_and_outcome = IncomeAndOutcomeTab()
        self.event_table = EventTableTab()
        self.content.addTab(self.income_and_outcome, 'Income/outcome')
        self.content.addTab(self.event_table, 'Events')
        self._set_layout()

    def _set_layout(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.content)

    def show_data(self, data: pd.DataFrame):
        self.income_and_outcome.show_data(data)
        self.event_table.show_data(data[SHOW_COLUMNS])


class IncomeAndOutcomeTab(QTabWidget):
    options = {
        "year": ["year"],
        "month": ["year", "month"],
        "day": ["year", "month", "day"]
    }

    def __init__(self):
        super().__init__()
        self.group_by = list(self.options.values())[0]
        self.analyser = DataAnalyzer()
        self.options_selector = QComboBox()
        self.options_selector.addItems(list(self.options.keys()))
        self.figure_income_and_outcome = IncomeAndOutcomeBarCanvas(figure_title='Income & Outcome',
                                                                   y_axis_title='Amount (EUR)')
        self.figure_profit = ProfitBarCanvas(figure_title='Profit',
                                             y_axis_title='Amount (EUR)')
        self._set_layout()
        self._set_connections()

    def _set_layout(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.options_selector)
        self.layout.addWidget(self.figure_income_and_outcome)
        self.layout.addWidget(self.figure_profit)
        self.setLayout(self.layout)

    def _set_connections(self):
        self.options_selector.currentIndexChanged.connect(self._option_changed)

    def _option_changed(self):
        option_text = self.options_selector.currentText()
        self.group_by = self.options[option_text]
        print(option_text)

    def show_data(self, data: pd.DataFrame):
        analysed_data = self.analyser.analyze_data(data, self.group_by)
        self.figure_income_and_outcome.plot(analysed_data['income'], analysed_data['outcome'], analysed_data.index)
        self.figure_profit.plot(analysed_data['total'], analysed_data.index)


class EventTableTab(QTabWidget):
    def __init__(self):
        super().__init__()
        self.table_view = QtWidgets.QTableView()
        self.table_view.setObjectName("tableView")
        self.group_by_target_button = QRadioButton("Group by target")
        self._set_layout()
        self._set_connections()
        self.group_by_target = False

    def _set_layout(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.group_by_target_button)
        self.layout.addWidget(self.table_view)
        self.setLayout(self.layout)

    def _set_connections(self):
        self.group_by_target_button.toggled.connect(self._handle_grouping_button_toggle)

    def _handle_grouping_button_toggle(self):
        if self.group_by_target_button.isChecked():
            self.group_by_target = True
        else:
            self.group_by_target = False

    def show_data(self, data):
        if self.group_by_target:
            grouped_data = data.groupby("target", as_index=False).sum()[["target", "value"]].sort_values("value")
            model = DataFrameModel(grouped_data)
        else:
            model = DataFrameModel(data)
        self.table_view.setModel(model)
