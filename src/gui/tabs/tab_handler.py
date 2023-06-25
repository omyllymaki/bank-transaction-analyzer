import pandas as pd
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout

from src.gui.tabs.event_table import EventTableTab
from src.gui.tabs.event_table_with_drop_data import EventTableWithDropDataTab
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
            'Events': EventTableWithDropDataTab(config),
            "Events filtered out": EventTableTab()
        }

        self.content = QTabWidget()
        for tab_name, tab in self.tabs.items():
            self.content.addTab(tab, tab_name)
        self._set_layout()

    def _set_layout(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.content)

    def handle_data(self, data: pd.DataFrame):
        for tab_name, tab in self.tabs.items():
            if tab_name != "Events filtered out":
                tab.handle_data(data)

    def handle_prefiltered_data(self, data: pd.DataFrame):
        self.tabs["Events filtered out"].handle_data(data)

    def update_config(self, config):
        self.tabs["Indicators"].update_indicators(config["indicators"])

    def get_notes(self):
        d1 = self.tabs['Events'].get_notes()
        d2 = self.tabs['Events filtered out'].get_notes()
        return {**d1, **d2}
