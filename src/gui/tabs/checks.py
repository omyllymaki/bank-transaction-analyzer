import pandas as pd
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QTableView

from src.data_processing.checks.utils import get_checks
from src.gui.dataframe_model import DataFrameModel
from src.gui.tabs.base_tab import BaseTab


class ChecksTab(BaseTab):
    def __init__(self, check_specifications):
        self.table_view = QTableView()
        self.model = DataFrameModel(pd.DataFrame())
        self.checks = get_checks(check_specifications)
        super().__init__()

    def _set_layout(self):
        self.layout = QHBoxLayout(self)
        table_layout = QVBoxLayout(self)
        self.selected_test_label = QLabel("Selected Test: None")
        table_layout.addWidget(self.selected_test_label)
        table_layout.addWidget(self.table_view)
        self.layout.addLayout(table_layout)

    def _set_connections(self):
        pass

    def handle_data(self, data):
        layout = QVBoxLayout()

        for i, check in enumerate(self.checks):
            passed, results = check.apply(data)

            item_layout = QHBoxLayout()
            name_label = QLabel(check.name)
            item_layout.addWidget(name_label)
            if passed:
                pixmap = QPixmap(20, 20)
                pixmap.fill(QColor("green"))
            else:
                pixmap = QPixmap(20, 20)
                pixmap.fill(QColor("red"))
            status_label = QLabel()
            status_label.setPixmap(pixmap)
            item_layout.addWidget(status_label)
            layout.addLayout(item_layout)

            name_label.mousePressEvent = lambda event, check=check, results=results: self.render_table(check, results)
            if i == 0:
                self.render_table(check, results)

        self.layout.addLayout(layout)

    def render_table(self, check, results):
        results["key"] = results.index
        self.model = DataFrameModel(results)
        self.table_view.setModel(self.model)
        self.selected_test_label.setText(f"Selected Test: {check.name}")