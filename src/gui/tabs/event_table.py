import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QRadioButton, QVBoxLayout

from src.gui.dataframe_model import DataFrameModel
from src.gui.tabs.base_tab import BaseTab


class EventTableTab(BaseTab):
    show_columns = ["target", "account_number", "value", "time", "message", "event"]

    def __init__(self):
        self.table_view = QtWidgets.QTableView()
        self.table_view.setObjectName("tableView")
        self.group_by_target_button = QRadioButton("Group by target")
        self.header = self.table_view.horizontalHeader()
        self.group_by_target = False
        self.data = None
        self.grouped_data = None
        self.sort_col_index = 0
        self.ascending = True

        super().__init__()

    def _set_layout(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.group_by_target_button)
        self.layout.addWidget(self.table_view)
        self.setLayout(self.layout)

    def _set_connections(self):
        self.group_by_target_button.toggled.connect(self._handle_grouping_button_toggle)
        self.header.sectionClicked.connect(self._handle_header_clicked)

    def _handle_grouping_button_toggle(self):
        if self.group_by_target_button.isChecked():
            self.group_by_target = True
        else:
            self.group_by_target = False
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
        grouped = self.data.groupby("target", as_index=False)
        grouped_data = pd.DataFrame()
        grouped_data[["target", "sum"]] = grouped.sum()[["target", "value"]]
        grouped_data["mean"] = grouped.mean()["value"]
        grouped_data["median"] = grouped.median()["value"]
        grouped_data["min"] = grouped.min()["value"]
        grouped_data["max"] = grouped.max()["value"]
        grouped_data["count"] = grouped.count()["value"]
        self.grouped_data = grouped_data

        self._render_table()

    def _render_table(self):
        if self.data is not None:
            if self.group_by_target:
                table_data = self.grouped_data
            else:
                table_data = self.data
            sort_col_name = table_data.columns[self.sort_col_index]
            table_data_sorted = table_data.sort_values(sort_col_name, ascending=self.ascending)
            model = DataFrameModel(table_data_sorted)
            self.table_view.setModel(model)
