import pandas as pd
from PyQt5.QtWidgets import QComboBox, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog, QButtonGroup

from src.alert_checks.check_runner import CheckRunner
from src.alert_checks.utils import checks_from_json
from src.data_processing.data_analyzer import DataAnalyzer
from src.data_processing.data_filtering import DataFilter
from src.gui.canvases.bar_canvas import BarCanvas
from src.gui.tabs.base_tab import BaseTab


class AlertsTab(BaseTab):
    grouping_options = {
        "Year": ["year"],
        "Month": ["year", "month"],
        "Week": ["year", "week"],
        "Day": ["year", "month", "day"]
    }

    def __init__(self, config):

        self.checks = checks_from_json("alert_checks.json")
        self.summary_label = QLabel('Test summary: ')
        self.buttons = {}
        self.btn_grp = QButtonGroup()
        for check in self.checks:
            button = QPushButton(check.name)
            self.buttons[check.name] = button
            self.btn_grp.addButton(button)

        self.test_results_figure = BarCanvas(y_axis_title='Amount (EUR)')

        self.check_runner = CheckRunner()

        super().__init__()

    def _set_layout(self):
        self.layout = QHBoxLayout()

        test_buttons_layout = QVBoxLayout()
        test_buttons_layout.addWidget(self.summary_label)
        for button in self.buttons.values():
            test_buttons_layout.addWidget(button)

        self.layout.addLayout(test_buttons_layout)
        self.layout.addWidget(self.test_results_figure)

        self.setLayout(self.layout)

    def _set_connections(self):
       self.btn_grp.buttonClicked.connect(self._handle_test_button_clicked)

    def handle_data(self, data):
        _, not_passed = self.check_runner.run_checks(data, self.checks)
        not_passes_names = [i.name for i in not_passed]

        n_total = len(self.checks)
        n_passed = len(self.checks) - len(not_passed)

        summary_text = f"Test summary: {n_passed}/{n_total} ({100 * n_passed / n_total:0.1f} %) passed"
        self.summary_label.setText(summary_text)

        for name, button in self.buttons.items():
            if name in not_passes_names:
                button.setStyleSheet("background-color: red")
            else:
                button.setStyleSheet("background-color: green")

    def _handle_test_button_clicked(self, button):
        name = button.text()
        test_values, ref_values = self.check_runner.get_test_values(name)
        x_values = [str(k) for k in range(len(test_values))]
        self.test_results_figure.figure_title = name
        self.test_results_figure.plot(y=test_values, x_labels=x_values, y_ref=ref_values)
