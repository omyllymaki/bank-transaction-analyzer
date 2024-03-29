import math

import numpy as np
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import pyqtSignal


class DataFrameModel(QtCore.QAbstractTableModel):
    """
    Class to populate a table view with a pandas dataframe
    """

    data_edited_signal = pyqtSignal(tuple)

    def __init__(self, data, parent=None, columns_for_edition=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data
        self._max_values = self._data.max()
        self._min_values = self._data.min()
        if columns_for_edition:
            self.columns_for_edition = columns_for_edition
        else:
            self.columns_for_edition = []

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[col]
        return None

    def setData(self, index, value, role):
        if role == QtCore.Qt.EditRole:
            self._data.iloc[index.row(), index.column()] = value
            i = self._data.index[index.row()]
            c = self._data.columns[index.column()]
            self.data_edited_signal.emit((i, c, value))
            return True
        return False

    def flags(self, index):
        col_name = self._data.columns[index.column()]
        if col_name in self.columns_for_edition:
            if not index.isValid():
                return QtCore.Qt.ItemIsEnabled
            return super().flags(index) | QtCore.Qt.ItemIsEditable
        return super().flags(index)
