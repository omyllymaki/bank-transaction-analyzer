import pandas as pd
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout

from gui.tabs.event_table import EventTableTab
from gui.tabs.income_and_outcome import IncomeAndOutcomeTab
from gui.tabs.indicators import IndicatorsTab
from gui.tabs.stacked_bars import StackedBarsTab
from gui.tabs.top_incomes_and_outcomes import TopIncomesAndOutComesTab


class TabHandler(QWidget):
    def __init__(self):
        super().__init__()

        self.tabs = {
            'Income/outcome vs time': IncomeAndOutcomeTab(),
            'Income/outcome by target': TopIncomesAndOutComesTab(),
            'Stacked bars': StackedBarsTab(),
            'Indicators': IndicatorsTab(),
            'Events': EventTableTab(),
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
