from abc import abstractmethod
from typing import List

import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib import pyplot
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.patches import Rectangle
from matplotlib.text import Text
from mpldatacursor import datacursor

from gui.color_generation import generate_colors


class BaseCanvas(QWidget):
    def __init__(self, figure_title='', x_axis_title='', y_axis_title='', add_toolbar=True):
        super().__init__()

        self.add_toolbar = add_toolbar
        self.figure_title = figure_title
        self.x_axis_title = x_axis_title
        self.y_axis_title = y_axis_title
        self.figure, self.axes = pyplot.subplots()
        self.canvas = FigureCanvas(self.figure)
        if self.add_toolbar:
            self.toolbar = NavigationToolbar(self.canvas, self)
        else:
            self.toolbar = None
        self._set_layout()
        self._initialize_figure()

    def _update_figure(self):
        if self.toolbar is not None:
            self.toolbar.update()
        self.canvas.draw()

    def _set_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        if self.toolbar is not None:
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

    def plot(self, y1: np.ndarray, y2: np.ndarray, x_labels: List[str] = None, plot_average=True):
        x = np.array([k for k in range(len(y1))])
        if x_labels is None:
            x_labels = ['' for k in y1]

        n = int(x.shape[0] / 15)
        if n == 0:
            n = 1
        x_subset = x[::n]
        x_labels_subset = x_labels[::n]

        self._initialize_figure()
        y1_plot = self.axes.bar(x - 0.15, y1, width=0.3, color='b', label=self.y1_label)
        if plot_average:
            y1_mean = [np.mean(y1) for k in y1]
            self.axes.plot(x, y1_mean, 'b--')
        y2_plot = self.axes.bar(x + 0.15, y2, width=0.3, color='r', label=self.y2_label)
        if plot_average:
            y2_mean = [np.mean(y2) for k in y2]
            self.axes.plot(x, y2_mean, 'r--')
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

    def plot(self, y: np.ndarray, x_labels: List[str], plot_average=True):
        x = np.array([k for k in range(len(y))])

        n = int(x.shape[0] / 15)
        if n == 0:
            n = 1
        x_subset = x[::n]
        x_labels_subset = x_labels[::n]

        self._initialize_figure()
        y_plot = self.axes.bar(x, y, width=0.3, color='b')
        if plot_average:
            y_mean = [np.mean(y) for k in y]
            self.axes.plot(x, y_mean, 'b--')
        self.axes.set_xticks(x_subset)
        self.axes.set_xticklabels(x_labels_subset, rotation=-60)
        datacursor(y_plot, hover=True, formatter='{height:.2f}'.format)
        self._update_figure()


class BarHorizontalCanvas(BaseCanvas):
    def __init__(self, figure_title='', x_axis_title='', y_axis_title=''):
        super().__init__(figure_title, x_axis_title, y_axis_title)
        self._initialize_figure()

    def plot(self, y: np.ndarray, x_labels: List[str]):
        self._initialize_figure()
        y_plot = self.axes.barh(x_labels, y, color='b')
        datacursor(y_plot, hover=True, formatter='{width:.2f}'.format)
        self._update_figure()


class StackedBarsCanvas(BaseCanvas):
    def __init__(self, figure_title='', x_axis_title='', y_axis_title=''):
        super().__init__(figure_title, x_axis_title, y_axis_title)
        self._initialize_figure()

    def plot(self, data: pd.DataFrame):
        self._initialize_figure()
        self.data = data
        colors = generate_colors(data.shape[1], pastel_factor=0.1)
        self.data.plot(kind="bar", ax=self.axes, stacked=True, legend=False, color=colors, edgecolor="black",
                       picker=True)
        for label in self.axes.get_xticklabels():
            label.set_picker(True)

        self.figure.canvas.mpl_connect('pick_event', self._handle_pick)

        self.annotation = self.axes.annotate("", xy=(0, 0), xytext=(0.5, 30), textcoords="offset points",
                                             bbox=dict(boxstyle="round", fc="black", ec="b", lw=2),
                                             arrowprops=dict(arrowstyle="->"))
        self.annotation.set_visible(False)
        self._update_figure()

    def _handle_pick(self, event):
        if isinstance(event.artist, Rectangle):
            self._handle_rectangle_pick(event)

        elif isinstance(event.artist, Text):
            print("Send signal to pie chart canvas")
            # TODO: implement pie chart
        else:
            print("Unknown event")

    def _handle_rectangle_pick(self, event):
        rect = event.artist
        handles, labels = rect.axes.get_legend_handles_labels()

        # Search for your current artist within all plot groups
        labels = [label for h, label in zip(handles, labels) if rect in h.get_children()]

        # Should only be one entry but just double check
        if len(labels) == 1:
            label = labels[0]
        else:
            label = None

        self.annotation.set_visible(True)
        width = rect.get_width()
        height = rect.get_height()
        x = rect.get_x() + width / 2
        y = rect.get_y() + height / 2
        self.annotation.xy = (x, y)
        text = f"{label}: {height:0.0f}"
        self.annotation.set_text(text)
        self.annotation.get_bbox_patch().set_alpha(0.4)
        self.figure.canvas.draw_idle()
