from typing import Dict

import pandas as pd
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout

from gui.canvases import IncomeAndOutcomeBarCanvas, IncomeAndOutcomeLineCanvas, ProfitBarCanvas, ProfitLineCanvas


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

    def plot_data(self, data: Dict[str, pd.DataFrame]):
        self.figure_yearly_data.plot(data['by_year'])
        self.figure_monthly_data.plot(data['by_year_and_month'])
        self.figure_daily_data.plot(data['by_event'])
        self.event_table.plot(data['by_event'])


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

    def plot(self, data: pd.DataFrame):
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

    def plot(self, data: pd.DataFrame):
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

    def plot(self, data: pd.DataFrame):
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

    def plot(self, data):
        model = DataFrameModel(data)
        self.table_view.setModel(model)


class DataFrameModel(QtCore.QAbstractTableModel):
    DtypeRole = QtCore.Qt.UserRole + 1000
    ValueRole = QtCore.Qt.UserRole + 1001

    def __init__(self, df=pd.DataFrame(), parent=None):
        super(DataFrameModel, self).__init__(parent)
        self._dataframe = df

    def setDataFrame(self, dataframe):
        self.beginResetModel()
        self._dataframe = dataframe.copy()
        self.endResetModel()

    def dataFrame(self):
        return self._dataframe

    dataFrame = QtCore.pyqtProperty(pd.DataFrame, fget=dataFrame, fset=setDataFrame)

    @QtCore.pyqtSlot(int, QtCore.Qt.Orientation, result=str)
    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._dataframe.columns[section]
            else:
                return str(self._dataframe.index[section])
        return QtCore.QVariant()

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._dataframe.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return self._dataframe.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount() \
                                       and 0 <= index.column() < self.columnCount()):
            return QtCore.QVariant()
        row = self._dataframe.index[index.row()]
        col = self._dataframe.columns[index.column()]
        dt = self._dataframe[col].dtype

        val = self._dataframe.iloc[row][col]
        if role == QtCore.Qt.DisplayRole:
            return str(val)
        elif role == DataFrameModel.ValueRole:
            return val
        if role == DataFrameModel.DtypeRole:
            return dt
        return QtCore.QVariant()

    def roleNames(self):
        roles = {
            QtCore.Qt.DisplayRole: b'display',
            DataFrameModel.DtypeRole: b'dtype',
            DataFrameModel.ValueRole: b'value'
        }
        return roles
