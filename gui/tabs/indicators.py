import pandas as pd
from PyQt5.QtWidgets import QComboBox, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog

from data_processing.data_analyzer import DataAnalyzer
from data_processing.data_filtering import DataFilter
from gui.canvases import BarCanvas
from gui.tabs.base_tab import BaseTab


class IndicatorsTab(BaseTab):
    grouping_options = {
        "Year": ["year"],
        "Month": ["year", "month"],
        "Week": ["year", "week"],
        "Day": ["year", "month", "day"]
    }

    def __init__(self):

        self.data = None
        self.indicator_values = None
        self.indicators_dict = {}
        self.analyser = DataAnalyzer()
        self.filter = DataFilter()

        self.grouping_option_selector = QComboBox()
        self.grouping_option_selector.addItems(list(self.grouping_options.keys()))
        self._grouping_option_changed()

        self.indicator_selector = QComboBox()

        self.load_button = QPushButton('Load indicators')

        self.figure_value = BarCanvas(y_axis_title='Amount (EUR)')
        self.figure_cumulative = BarCanvas(y_axis_title='Cumulative amount (EUR)')

        super().__init__()

    def _set_layout(self):
        self.layout = QVBoxLayout()

        self.layout.addWidget(self.load_button)

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
        self.load_button.clicked.connect(self._handle_load_indicators)

    def _grouping_option_changed(self):
        option_text = self.grouping_option_selector.currentText()
        self.group_by = self.grouping_options[option_text]
        self._analyze_data_and_update_canvas()

    def _indicator_option_changed(self):
        self.current_indicator = self.indicator_selector.currentText()
        self.indicator_values = self.indicators_dict.get(self.current_indicator, None)
        self._analyze_data_and_update_canvas()

    def _handle_load_indicators(self):
        file_path, _ = QFileDialog.getOpenFileName(caption='Choose indicators file for analysis', directory=".")
        if not file_path:
            return None
        indicators = pd.read_csv(file_path)
        indicators = indicators.where(pd.notnull(indicators), None)
        indicators.set_index("name", inplace=True)
        self.indicators_dict = indicators.to_dict("index")
        self.indicator_selector.clear()
        self.indicator_selector.addItems(list(self.indicators_dict.keys()))
        self._indicator_option_changed()

    def handle_data(self, data: pd.DataFrame):
        self.data = data
        self._analyze_data_and_update_canvas()

    def _analyze_data_and_update_canvas(self):
        if self.indicator_values is not None and self.data is not None:
            filtered_data = self.filter.filter(self.data,
                                               min_value=self.indicator_values["min_value"],
                                               max_value=self.indicator_values["max_value"],
                                               target=self.indicator_values["target"],
                                               message=self.indicator_values["message"],
                                               account_number=self.indicator_values["account_number"],
                                               event=self.indicator_values["event"])
            analysed_data = self.analyser.calculate_incomes_and_outcomes(filtered_data, self.group_by)
            self.figure_value.plot(analysed_data['total'], analysed_data.index.tolist())
            self.figure_cumulative.plot(analysed_data['total_cumulative'],
                                        analysed_data.index.tolist(),
                                        plot_average=False)
