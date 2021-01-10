from abc import abstractmethod
from datetime import datetime
from typing import List

import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib import pyplot
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from mpldatacursor import datacursor


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
        self._initialize_figure()

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
        self.figure.subplots_adjust(bottom=0.3)
        self.canvas.draw()

    @abstractmethod
    def plot(self, *args):
        raise NotImplementedError


class DoubleBarCanvas(BaseCanvas):
    def __init__(self, figure_title='', x_axis_title='', y_axis_title='', y1_label="", y2_label=""):
        super().__init__(figure_title, x_axis_title, y_axis_title)
        self.y1_label = y1_label
        self.y2_label = y2_label
        self._initialize_figure()

    def plot(self, y1: np.ndarray, y2: np.ndarray, x_labels: List[str] = None):
        income_mean = [np.mean(y1) for k in y1]
        outcome_mean = [np.mean(y2) for k in y2]
        x = np.array([k for k in range(len(y1))])
        if x_labels is None:
            x_labels = ['' for k in y1]

        n = int(x.shape[0] / 15)
        if n == 0:
            n = 1
        x_subset = x[::n]
        x_labels_subset = x_labels[::n]

        self._initialize_figure()
        y1_plot = self.axes.bar(x - 0.1, y1, width=0.2, color='b', label=self.y1_label)
        self.axes.plot(x, income_mean, 'b--')
        y2_plot = self.axes.bar(x + 0.1, y2, width=0.2, color='r', label=self.y2_label)
        self.axes.plot(x, outcome_mean, 'r--')
        self.axes.set_xticks(x_subset)
        self.axes.set_xticklabels(x_labels_subset, rotation=-60)
        datacursor(y1_plot, hover=True, formatter='{height:.0f} EUR'.format)
        datacursor(y2_plot, hover=True, formatter='{height:.0f} EUR'.format)
        self.axes.legend()
        self._update_figure()


class BarCanvas(BaseCanvas):
    def __init__(self, figure_title='', x_axis_title='', y_axis_title=''):
        super().__init__(figure_title, x_axis_title, y_axis_title)
        self._initialize_figure()

    def plot(self, ratio: np.ndarray, x_labels: List[str]):
        ratio_mean = [np.mean(ratio) for k in ratio]
        x = np.array([k for k in range(len(ratio))])

        n = int(x.shape[0] / 15)
        if n == 0:
            n = 1
        x_subset = x[::n]
        x_labels_subset = x_labels[::n]

        self._initialize_figure()
        ratio_plot = self.axes.bar(x, ratio, width=0.2, color='b')
        self.axes.plot(x, ratio_mean, 'b--')
        self.axes.set_xticks(x_subset)
        self.axes.set_xticklabels(x_labels_subset, rotation=-60)
        datacursor(ratio_plot, hover=True, formatter='{height:.2f}'.format)
        self._update_figure()


class IncomeAndOutcomeLineCanvas(BaseCanvas):
    def __init__(self, figure_title='', x_axis_title='', y_axis_title=''):
        super().__init__(figure_title, x_axis_title, y_axis_title)
        self._initialize_figure()

    def plot(self, x: List[datetime], income: np.ndarray, outcome: np.ndarray):
        self._initialize_figure()
        income_plot = self.axes.plot(x, income, 'b.', label='Income')
        outcome_plot = self.axes.plot(x, outcome, 'r.', label='Outcome')
        self.axes.legend()
        self._update_figure()


class ProfitLineCanvas(BaseCanvas):
    def __init__(self, figure_title='', x_axis_title='', y_axis_title=''):
        super().__init__(figure_title, x_axis_title, y_axis_title)
        self._initialize_figure()

    def plot(self, x: List[datetime], ratio: np.ndarray):
        self._initialize_figure()
        ratio_plot = self.axes.plot(x, ratio, 'b.')
        self._update_figure()
