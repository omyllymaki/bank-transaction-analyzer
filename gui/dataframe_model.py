import math

import pandas as pd
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QBrush
import numpy as np


class DataFrameModel(QtCore.QAbstractTableModel):
    """
    Class to populate a table view with a pandas dataframe
    """

    colors_green = ["#f7fcf5", "#e5f5e0", "#c7e9c0", "#a1d99b", "#74c476", "#41ab5d", "#238b45", "#006d2c", "#00441b"]
    colors_red = ["#fff5eb", "#fee6ce", "#fdd0a2", "#fdae6b", "#fd8d3c", "#f16913", "#d94801", "#a63603", "#7f2704"]

    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data
        self._max_values = self._data.max()
        self._min_values = self._data.min()

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
            if role == QtCore.Qt.BackgroundRole:

                value = self._data.iloc[index.row()][index.column()]
                is_number = isinstance(value, int) or isinstance(value, float)

                if is_number:
                    if value < 0:
                        min_value = self._min_values[index.column()]
                        ratio_sqrt = np.sqrt(abs(value) / abs(min_value))
                        color_index = math.ceil(len(self.colors_green) * ratio_sqrt) - 1
                        color = self.colors_red[color_index]
                    else:
                        max_value = self._max_values[index.column()]
                        ratio_sqrt = np.sqrt(value / max_value)
                        color_index = math.ceil(len(self.colors_green) * ratio_sqrt) - 1
                        color = self.colors_green[color_index]
                    return QtGui.QColor(color)

        return None

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[col]
        return None
