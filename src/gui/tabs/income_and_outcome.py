import pandas as pd
from PyQt5.QtWidgets import QComboBox, QVBoxLayout, QHBoxLayout, QLabel

from src.data_processing.data_analysis import calculate_incomes_and_outcomes
from src.gui.canvases.bar_canvas import BarCanvas
from src.gui.canvases.double_bar_canvas import DoubleBarCanvas
from src.gui.tabs.base_tab import BaseTab


class IncomeAndOutcomeTab(BaseTab):
    options = {
        "Year": {"group_by": "Y", "format": "%Y"},
        "Month": {"group_by": "M", "format": "%Y-%m"},
        "Week": {"group_by": "W", "format": "%Y-%W"},
        "Day": {"group_by": "D", "format": "%Y-%m-%d"}
    }

    def __init__(self):
        self.data = None
        self.option_text = None
        self.group_by = list(self.options.values())[0]["group_by"]
        self.formatting = list(self.options.values())[0]["format"]
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
        self.group_by = self.options[self.option_text]["group_by"]
        self.formatting = self.options[self.option_text]["format"]
        self._analyze_data_and_update_canvases()

    def handle_data(self, data: pd.DataFrame):
        self.data = data
        self._analyze_data_and_update_canvases()

    def _analyze_data_and_update_canvases(self):
        if self.data is not None:
            analysed_data = calculate_incomes_and_outcomes(self.data, self.group_by)
            self.figure_income_and_outcome.plot(analysed_data['income'],
                                                analysed_data['outcome'],
                                                analysed_data.index.strftime(self.formatting).tolist())
            self.figure_profit.plot(analysed_data['total'],
                                    analysed_data.index.strftime(self.formatting).tolist())
