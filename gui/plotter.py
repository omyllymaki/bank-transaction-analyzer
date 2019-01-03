from typing import Dict

import pandas as pd
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout

from gui.figures import BarPlotCanvas, LinePlotCanvas


class Plotter(QWidget):
    def __init__(self):
        super().__init__()

        self.content = QTabWidget()
        self.figure_yearly_data = BarPlotCanvas('Income & Outcome per year', 'Year', 'Amount (EUR)')
        self.figure_monthly_data = BarPlotCanvas('Income & Outcome per month', '(Year, Month)', 'Amount (EUR)')
        self.figure_daily_data = LinePlotCanvas('Income & Outcome', 'Time', 'Amount (EUR)')
        self.content.addTab(self.figure_yearly_data, 'By year')
        self.content.addTab(self.figure_monthly_data, 'By month')
        self.content.addTab(self.figure_daily_data, 'By day')
        self._set_layout()

    def _set_layout(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.content)

    def plot_data(self, data: Dict[str, pd.DataFrame]):
        self.figure_yearly_data.plot(data['by_year'])
        self.figure_monthly_data.plot(data['by_year_and_month'])
        self.figure_daily_data.plot(data['by_event'])

