from typing import Dict

import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout

from gui.canvases import IncomeAndOutcomeBarCanvas, IncomeAndOutcomeLineCanvas, ProfitBarCanvas, ProfitLineCanvas
from gui.dataframe_model import DataFrameModel

SHOW_COLUMNS = ["target", "account_number", "value", "time", "cumulative_income", "cumulative_outcome",
                "cumulative_value", "message"]


class Plotter(QWidget):
    def __init__(self):
        super().__init__()

        self.content = QTabWidget()
        self.figure_yearly_data = YearlyFigure()
        self.figure_monthly_data = MonthlyFigure()
        self.figure_daily_data = DailyFigure()
        self.event_table = EventTable()
        self.content.addTab(self.figure_yearly_data, 'By year')
        self.content.addTab(self.figure_monthly_data, 'By month')
        self.content.addTab(self.figure_daily_data, 'By day')
        self.content.addTab(self.event_table, 'Events')
        self._set_layout()

    def _set_layout(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.content)

    def show_data(self, data: Dict[str, pd.DataFrame]):
        self.figure_yearly_data.show_data(data['by_year'])
        self.figure_monthly_data.show_data(data['by_year_and_month'])
        self.figure_daily_data.show_data(data['by_event'])
        self.event_table.show_data(data['by_event'][SHOW_COLUMNS])


class YearlyFigure(QTabWidget):
    def __init__(self):
        super().__init__()
        self.figure_income_and_outcome = IncomeAndOutcomeBarCanvas('Income & Outcome per year', '', 'Amount (EUR)')
        self.figure_profit = ProfitBarCanvas('Profit', 'Year', 'Amount (EUR)')
        self._set_layout()

    def _set_layout(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.figure_income_and_outcome)
        self.layout.addWidget(self.figure_profit)
        self.setLayout(self.layout)

    def show_data(self, data: pd.DataFrame):
        self.figure_income_and_outcome.plot(data['income'], data['outcome'])
        self.figure_profit.plot(data['total'], data.index)


class MonthlyFigure(QTabWidget):
    def __init__(self):
        super().__init__()
        self.figure_income_and_outcome = IncomeAndOutcomeBarCanvas('Income & Outcome per month', '', 'Amount (EUR)')
        self.figure_profit = ProfitBarCanvas('Profit', 'Month', 'Amount (EUR)')
        self._set_layout()

    def _set_layout(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.figure_income_and_outcome)
        self.layout.addWidget(self.figure_profit)
        self.setLayout(self.layout)

    def show_data(self, data: pd.DataFrame):
        self.figure_income_and_outcome.plot(data['income'], data['outcome'])
        self.figure_profit.plot(data['total'], data.index)


class DailyFigure(QTabWidget):
    def __init__(self):
        super().__init__()
        self.figure_income_and_outcome = IncomeAndOutcomeLineCanvas('Income & Outcome', 'Time', 'Amount (EUR)')
        self.figure_profit = ProfitLineCanvas('Profit', 'Time', 'Amount (EUR)')
        self._set_layout()

    def _set_layout(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.figure_income_and_outcome)
        self.layout.addWidget(self.figure_profit)
        self.setLayout(self.layout)

    def show_data(self, data: pd.DataFrame):
        self.figure_income_and_outcome.plot(data['time'], data['cumulative_income'], data['cumulative_outcome'])
        self.figure_profit.plot(data['time'], data['cumulative_value'])


class EventTable(QTabWidget):
    def __init__(self):
        super().__init__()
        self.table_view = QtWidgets.QTableView()
        self.table_view.setObjectName("tableView")
        self._set_layout()

    def _set_layout(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.table_view)
        self.setLayout(self.layout)

    def show_data(self, data):
        model = DataFrameModel(data)
        self.table_view.setModel(model)
