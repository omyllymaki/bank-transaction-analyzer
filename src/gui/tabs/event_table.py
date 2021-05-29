import json

import pandas as pd
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QRadioButton, QVBoxLayout, QMenu, QAction, QAbstractItemView

from src.gui.dataframe_model import DataFrameModel
from src.gui.dialog_boxes import show_warning
from src.gui.tabs.base_tab import BaseTab
from src.utils import load_json, save_json


class EventTableTab(BaseTab):
    drop_data_added = pyqtSignal()
    show_columns = ["target", "account_number", "value", "time", "message", "event", "category"]

    def __init__(self, config):
        self.config = config
        self.table_view = QtWidgets.QTableView()
        self.table_view.setObjectName("tableView")
        self.header = self.table_view.horizontalHeader()
        self.group_by_target = False
        self.group_by = "target"
        self.data = None
        self.table_data_sorted = None
        self.grouped_data = None
        self.sort_col_index = 0
        self.ascending = True

        super().__init__()

    def _set_layout(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.table_view)
        self.setLayout(self.layout)

    def _set_connections(self):
        self.header.sectionClicked.connect(self._handle_header_clicked)
        self.header.sectionClicked.connect(self._handle_header_clicked)
        self.header.setContextMenuPolicy(Qt.CustomContextMenu)
        self.header.customContextMenuRequested.connect(self._handle_header_right_clicked)
        self.header.setSelectionMode(QAbstractItemView.SingleSelection)

    def _handle_header_right_clicked(self, position):
        index = self.header.logicalIndexAt(position)
        self.group_by = self.table_data_sorted.columns[index]
        self.group_by_target = not self.group_by_target
        self._group_data()
        self.sort_col_index = 0
        self._render_table()

    def _handle_header_clicked(self, index):
        self.sort_col_index = index
        order = self.header.sortIndicatorOrder()
        if order == 0:
            self.ascending = True
        else:
            self.ascending = False
        self._render_table()

    def handle_data(self, data):
        self.data = data[self.show_columns]
        self._group_data()
        self._render_table()

    def _group_data(self):
        if not self.group_by_target:
            return
        grouped = self.data.groupby(self.group_by, as_index=False)
        grouped_data = pd.DataFrame()
        grouped_data[self.group_by] = grouped.first()[self.group_by]
        grouped_data["sum"] = grouped.sum()["value"]
        grouped_data["mean"] = grouped.mean()["value"]
        grouped_data["median"] = grouped.median()["value"]
        grouped_data["min"] = grouped.min()["value"]
        grouped_data["max"] = grouped.max()["value"]
        grouped_data["count"] = grouped.count()["value"]
        self.grouped_data = grouped_data

    def _render_table(self):
        if self.data is not None:
            if self.group_by_target:
                table_data = self.grouped_data
            else:
                table_data = self.data
            sort_col_name = table_data.columns[self.sort_col_index]
            self.table_data_sorted = table_data.sort_values(sort_col_name, ascending=self.ascending)
            model = DataFrameModel(self.table_data_sorted)
            self.table_view.setModel(model)

    def contextMenuEvent(self, event):
        if not self.group_by_target:
            self.menu = QMenu(self)
            action = QAction('Add to drop data file', self)
            action.triggered.connect(lambda: self.add_to_drop_data(event))
            self.menu.addAction(action)
            self.menu.popup(QtGui.QCursor.pos())

    def add_to_drop_data(self, event):
        col_index = self.table_view.currentIndex().column()
        row_index = self.table_view.currentIndex().row()
        column = self.table_data_sorted.columns[col_index]
        content = self.table_data_sorted.iloc[row_index, col_index]

        try:
            drop_data = load_json(self.config["paths"]["drop_data"])
            values = drop_data.get(column, None)
            if values:
                drop_data[column] = values + [content]
            else:
                drop_data[column] = [content]
            save_json(self.config["paths"]["drop_data"], drop_data)
            self.drop_data_added.emit()

        except Exception as e:
            print(e)
            show_warning("Drop data addition failure", "Something went wrong")
