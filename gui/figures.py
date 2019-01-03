from abc import abstractmethod

import pandas as pd
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib import pyplot
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np


class BaseCanvas(QWidget):
    def __init__(self, figure_title='', x_axis_title='', y_axis_title=''):
        super().__init__()

        self.figure_title = figure_title
        self.x_axis_title = x_axis_title
        self.y_axis_title = y_axis_title
        self.figure, self.axes = pyplot.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self._set_layout()

    def _update_figure(self):
        self.toolbar.update()
        self.canvas.draw()

    def _set_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.toolbar)
        self.setLayout(layout)

    def _initialize_figure(self):
        self.figure.clf()
        self.axes = self.figure.add_subplot(111)
        self.axes.set_title(self.figure_title)
        self.axes.set_xlabel(self.x_axis_title)
        self.axes.set_ylabel(self.y_axis_title)
        self.axes.grid()
        self.canvas.draw()

    @abstractmethod
    def plot(self, *args):
        raise NotImplementedError


class BarPlotCanvas(BaseCanvas):
    def __init__(self, figure_title='', x_axis_title='', y_axis_title=''):
        super().__init__(figure_title, x_axis_title, y_axis_title)
        self._initialize_figure()

    def plot(self, data: pd.DataFrame):
        x_values = data.index
        income = data['income']
        income_mean = [np.mean(income) for k in x_values]
        outcome = data['outcome']
        outcome_mean = [np.mean(outcome) for k in x_values]
        x = np.array([k for k in range(len(income))])

        self._initialize_figure()
        self.axes.bar(x - 0.1, income, width=0.2, color='b', label='Income')
        self.axes.plot(x, income_mean, 'b--')
        self.axes.bar(x + 0.1, outcome, width=0.2, color='r', label='Outcome')
        self.axes.plot(x, outcome_mean, 'r--')
        self.axes.set_xticks(x)
        self.axes.set_xticklabels(x_values, rotation=270)
        self._update_figure()


class LinePlotCanvas(BaseCanvas):
    def __init__(self, figure_title='', x_axis_title='', y_axis_title=''):
        super().__init__(figure_title, x_axis_title, y_axis_title)
        self._initialize_figure()

    def plot(self, data: pd.DataFrame):
        x = data['time']
        self._initialize_figure()
        self.axes.plot(x, data['cumulative_value'], '-')
        self.axes.plot(x, data['cumulative_income'], 'b-', markersize=3, label='Income')
        self.axes.plot(x, data['cumulative_outcome'], 'r-', markersize=3, label='Outcome')
        self._update_figure()
