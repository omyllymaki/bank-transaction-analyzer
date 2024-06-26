import numpy as np
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor


class DataFrameModel(QtCore.QAbstractTableModel):
    """
    Class to populate a table view with a pandas dataframe
    """

    data_edited_signal = pyqtSignal(tuple)

    def __init__(self, df, parent=None, columns_for_edition=None, boolean_cell_background=False):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.df = df
        self._max_values = self.df.max()
        self._min_values = self.df.min()
        if columns_for_edition:
            self.columns_for_edition = columns_for_edition
        else:
            self.columns_for_edition = []
        self.boolean_cell_background = boolean_cell_background

    def rowCount(self, parent=None):
        return self.df.shape[0]

    def columnCount(self, parent=None):
        return self.df.shape[1]

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self.df.iloc[index.row(), index.column()])
            elif role == QtCore.Qt.BackgroundRole and self.boolean_cell_background:
                value = self.df.iloc[index.row(), index.column()]
                if isinstance(value, bool) or isinstance(value, np.bool_):
                    if value:
                        return QtGui.QBrush(QtGui.QColor(0, 255, 0))
                    else:
                        return QtGui.QBrush(QtGui.QColor(255, 0, 0))
        return None

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.df.columns[col]
        return None

    def setData(self, index, value, role):
        if role == QtCore.Qt.EditRole:
            self.df.iloc[index.row(), index.column()] = value
            i = self.df.index[index.row()]
            c = self.df.columns[index.column()]
            self.data_edited_signal.emit((i, c, value))
            return True
        return False

    def flags(self, index):
        col_name = self.df.columns[index.column()]
        if col_name in self.columns_for_edition:
            if not index.isValid():
                return QtCore.Qt.ItemIsEnabled
            return super().flags(index) | QtCore.Qt.ItemIsEditable
        return super().flags(index)
