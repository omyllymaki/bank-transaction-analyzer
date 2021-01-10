import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QRadioButton, QComboBox, QHBoxLayout, QLabel

from config import INDICATORS
from data_processing.data_analyzer import DataAnalyzer
from data_processing.data_filtering import DataFilter
from gui.canvases import DoubleBarCanvas, BarCanvas
from gui.dataframe_model import DataFrameModel

SHOW_COLUMNS = ["target", "account_number", "value", "time", "message", "event"]


class TabHandler(QWidget):
    def __init__(self):
        super().__init__()

        self.content = QTabWidget()
        self.income_and_outcome = IncomeAndOutcomeTab()
        self.indicators = IndicatorsTab()
        self.event_table = EventTableTab()
        self.content.addTab(self.income_and_outcome, 'Income/outcome')
        self.content.addTab(self.indicators, 'Indicators')
        self.content.addTab(self.event_table, 'Events')
        self._set_layout()

    def _set_layout(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.content)

    def show_data(self, data: pd.DataFrame):
        self.income_and_outcome.show_data(data)
        self.indicators.show_data(data)
        self.event_table.show_data(data[SHOW_COLUMNS])


class IncomeAndOutcomeTab(QTabWidget):
    options = {
        "Year": ["year"],
        "Month": ["year", "month"],
        "Week": ["year", "week"],
        "Day": ["year", "month", "day"],
    }

    def __init__(self):
        super().__init__()
        self.option_text = None
        self.group_by = list(self.options.values())[0]
        self.analyser = DataAnalyzer()
        self.grouping_option_selector = QComboBox()
        self.grouping_option_selector.addItems(list(self.options.keys()))
        self.figure_income_and_outcome = DoubleBarCanvas(figure_title='Income & Outcome',
                                                         y_axis_title='Amount (EUR)',
                                                         y1_label="Income",
                                                         y2_label="Outcome")
        self.figure_profit = BarCanvas(figure_title='Profit',
                                       y_axis_title='Amount (EUR)')
        self._set_layout()
        self._set_connections()

    def _set_layout(self):
        self.layout = QVBoxLayout()

        grouping_layout = QHBoxLayout()
        grouping_layout.addWidget(QLabel("Grouping"))
        grouping_layout.addWidget(self.grouping_option_selector)

        self.layout.addLayout(grouping_layout)
        self.layout.addWidget(self.figure_income_and_outcome)
        self.layout.addWidget(self.figure_profit)
        self.setLayout(self.layout)

    def _set_connections(self):
        self.grouping_option_selector.currentIndexChanged.connect(self._option_changed)

    def _option_changed(self):
        self.option_text = self.grouping_option_selector.currentText()
        self.group_by = self.options[self.option_text]

    def show_data(self, data: pd.DataFrame):
        analysed_data = self.analyser.analyze_data(data, self.group_by)
        self.figure_income_and_outcome.plot(analysed_data['income'],
                                            analysed_data['outcome'],
                                            analysed_data.index.tolist())

        self.figure_profit.plot(analysed_data['total'], analysed_data.index.tolist())


class IndicatorsTab(QTabWidget):
    grouping_options = {
        "Year": ["year"],
        "Month": ["year", "month"],
        "Week": ["year", "week"],
        "Day": ["year", "month", "day"]
    }

    def __init__(self):
        super().__init__()

        self.group_by = list(self.grouping_options.values())[0]
        self.indicator_pattern = list(INDICATORS.values())[0]
        self.analyser = DataAnalyzer()
        self.filter = DataFilter()

        self.grouping_option_selector = QComboBox()
        self.grouping_option_selector.addItems(list(self.grouping_options.keys()))

        self.indicator_selector = QComboBox()
        self.indicator_selector.addItems(list(INDICATORS.keys()))

        self.figure_value = BarCanvas(y_axis_title='Amount (EUR)')
        self.figure_cumulative = BarCanvas(y_axis_title='Cumulative amount (EUR)')
        self._set_layout()
        self._set_connections()

    def _set_layout(self):
        self.layout = QVBoxLayout()

        grouping_layout = QHBoxLayout()
        grouping_layout.addWidget(QLabel("Grouping"))
        grouping_layout.addWidget(self.grouping_option_selector)
        self.layout.addLayout(grouping_layout)

        indicator_layout = QHBoxLayout()
        indicator_layout.addWidget(QLabel("Indicator"))
        indicator_layout.addWidget(self.indicator_selector)
        self.layout.addLayout(indicator_layout)

        self.layout.addWidget(self.figure_value)
        self.layout.addWidget(self.figure_cumulative)

        self.setLayout(self.layout)

    def _set_connections(self):
        self.grouping_option_selector.currentIndexChanged.connect(self._grouping_option_changed)
        self.indicator_selector.currentIndexChanged.connect(self._indicator_option_changed)

    def _grouping_option_changed(self):
        option_text = self.grouping_option_selector.currentText()
        self.group_by = self.grouping_options[option_text]

    def _indicator_option_changed(self):
        option_text = self.indicator_selector.currentText()
        self.indicator_pattern = INDICATORS[option_text]

    def show_data(self, data: pd.DataFrame):
        filtered_data = self.filter.filter(data, target=self.indicator_pattern)
        analysed_data = self.analyser.analyze_data(filtered_data, self.group_by)
        self.figure_value.plot(analysed_data['total'], analysed_data.index.tolist())
        self.figure_cumulative.plot(analysed_data['total_cumulative'], analysed_data.index.tolist(), plot_average=False)


class EventTableTab(QTabWidget):
    def __init__(self):
        super().__init__()
        self.table_view = QtWidgets.QTableView()
        self.table_view.setObjectName("tableView")
        self.group_by_target_button = QRadioButton("Group by target")
        self._set_layout()
        self._set_connections()
        self.group_by_target = False

    def _set_layout(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.group_by_target_button)
        self.layout.addWidget(self.table_view)
        self.setLayout(self.layout)

    def _set_connections(self):
        self.group_by_target_button.toggled.connect(self._handle_grouping_button_toggle)

    def _handle_grouping_button_toggle(self):
        if self.group_by_target_button.isChecked():
            self.group_by_target = True
        else:
            self.group_by_target = False

    def show_data(self, data):
        if self.group_by_target:
            grouped_data = data.groupby("target", as_index=False).sum()[["target", "value"]].sort_values("value")
            model = DataFrameModel(grouped_data)
        else:
            model = DataFrameModel(data)
        self.table_view.setModel(model)
