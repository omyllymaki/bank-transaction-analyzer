from typing import List

import numpy as np
from mpldatacursor import datacursor

from gui.canvases.base_canvas import BaseCanvas


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
