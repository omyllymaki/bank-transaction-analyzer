import pandas as pd
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QAbstractItemView, QPushButton, QFileDialog
from src.gui.dataframe_model import DataFrameModel
from src.gui.tabs.base_tab import BaseTab


class EventTableTab(BaseTab):
    notes_edited_signal = pyqtSignal(tuple)
    COLUMNS = ["target", "account_number", "value", "time", "year", "month", "message", "event", "category", "labels", "bank", "id",
               "notes", "is_duplicate"]
    EDITABLE_COLUMNS = ["notes"]

    def __init__(self):
        self.table_view = QtWidgets.QTableView()
        self.table_view.setObjectName("tableView")
        self.export_data_button = QPushButton('Export data')
        self.header = self.table_view.horizontalHeader()
        self.group_by_target = False
        self.group_by = "target"
        self.table_data_sorted = None
        self.grouped_data = None
        self.sort_col_index = 0
        self.ascending = True
        self.model = DataFrameModel(pd.DataFrame())

        super().__init__()

    def _set_layout(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.table_view)
        self.layout.addWidget(self.export_data_button, alignment=QtCore.Qt.AlignLeft)
        self.setLayout(self.layout)

    def _set_connections(self):
        self.header.sectionClicked.connect(self._handle_header_clicked)
        self.header.sectionClicked.connect(self._handle_header_clicked)
        self.header.setContextMenuPolicy(Qt.CustomContextMenu)
        self.header.customContextMenuRequested.connect(self._handle_header_right_clicked)
        self.header.setSelectionMode(QAbstractItemView.SingleSelection)
        self.export_data_button.clicked.connect(self._handle_data_export)

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
        self.data = data[self.COLUMNS]
        self._group_data()
        self._render_table()

    def _group_data(self):
        if not self.group_by_target:
            return
        grouped = self.data.groupby(self.group_by, as_index=False)
        grouped_data = pd.DataFrame()
        grouped_data[self.group_by] = grouped.first()[self.group_by]
        grouped_data["sum"] = grouped.sum(numeric_only=True)["value"]
        grouped_data["mean"] = grouped.mean(numeric_only=True)["value"]
        grouped_data["median"] = grouped.median(numeric_only=True)["value"]
        grouped_data["min"] = grouped.min(numeric_only=True)["value"]
        grouped_data["max"] = grouped.max(numeric_only=True)["value"]
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
            self.model = DataFrameModel(self.table_data_sorted, columns_for_edition=self.EDITABLE_COLUMNS)
            self.table_view.setModel(self.model)
            self.model.data_edited_signal.connect(self._handle_data_edited)

    def _handle_data_edited(self, data):
        index, column, value = data
        self.data.loc[index, column] = value
        event_id = self.data["id"].loc[index]
        self.notes_edited_signal.emit((event_id, value))

    def _handle_data_export(self):
        file_filter = "CSV Files (*.csv)"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            "",
            file_filter,
        )
        if file_path:
            self.model._data.to_csv(file_path)
