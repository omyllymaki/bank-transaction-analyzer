import pandas as pd
from PyQt5.QtWidgets import QComboBox, QVBoxLayout, QHBoxLayout, QLabel

from data_processing.data_analyzer import DataAnalyzer
from gui.canvases import StackedBarsCanvas
from gui.tabs.base_tab import BaseTab
from gui.widgets import FloatLineEdit


class StackedBarsTab(BaseTab):
    output_options = ["income", "outcome"]
    grouping_options = {
        "Year": ["year"],
        "Month": ["year", "month"],
        "Week": ["year", "week"],
        "Day": ["year", "month", "day"],
    }

    def __init__(self):
        self.data = None
        self.group_by = ["year"]
        self.current_output_option = "income"

        self.analyzer = DataAnalyzer()
        self.canvas = StackedBarsCanvas(y_axis_title="Amount (EUR)")

        self.output_selector = QComboBox()
        self.output_selector.addItems(self.output_options)

        self.threshold_line = FloatLineEdit()
        self.threshold_line.setText("100")
        self.threshold_value = 100
        self.threshold_value_is_valid = True

        self.grouping_option_selector = QComboBox()
        self.grouping_option_selector.addItems(list(self.grouping_options.keys()))

        super().__init__()

    def _set_layout(self):
        self.layout = QVBoxLayout()

        grouping_layout = QHBoxLayout()
        grouping_layout.addWidget(QLabel("Grouping"))
        grouping_layout.addWidget(self.grouping_option_selector)

        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output"))
        output_layout.addWidget(self.output_selector)

        threshold_value_layout = QHBoxLayout()
        threshold_value_layout.addWidget(QLabel("Threshold"))
        threshold_value_layout.addWidget(self.threshold_line)

        self.layout.addLayout(grouping_layout)
        self.layout.addLayout(output_layout)
        self.layout.addLayout(threshold_value_layout)
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

    def _set_connections(self):
        self.grouping_option_selector.currentIndexChanged.connect(self._grouping_option_changed)
        self.output_selector.currentIndexChanged.connect(self._output_option_changed)
        self.threshold_line.returnPressed.connect(self._handle_threshold_value_changed)

    def _grouping_option_changed(self):
        option_text = self.grouping_option_selector.currentText()
        self.group_by = self.grouping_options[option_text]
        self._analyze_data_and_update_canvases()

    def _output_option_changed(self):
        self.current_output_option = self.output_selector.currentText()
        self._analyze_data_and_update_canvases()

    def _handle_threshold_value_changed(self):
        self.threshold_value, self.threshold_value_is_valid = self.threshold_line.get_value()
        self._analyze_data_and_update_canvases()

    def handle_data(self, data: pd.DataFrame):
        self.data = data
        self._analyze_data_and_update_canvases()

    def _analyze_data_and_update_canvases(self):
        if self.threshold_value_is_valid and self.data is not None:
            if self.current_output_option == "income":
                data_to_analyze = self.data[self.data.value > 0]
            else:
                data_to_analyze = self.data[self.data.value < 0]
                data_to_analyze["value"] = abs(data_to_analyze["value"])

            pivot_table = self.analyzer.calculate_pivot_table(data_to_analyze,
                                                              group_by=self.group_by,
                                                              threshold=self.threshold_value)

            if pivot_table.shape[0] > 0:
                self.canvas.plot(pivot_table)
            else:
                self.canvas.clear()
