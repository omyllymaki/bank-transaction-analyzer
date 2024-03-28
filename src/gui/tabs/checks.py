import pandas as pd
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QTableView

from src.data_processing.checks.utils import get_checks
from src.gui.dataframe_model import DataFrameModel
from src.gui.tabs.base_tab import BaseTab


class ChecksTab(BaseTab):
    def __init__(self, check_specifications):
        self.summary_table_view = QTableView()
        self.details_table_view = QTableView()
        self.summary_model = DataFrameModel(pd.DataFrame(), boolean_cell_background=True)
        self.details_model = DataFrameModel(pd.DataFrame(), boolean_cell_background=True)
        self.checks = get_checks(check_specifications)
        self.results = []
        super().__init__()

    def _set_layout(self):
        layout = QHBoxLayout(self)

        summary_table_layout = QVBoxLayout(self)
        summary_label = QLabel("Check summary")
        summary_table_layout.addWidget(summary_label)
        summary_table_layout.addWidget(self.summary_table_view)
        layout.addLayout(summary_table_layout, 1)

        items = []
        for check in self.checks:
            items.append({"name": check.get_name(), "passed": False})
        df = pd.DataFrame(items)
        self.summary_model.df = df
        self.summary_table_view.setModel(self.summary_model)

        details_table_layout = QVBoxLayout(self)
        self.selected_check_label = QLabel("Selected check: None")
        details_table_layout.addWidget(self.selected_check_label)
        details_table_layout.addWidget(self.details_table_view)
        layout.addLayout(details_table_layout, 2)

        self.setLayout(layout)

    def _set_connections(self):
        self.summary_table_view.clicked.connect(self._show_check_results)

    def handle_data(self, data):
        passed_list = []
        results_list = []
        for check in self.checks:
            passed, results = check.apply(data.copy())
            passed_list.append(passed)
            results_list.append(results)
        self.summary_model.df["passed"] = passed_list
        self.results = results_list
        selected_indexes = self.summary_table_view.selectedIndexes()
        if selected_indexes:
            selected_index = selected_indexes[0]
            self._show_check_results(selected_index)

    def _show_check_results(self, index):
        row_index = index.row()
        check_name = self.checks[row_index].get_name()
        results = self.results[row_index]
        results["key"] = results.index
        self.details_model = DataFrameModel(results, boolean_cell_background=True)
        self.details_table_view.setModel(self.details_model)
        self.selected_check_label.setText(f"Selected check: {check_name}")
