import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QComboBox, QVBoxLayout, QHBoxLayout, QLabel

from src.data_processing.data_analysis import calculate_incomes_and_outcomes, yearly_analysis, \
    estimate_year
from src.gui.canvases.line_canvas import LineCanvas
from src.gui.tabs.base_tab import BaseTab


class YearComparisonTab(BaseTab):
    output_options = ["income", "outcome", "total"]

    def __init__(self):
        self.data = None
        self.current_output_option = "income"

        self.line_canvas = LineCanvas(y_axis_title="Cumulative value (EUR)", x_axis_title="Day of year")

        self.output_selector = QComboBox()
        self.output_selector.addItems(self.output_options)

        super().__init__()

    def _set_layout(self):
        self.layout = QVBoxLayout()

        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output"))
        output_layout.addWidget(self.output_selector)
        self.layout.addLayout(output_layout)
        self.layout.addWidget(self.line_canvas)
        self.setLayout(self.layout)

    def _set_connections(self):
        self.output_selector.currentIndexChanged.connect(self._output_option_changed)

    def _output_option_changed(self):
        self.current_output_option = self.output_selector.currentText()
        self._analyze_data_and_update_canvases()

    def handle_data(self, data: pd.DataFrame):
        self.data = data
        self._analyze_data_and_update_canvases()

    def _analyze_data_and_update_canvases(self):
        if self.data is not None:
            self.line_canvas.clear()
            if self.data.shape[0] == 0:
                return
            field = self.current_output_option
            df = calculate_incomes_and_outcomes(self.data)
            output = yearly_analysis(df)
            year_largest = np.max(list(output.keys()))
            for year, data in output.items():
                x = data.day_of_year.values
                y = data[field + "_cumulative"].values
                if year == year_largest:
                    self.line_canvas.plot(x, y, "r-", linewidth=2)
                    xp, yp = estimate_year(data, field)
                    self.line_canvas.plot(xp, yp, "r--", linewidth=2)
                    self.line_canvas.text(xp[-1] + 1, yp[-1], f"{year} predicted")
                else:
                    self.line_canvas.plot(x, y, "-", alpha=0.5, linewidth=1)
                self.line_canvas.text(x[-1] + 1, y[-1], year)
