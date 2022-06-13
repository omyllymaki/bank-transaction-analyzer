import pandas as pd
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout

from src.gui.tabs.event_table import EventTableTab
from src.gui.tabs.event_table_with_drop_data import EventTableWithDropDataTab
from src.gui.tabs.income_and_outcome import IncomeAndOutcomeTab
from src.gui.tabs.indicators import IndicatorsTab
from src.gui.tabs.distributions import DistributionsTab

EVENT_COLUMNS = ["target", "account_number", "value", "time", "message", "event", "category", "bank", "id"]
PREFILTERED_EVENT_COLUMNS = ["target", "account_number", "value", "time", "message", "event", "bank", "id"]


class TabHandler(QWidget):
    def __init__(self, config):
        super().__init__()

        self.tabs = {
            'Incomes & outcomes': IncomeAndOutcomeTab(),
            'Distributions': DistributionsTab(),
            'Indicators': IndicatorsTab(config["indicators"]),
            'Events': EventTableWithDropDataTab(EVENT_COLUMNS, config),
        }
        self.prefiltered_event_table = EventTableTab(PREFILTERED_EVENT_COLUMNS)

        self.content = QTabWidget()
        for tab_name, tab in self.tabs.items():
            self.content.addTab(tab, tab_name)
        self.content.addTab(self.prefiltered_event_table, "Prefiltered events")
        self._set_layout()

    def _set_layout(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.content)

    def handle_data(self, data: pd.DataFrame):
        for tab in self.tabs.values():
            tab.handle_data(data)

    def handle_prefiltered_data(self, data: pd.DataFrame):
        self.prefiltered_event_table.handle_data(data)

    def update_config(self, config):
        self.tabs["Indicators"].update_indicators(config["indicators"])
