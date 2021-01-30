import pandas as pd
from PyQt5.QtWidgets import QComboBox, QVBoxLayout, QHBoxLayout, QLabel

from data_processing.data_analyzer import DataAnalyzer
from gui.canvases import DoubleBarCanvas, BarCanvas
from gui.tabs.base_tab import BaseTab


class IncomeAndOutcomeTab(BaseTab):
    options = {
        "Year": ["year"],
        "Month": ["year", "month"],
        "Week": ["year", "week"],
        "Day": ["year", "month", "day"],
    }

    def __init__(self):
        self.data = None
        self.option_text = None
        self.group_by = list(self.options.values())[0]
        self.analyser = DataAnalyzer()
        self.grouping_option_selector = QComboBox()
        self.grouping_option_selector.addItems(list(self.options.keys()))
        self.figure_income_and_outcome = DoubleBarCanvas(figure_title='Income & Outcome',
                                                         y_axis_title='Amount (EUR)',
                                                         y1_label="Income",
                                                         y2_label="Outcome")
        self.figure_profit = BarCanvas(figure_title='Profit',
                                       y_axis_title='Amount (EUR)')

        super().__init__()

    def _set_layout(self):
        self.layout = QVBoxLayout()

        grouping_layout = QHBoxLayout()
        grouping_layout.addWidget(QLabel("Grouping"))
        grouping_layout.addWidget(self.grouping_option_selector)

        self.layout.addLayout(grouping_layout)
        self.layout.addWidget(self.figure_income_and_outcome)
        self.layout.addWidget(self.figure_profit)
        self.setLayout(self.layout)

    def _set_connections(self):
        self.grouping_option_selector.currentIndexChanged.connect(self._option_changed)

    def _option_changed(self):
        self.option_text = self.grouping_option_selector.currentText()
        self.group_by = self.options[self.option_text]
        self._analyze_data_and_update_canvases()

    def handle_data(self, data: pd.DataFrame):
        self.data = data
        self._analyze_data_and_update_canvases()

    def _analyze_data_and_update_canvases(self):
        if self.data is not None:
            analysed_data = self.analyser.calculate_incomes_and_outcomes(self.data, self.group_by)
            self.figure_income_and_outcome.plot(analysed_data['income'],
                                                analysed_data['outcome'],
                                                analysed_data.index.tolist())
            self.figure_profit.plot(analysed_data['total'], analysed_data.index.tolist())
