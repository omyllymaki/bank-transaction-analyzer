import pandas as pd
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QRadioButton, QComboBox, QHBoxLayout, QLabel, QLineEdit

from config import INDICATORS
from data_processing.data_analyzer import DataAnalyzer
from data_processing.data_filtering import DataFilter
from gui.canvases import DoubleBarCanvas, BarCanvas, BarHorizontalCanvas
from gui.dataframe_model import DataFrameModel

SHOW_COLUMNS = ["target", "account_number", "value", "time", "message", "event"]


class TabHandler(QWidget):
    def __init__(self):
        super().__init__()

        self.content = QTabWidget()
        self.income_and_outcome_vs_time = IncomeAndOutcomeTab()
        self.top_incomes_and_outcomes = TopIncomesAndOutComes()
        self.indicators = IndicatorsTab()
        self.event_table = EventTableTab()
        self.content.addTab(self.income_and_outcome_vs_time, 'Income/outcome vs time')
        self.content.addTab(self.top_incomes_and_outcomes, 'Top incomes/outcomes')
        self.content.addTab(self.indicators, 'Indicators')
        self.content.addTab(self.event_table, 'Events')
        self._set_layout()

    def _set_layout(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.content)

    def show_data(self, data: pd.DataFrame):
        self.income_and_outcome_vs_time.show_data(data)
        self.top_incomes_and_outcomes.show_data(data)
        self.indicators.show_data(data)
        self.event_table.show_data(data[SHOW_COLUMNS])


class TopIncomesAndOutComes(QTabWidget):
    criteria_options = ["sum", "mean", "max"]
    output_options = ["income", "outcome"]

    def __init__(self):
        super().__init__()
        self.selected_criteria = self.criteria_options[0]
        self.selected_output = self.output_options[0]

        self.analyser = DataAnalyzer()

        self.criteria_selector = QComboBox()
        self.criteria_selector.addItems(self.criteria_options)

        self.output_selector = QComboBox()
        self.output_selector.addItems(self.output_options)

        self.min_value_line = QLineEdit(self)
        self.min_value_line.setText("0")
        self.max_value_line = QLineEdit(self)
        self.max_value_line.setText("100000")
        self.amount_line = QLineEdit(self)
        self.amount_line.setText("10")

        self.canvas = BarHorizontalCanvas(figure_title='Income & Outcome',
                                          y_axis_title='Target',
                                          x_axis_title='Amount (EUR)')
        self._set_layout()
        self._set_connections()

    def _set_layout(self):
        self.layout = QVBoxLayout()

        criteria_layout = QHBoxLayout()
        criteria_layout.addWidget(QLabel("Criteria"))
        criteria_layout.addWidget(self.criteria_selector)

        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output"))
        output_layout.addWidget(self.output_selector)

        min_max_layout = QHBoxLayout()
        min_max_layout.addWidget(QLabel("Min"))
        min_max_layout.addWidget(self.min_value_line)
        min_max_layout.addWidget(QLabel("Max"))
        min_max_layout.addWidget(self.max_value_line)
        min_max_layout.addWidget(QLabel("Amount"))
        min_max_layout.addWidget(self.amount_line)

        self.layout.addLayout(criteria_layout)
        self.layout.addLayout(output_layout)
        self.layout.addLayout(min_max_layout)
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

    def _set_connections(self):
        self.criteria_selector.currentIndexChanged.connect(self._criteria_changed)
        self.output_selector.currentIndexChanged.connect(self._output_changed)

    def _criteria_changed(self):
        self.selected_criteria = self.criteria_selector.currentText()

    def _output_changed(self):
        self.selected_output = self.output_selector.currentText()

    def _get_min_value(self) -> float:
        try:
            text = self.min_value_line.text()
            if text == "":
                return 0
            else:
                return float(text)
        except (ValueError, TypeError):
            return None

    def _get_max_value(self) -> float:
        try:
            text = self.max_value_line.text()
            if text == "":
                return np.inf
            else:
                return float(text)
        except (ValueError, TypeError):
            return None

    def _get_amount(self) -> float:
        try:
            return int(self.amount_line.text())
        except (ValueError, TypeError):
            return None

    def show_data(self, data: pd.DataFrame):
        incomes, outcomes = self.analyser.calculate_top_incomes_and_outcomes(data, self.selected_criteria)
        min_value = self._get_min_value()
        max_value = self._get_max_value()
        n_values = self._get_amount()
        if self.selected_output == "income":
            values_to_show = incomes
        else:
            values_to_show = outcomes
        i1 = values_to_show > min_value
        i2 = values_to_show < max_value
        values_to_show = values_to_show[i1 & i2]
        values_to_show = values_to_show[:]
        values_to_show = values_to_show[:n_values]
        self.canvas.plot(values_to_show.values, values_to_show.index)


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
        analysed_data = self.analyser.calculate_incomes_and_outcomes(data, self.group_by)
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
        analysed_data = self.analyser.calculate_incomes_and_outcomes(filtered_data, self.group_by)
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
