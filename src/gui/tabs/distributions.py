import pandas as pd
import numpy as np
from PyQt5.QtWidgets import QComboBox, QVBoxLayout, QHBoxLayout, QLabel

from src.data_processing.data_analyzer import DataAnalyzer
from src.gui.canvases.pie_canvas import PieCanvas
from src.gui.canvases.stacked_bar_canvas import StackedBarsCanvas
from src.gui.tabs.base_tab import BaseTab
from src.gui.widgets import FloatLineEdit


class DistributionsTab(BaseTab):
    output_options = ["income", "outcome"]
    time_grouping_options = {
        "Year": ["year"],
        "Month": ["year", "month"],
        "Week": ["year", "week"],
        "Day": ["year", "month", "day"],
    }
    column_grouping_options = {
        "Target": "target",
        "Category": "category",
    }

    def __init__(self):
        self.data = None
        self.time_group_by = ["year"]
        self.column_group_by = "target"
        self.current_output_option = "income"

        self.analyzer = DataAnalyzer()
        self.bar_canvas = StackedBarsCanvas(y_axis_title="Amount (EUR)")
        self.pie_canvas = PieCanvas(threshold=0.01)

        self.output_selector = QComboBox()
        self.output_selector.addItems(self.output_options)

        self.threshold_line = FloatLineEdit()
        self.threshold_line.setText("100")
        self.threshold_value = 100
        self.threshold_value_is_valid = True

        self.time_grouping_selector = QComboBox()
        self.time_grouping_selector.addItems(list(self.time_grouping_options.keys()))

        self.column_grouping_selector = QComboBox()
        self.column_grouping_selector.addItems(list(self.column_grouping_options.keys()))

        super().__init__()

    def _set_layout(self):
        self.layout = QVBoxLayout()

        grouping_layout = QHBoxLayout()
        grouping_layout.addWidget(QLabel("Grouping"))
        grouping_layout.addWidget(self.time_grouping_selector)
        grouping_layout.addWidget(self.column_grouping_selector)

        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output"))
        output_layout.addWidget(self.output_selector)

        threshold_value_layout = QHBoxLayout()
        threshold_value_layout.addWidget(QLabel("Threshold"))
        threshold_value_layout.addWidget(self.threshold_line)

        figures_layout = QHBoxLayout()
        figures_layout.addWidget(self.bar_canvas)
        figures_layout.addWidget(self.pie_canvas)

        self.layout.addLayout(grouping_layout)
        self.layout.addLayout(output_layout)
        self.layout.addLayout(threshold_value_layout)
        self.layout.addLayout(figures_layout)

        self.setLayout(self.layout)

    def _set_connections(self):
        self.time_grouping_selector.currentIndexChanged.connect(self._time_grouping_option_changed)
        self.column_grouping_selector.currentIndexChanged.connect(self._column_grouping_option_changed)
        self.output_selector.currentIndexChanged.connect(self._output_option_changed)
        self.threshold_line.returnPressed.connect(self._handle_threshold_value_changed)
        self.bar_canvas.data_selected_signal.connect(self._handle_pie_plotting)

    def _time_grouping_option_changed(self):
        option_text = self.time_grouping_selector.currentText()
        self.time_group_by = self.time_grouping_options[option_text]
        self._analyze_data_and_update_canvases()

    def _column_grouping_option_changed(self):
        option_text = self.column_grouping_selector.currentText()
        self.column_group_by = self.column_grouping_options[option_text]
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
                                                              group_by=self.time_group_by,
                                                              columns=self.column_group_by,
                                                              threshold=self.threshold_value)

            if pivot_table.shape[0] > 0:
                self.bar_canvas.plot(pivot_table)
            else:
                self.bar_canvas.clear()

    def _handle_pie_plotting(self, data):
        df, colors = data
        self.pie_canvas.figure_title = df.name
        self.pie_canvas.plot(df.values/df.sum(), df.index, colors=np.array(colors))