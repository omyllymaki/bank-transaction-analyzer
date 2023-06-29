import pandas as pd
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout

from src.gui.tabs.event_table import EventTableTab
from src.gui.tabs.event_table_with_drop_data import EventTableWithDropDataTab
from src.gui.tabs.income_and_outcome import IncomeAndOutcomeTab
from src.gui.tabs.distributions import DistributionsTab


class TabHandler(QWidget):
    def __init__(self):
        super().__init__()

        self.incomes_and_outcomes_tab = IncomeAndOutcomeTab()
        self.distributions_tab = DistributionsTab()
        self.events_tab = EventTableWithDropDataTab()
        self.events_filtered_out_tab = EventTableTab()

        self.content = QTabWidget()
        self.content.addTab(self.incomes_and_outcomes_tab, "Incomes & Outcomes")
        self.content.addTab(self.distributions_tab, "Distributions")
        self.content.addTab(self.events_tab, "Events")
        self.content.addTab(self.events_filtered_out_tab, "events filtered out")

        self._set_layout()

    def _set_layout(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.content)

    def handle_data(self, data: pd.DataFrame):
        for tab in [self.incomes_and_outcomes_tab, self.distributions_tab, self.events_tab]:
            tab.handle_data(data)

    def handle_prefiltered_data(self, data: pd.DataFrame):
        self.events_filtered_out_tab.handle_data(data)

    def get_notes(self):
        d1 = self.events_tab.get_notes()
        d2 = self.events_filtered_out_tab.get_notes()
        return {**d1, **d2}
