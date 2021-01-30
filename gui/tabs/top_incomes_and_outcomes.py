import pandas as pd
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QComboBox, QSlider, QVBoxLayout, QHBoxLayout, QLabel

from data_processing.data_analyzer import DataAnalyzer
from gui.canvases import BarHorizontalCanvas
from gui.tabs.base_tab import BaseTab


class TopIncomesAndOutComesTab(BaseTab):
    criteria_options = ["sum", "mean", "max"]
    output_options = ["income", "outcome"]
    n_values_to_show = 15

    def __init__(self):
        self.data = None
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

        super().__init__()

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
        self._analyze_and_update_canvas()

    def _output_changed(self):
        self.selected_output = self.output_selector.currentText()
        self._analyze_and_update_canvas()

    def _handle_slider_value_changed(self):
        self.current_slider_value = self.slider.value()
        self._update_canvas()

    def handle_data(self, data: pd.DataFrame):
        self.data = data
        self._analyze_and_update_canvas()

    def _analyze_and_update_canvas(self):
        if self.data is not None:
            incomes, outcomes = self.analyser.calculate_top_incomes_and_outcomes(self.data, self.selected_criteria)
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
