import pandas as pd
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout

from src.gui.tabs.event_table import EventTableTab
from src.gui.tabs.income_and_outcome import IncomeAndOutcomeTab
from src.gui.tabs.indicators import IndicatorsTab
from src.gui.tabs.distributions import DistributionsTab


class TabHandler(QWidget):
    def __init__(self, config):
        super().__init__()

        self.tabs = {
            'Incomes & outcomes': IncomeAndOutcomeTab(),
            'Distributions': DistributionsTab(),
            'Indicators': IndicatorsTab(config["indicators"]),
            'Events': EventTableTab(config),
        }

        self.content = QTabWidget()
        for tab_name, tab in self.tabs.items():
            self.content.addTab(tab, tab_name)
        self._set_layout()

    def _set_layout(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.content)

    def handle_data(self, data: pd.DataFrame):
        for tab in self.tabs.values():
            tab.handle_data(data)

    def update_config(self, config):
        self.tabs["Indicators"].update_indicators(config["indicators"])
