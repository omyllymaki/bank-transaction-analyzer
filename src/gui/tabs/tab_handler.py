import pandas as pd
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout

from src.gui.tabs.event_table import EventTableTab
from src.gui.tabs.event_table_with_drop_data import EventTableWithDropDataTab
from src.gui.tabs.income_and_outcome import IncomeAndOutcomeTab
from src.gui.tabs.distributions import DistributionsTab
from src.gui.tabs.year_comparison import YearComparisonTab


class TabHandler(QWidget):
    def __init__(self):
        super().__init__()

        self.incomes_and_outcomes_tab = IncomeAndOutcomeTab()
        self.year_comparison_tab = YearComparisonTab()
        self.distributions_tab = DistributionsTab()
        self.events_tab = EventTableWithDropDataTab()
        self.events_filtered_out_tab = EventTableTab()

        self.content = QTabWidget()
        self.content.addTab(self.incomes_and_outcomes_tab, "Incomes & Outcomes")
        self.content.addTab(self.year_comparison_tab, "Year comparison")
        self.content.addTab(self.distributions_tab, "Distributions")
        self.content.addTab(self.events_tab, "Events")
        self.content.addTab(self.events_filtered_out_tab, "Events filtered out")

        self._set_layout()

    def _set_layout(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.content)

    def handle_data(self, data: pd.DataFrame):
        for tab in [self.incomes_and_outcomes_tab, self.year_comparison_tab, self.distributions_tab, self.events_tab]:
            tab.handle_data(data)

    def handle_removed_data(self, data: pd.DataFrame):
        self.events_filtered_out_tab.handle_data(data)
