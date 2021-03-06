import pandas as pd
from PyQt5.QtWidgets import QComboBox, QVBoxLayout, QHBoxLayout, QLabel

from src.data_processing.data_analysis import calculate_incomes_and_outcomes
from src.data_processing.data_filtering import filter_data
from src.gui.canvases.bar_canvas import BarCanvas
from src.gui.tabs.base_tab import BaseTab


class IndicatorsTab(BaseTab):
    grouping_options = {
        "Year": {"group_by": "Y", "format": "%Y"},
        "Month": {"group_by": "M", "format": "%Y-%m"},
        "Week": {"group_by": "W", "format": "%Y-%W"},
        "Day": {"group_by": "D", "format": "%Y-%m-%d"}
    }

    def __init__(self, indicators: dict):
        self.data = None
        self.indicator_values = None
        self.indicators_dict = indicators

        self.grouping_option_selector = QComboBox()
        self.grouping_option_selector.addItems(list(self.grouping_options.keys()))
        self._grouping_option_changed()

        self.indicator_selector = QComboBox()

        self.figure_value = BarCanvas(y_axis_title='Amount (EUR)')
        self.figure_cumulative = BarCanvas(y_axis_title='Cumulative amount (EUR)')

        self._add_indicator_options()

        super().__init__()

    def _set_layout(self):
        self.layout = QVBoxLayout()

        grouping_layout = QHBoxLayout()
        grouping_layout.addWidget(QLabel("Grouping"))
        grouping_layout.addWidget(self.grouping_option_selector)
        self.layout.addLayout(grouping_layout)

        indicator_layout = QHBoxLayout()
        indicator_layout.addWidget(QLabel("Indicator"))
        indicator_layout.addWidget(self.indicator_selector)
        self.layout.addLayout(indicator_layout)

        self.layout.addWidget(self.figure_value)
        self.layout.addWidget(self.figure_cumulative)

        self.setLayout(self.layout)

    def _set_connections(self):
        self.grouping_option_selector.currentIndexChanged.connect(self._grouping_option_changed)
        self.indicator_selector.currentIndexChanged.connect(self._indicator_option_changed)

    def _grouping_option_changed(self):
        option_text = self.grouping_option_selector.currentText()
        self.group_by = self.grouping_options[option_text]["group_by"]
        self.formatting = self.grouping_options[option_text]["format"]
        self._analyze_data_and_update_canvas()

    def _indicator_option_changed(self):
        self.current_indicator = self.indicator_selector.currentText()
        self.indicator_values = self.indicators_dict.get(self.current_indicator, None)
        self._analyze_data_and_update_canvas()

    def _add_indicator_options(self):
        self.indicator_selector.clear()
        self.indicator_selector.addItems(list(self.indicators_dict.keys()))
        self._indicator_option_changed()

    def update_indicators(self, indicators):
        self.indicators_dict = indicators
        self._add_indicator_options()

    def handle_data(self, data: pd.DataFrame):
        self.data = data
        self._analyze_data_and_update_canvas()

    def _analyze_data_and_update_canvas(self):
        if self.indicator_values is not None and self.data is not None:
            filtered_data = filter_data(self.data, **self.indicator_values)
            analysed_data = calculate_incomes_and_outcomes(filtered_data, self.group_by)
            self.figure_value.plot(analysed_data['total'],
                                   analysed_data.index.strftime(self.formatting).tolist())
            self.figure_cumulative.plot(analysed_data['total_cumulative'],
                                        analysed_data.index.strftime(self.formatting).tolist(),
                                        plot_average=False)
