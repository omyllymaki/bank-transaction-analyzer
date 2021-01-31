from typing import List

import numpy as np
from mpldatacursor import datacursor

from gui.canvases.base_canvas import BaseCanvas


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
