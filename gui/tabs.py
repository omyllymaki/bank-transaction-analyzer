import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QRadioButton, QComboBox, QHBoxLayout, QLabel, QPushButton, \
    QFileDialog, QSlider

from data_processing.data_analyzer import DataAnalyzer
from data_processing.data_filtering import DataFilter
from gui.canvases import DoubleBarCanvas, BarCanvas, BarHorizontalCanvas, StackedBarsCanvas
from gui.dataframe_model import DataFrameModel
from gui.widgets import FloatLineEdit

SHOW_COLUMNS = ["target", "account_number", "value", "time", "message", "event"]


class TabHandler(QWidget):
    def __init__(self):
        super().__init__()

        self.content = QTabWidget()
        self.income_and_outcome_vs_time = IncomeAndOutcomeTab()
        self.top_incomes_and_outcomes = TopIncomesAndOutComesTab()
        self.indicators = IndicatorsTab()
        self.event_table = EventTableTab()
        self.stacked_bars = StackedBarsTab()
        self.content.addTab(self.income_and_outcome_vs_time, 'Income/outcome vs time')
        self.content.addTab(self.top_incomes_and_outcomes, 'Income/outcome by target')
        self.content.addTab(self.stacked_bars, 'Stacked bars')
        self.content.addTab(self.event_table, 'Events')
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
        self.stacked_bars.show_data(data)


class TopIncomesAndOutComesTab(QTabWidget):
    criteria_options = ["sum", "mean", "max"]
    output_options = ["income", "outcome"]
    n_values_to_show = 15

    def __init__(self):
        super().__init__()
        self.selected_criteria = self.criteria_options[0]
        self.selected_output = self.output_options[0]

        self.analyser = DataAnalyzer()

        self.criteria_selector = QComboBox()
        self.criteria_selector.addItems(self.criteria_options)

        self.output_selector = QComboBox()
        self.output_selector.addItems(self.output_options)

        self.slider = QSlider(Qt.Vertical)
        self.slider.setMinimum(0)
        self.slider.setValue(0)
        self.current_slider_value = 0

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

        figure_layout = QHBoxLayout()
        figure_layout.addWidget(self.slider)
        figure_layout.addWidget(self.canvas)

        self.layout.addLayout(criteria_layout)
        self.layout.addLayout(output_layout)
        self.layout.addLayout(figure_layout)
        self.setLayout(self.layout)

    def _set_connections(self):
        self.criteria_selector.currentIndexChanged.connect(self._criteria_changed)
        self.output_selector.currentIndexChanged.connect(self._output_changed)
        self.slider.valueChanged.connect(self._handle_slider_value_changed)

    def _criteria_changed(self):
        self.selected_criteria = self.criteria_selector.currentText()

    def _output_changed(self):
        self.selected_output = self.output_selector.currentText()

    def _handle_slider_value_changed(self):
        self.current_slider_value = self.slider.value()
        self._update_canvas()

    def show_data(self, data: pd.DataFrame):
        incomes, outcomes = self.analyser.calculate_top_incomes_and_outcomes(data, self.selected_criteria)
        if self.selected_output == "income":
            values_to_show = incomes
        else:
            values_to_show = outcomes
        self.values_to_show = values_to_show
        self.slider.setValue(0)
        self.slider.setMaximum(values_to_show.shape[0] - self.n_values_to_show)
        self._update_canvas()

    def _update_canvas(self):
        values_to_show = self.values_to_show[
                         self.current_slider_value:self.current_slider_value + self.n_values_to_show]
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

        self.indicator_values = None
        self.indicators_dict = {}
        self.analyser = DataAnalyzer()
        self.filter = DataFilter()

        self.grouping_option_selector = QComboBox()
        self.grouping_option_selector.addItems(list(self.grouping_options.keys()))
        self._grouping_option_changed()

        self.indicator_selector = QComboBox()

        self.load_button = QPushButton('Load indicators')

        self.figure_value = BarCanvas(y_axis_title='Amount (EUR)')
        self.figure_cumulative = BarCanvas(y_axis_title='Cumulative amount (EUR)')
        self._set_layout()
        self._set_connections()

    def _set_layout(self):
        self.layout = QVBoxLayout()

        self.layout.addWidget(self.load_button)

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
        self.load_button.clicked.connect(self._handle_load_indicators)

    def _grouping_option_changed(self):
        option_text = self.grouping_option_selector.currentText()
        self.group_by = self.grouping_options[option_text]

    def _indicator_option_changed(self):
        self.current_indicator = self.indicator_selector.currentText()
        self.indicator_values = self.indicators_dict.get(self.current_indicator, None)

    def _handle_load_indicators(self):
        file_path, _ = QFileDialog.getOpenFileName(caption='Choose indicators file for analysis', directory=".")
        if not file_path:
            return None
        indicators = pd.read_csv(file_path)
        indicators = indicators.where(pd.notnull(indicators), None)
        indicators.set_index("name", inplace=True)
        self.indicators_dict = indicators.to_dict("index")
        self.indicator_selector.clear()
        self.indicator_selector.addItems(list(self.indicators_dict.keys()))
        self._indicator_option_changed()

    def show_data(self, data: pd.DataFrame):
        if self.indicator_values is not None:
            filtered_data = self.filter.filter(data,
                                               min_value=self.indicator_values["min_value"],
                                               max_value=self.indicator_values["max_value"],
                                               target=self.indicator_values["target"],
                                               message=self.indicator_values["message"],
                                               account_number=self.indicator_values["account_number"],
                                               event=self.indicator_values["event"])
            analysed_data = self.analyser.calculate_incomes_and_outcomes(filtered_data, self.group_by)
            self.figure_value.plot(analysed_data['total'], analysed_data.index.tolist())
            self.figure_cumulative.plot(analysed_data['total_cumulative'],
                                        analysed_data.index.tolist(),
                                        plot_average=False)


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
            grouped = data.groupby("target", as_index=False)
            table_data = pd.DataFrame()
            table_data[["target", "sum"]] = grouped.sum()[["target", "value"]].sort_values("value")
            table_data["average"] = grouped.mean()["value"]
            table_data["min"] = grouped.min()["value"]
            table_data["max"] = grouped.max()["value"]
            table_data["count"] = grouped.count()["value"]
            model = DataFrameModel(table_data)
        else:
            model = DataFrameModel(data)
        self.table_view.setModel(model)


class StackedBarsTab(QTabWidget):
    output_options = ["income", "outcome"]
    grouping_options = {
        "Year": ["year"],
        "Month": ["year", "month"],
        "Week": ["year", "week"],
        "Day": ["year", "month", "day"],
    }

    def __init__(self):
        super().__init__()

        self.group_by = ["year"]
        self.current_output_option = "income"

        self.analyzer = DataAnalyzer()
        self.canvas = StackedBarsCanvas(y_axis_title="Amount (EUR)")

        self.output_selector = QComboBox()
        self.output_selector.addItems(self.output_options)

        self.threshold_line = FloatLineEdit()
        self.threshold_line.setText("100")
        self.threshold_value = 100
        self.threshold_value_is_valid = True

        self.grouping_option_selector = QComboBox()
        self.grouping_option_selector.addItems(list(self.grouping_options.keys()))

        self._set_layout()
        self._set_connections()

    def _set_layout(self):
        self.layout = QVBoxLayout()

        grouping_layout = QHBoxLayout()
        grouping_layout.addWidget(QLabel("Grouping"))
        grouping_layout.addWidget(self.grouping_option_selector)

        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output"))
        output_layout.addWidget(self.output_selector)

        threshold_value_layout = QHBoxLayout()
        threshold_value_layout.addWidget(QLabel("Threshold"))
        threshold_value_layout.addWidget(self.threshold_line)

        self.layout.addLayout(grouping_layout)
        self.layout.addLayout(output_layout)
        self.layout.addLayout(threshold_value_layout)
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

    def _set_connections(self):
        self.grouping_option_selector.currentIndexChanged.connect(self._grouping_option_changed)
        self.output_selector.currentIndexChanged.connect(self._output_option_changed)
        self.threshold_line.textChanged.connect(self._handle_threshold_value_changed)

    def _grouping_option_changed(self):
        option_text = self.grouping_option_selector.currentText()
        self.group_by = self.grouping_options[option_text]

    def _output_option_changed(self):
        self.current_output_option = self.output_selector.currentText()

    def _handle_threshold_value_changed(self):
        self.threshold_value, self.threshold_value_is_valid = self.threshold_line.get_value()

    def show_data(self, data: pd.DataFrame):

        if self.threshold_value_is_valid:
            if self.current_output_option == "income":
                data_to_analyze = data[data.value > 0]
            else:
                data_to_analyze = data[data.value < 0]
                data_to_analyze["value"] = abs(data_to_analyze["value"])

            pivot_table = self.analyzer.calculate_pivot_table(data_to_analyze,
                                                              group_by=self.group_by,
                                                              threshold=self.threshold_value)

            if pivot_table.shape[0] > 0:
                self.canvas.plot(pivot_table)
            else:
                self.canvas.clear()
