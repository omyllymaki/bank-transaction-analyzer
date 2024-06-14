import logging
from datetime import datetime

import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QComboBox, QVBoxLayout, QHBoxLayout, QLabel

from src.data_processing.data_analysis import calculate_incomes_and_outcomes, yearly_analysis
from src.gui.canvases.line_canvas import LineCanvas
from src.gui.tabs.base_tab import BaseTab

logger = logging.getLogger(__name__)


class YearComparisonTab(BaseTab):
    output_options = ["income", "outcome", "total"]

    def __init__(self):
        self.data = None
        self.current_output_option = "income"
        self.line_canvas = LineCanvas(y_axis_title="Cumulative value (EUR)", x_axis_title="Day of year")
        self.output_selector = QComboBox()
        self.output_selector.addItems(self.output_options)
        self.year_selector = QComboBox()
        self.year_data = None

        super().__init__()

    def _set_layout(self):
        self.layout = QVBoxLayout()

        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output"))
        output_layout.addWidget(self.output_selector)
        self.layout.addLayout(output_layout)

        year_layout = QHBoxLayout()
        year_layout.addWidget(QLabel("Year"))
        year_layout.addWidget(self.year_selector)
        self.layout.addLayout(year_layout)

        self.layout.addWidget(self.line_canvas)
        self.setLayout(self.layout)

    def _set_connections(self):
        self.output_selector.currentIndexChanged.connect(self._update_canvas)
        self.year_selector.currentIndexChanged.connect(self._update_canvas)

    def handle_data(self, data: pd.DataFrame):
        self.data = data
        years = data.time.dt.year.unique().astype(str).tolist()
        self.year_selector.currentIndexChanged.disconnect(self._update_canvas)
        self.year_selector.clear()
        self.year_selector.addItems(years)
        if len(years) > 0:
            self.year_selector.setCurrentText(years[-1])
        self.year_selector.currentIndexChanged.connect(self._update_canvas)
        self._analyze_data_and_update_canvas()

    def _analyze_data_and_update_canvas(self):
        if self.data is not None:
            df = calculate_incomes_and_outcomes(self.data)
            target_year = self._get_target_year()
            self.year_data = yearly_analysis(df, forecast_year=target_year)
            self._update_canvas()

    def _update_canvas(self):
        self.line_canvas.clear()
        field = self.output_selector.currentText()

        target_year = self._get_target_year()
        if self.year_data is not None:
            for year, data in self.year_data.items():
                x = data.day_of_year.values
                y = data[field + "_cumulative"].values
                not_predicted = ~data.predicted
                predicted = data.predicted
                if year == target_year:
                    self.line_canvas.plot(x[not_predicted], y[not_predicted], "r-", linewidth=2)
                    self.line_canvas.plot(x[predicted], y[predicted], "r--", linewidth=2)
                else:
                    self.line_canvas.plot(x[not_predicted], y[not_predicted], "-", alpha=0.5, linewidth=1)
                self.line_canvas.text(x[not_predicted][-1] + 1, y[not_predicted][-1], year)

    def _get_target_year(self):
        target_year = None
        try:
            target_year = int(self.year_selector.currentText())
        except Exception as e:
            logger.warning(f"Cannot convert year selector value to int, error {e}")
        return target_year
