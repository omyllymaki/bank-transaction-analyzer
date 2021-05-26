import pandas as pd
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout

from src.gui.tabs.alerts import AlertsTab
from src.gui.tabs.event_table import EventTableTab
from src.gui.tabs.income_and_outcome import IncomeAndOutcomeTab
from src.gui.tabs.indicators import IndicatorsTab
from src.gui.tabs.stacked_bars import StackedBarsTab
from src.gui.tabs.top_incomes_and_outcomes import TopIncomesAndOutComesTab


class TabHandler(QWidget):
    def __init__(self, config):
        super().__init__()

        self.tabs = {
            'Income/outcome vs time': IncomeAndOutcomeTab(),
            'Income/outcome by target': TopIncomesAndOutComesTab(),
            'Stacked bars': StackedBarsTab(),
            'Indicators': IndicatorsTab(config),
            'Alerts': AlertsTab(config),
            'Events': EventTableTab(),
        }

        self.content = QTabWidget()
        for tab_name, tab in self.tabs.items():
            self.content.addTab(tab, tab_name)
        self._set_layout()

    def _set_layout(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.content)

    def handle_filtered_data(self, data: pd.DataFrame):
        for name, tab in self.tabs.items():
            if name != "Alerts":
                tab.handle_data(data)

    def handle_non_filtered_data(self, data: pd.DataFrame):
        self.tabs["Alerts"].handle_data(data)
