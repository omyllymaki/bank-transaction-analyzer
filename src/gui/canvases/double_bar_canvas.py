from typing import List

import numpy as np

from src.gui.canvases.base_bar_canvas import BaseBarCanvas


class DoubleBarCanvas(BaseBarCanvas):
    def __init__(self, figure_title='', x_axis_title='', y_axis_title='', y1_label="", y2_label=""):
        super().__init__(figure_title, x_axis_title, y_axis_title)
        self.y1_label = y1_label
        self.y2_label = y2_label
        self._initialize_figure()

    def plot(self, y1: np.ndarray, y2: np.ndarray, x_labels: List[str] = None, plot_average=True):
        self._initialize_figure()
        self._plot_bar(y1, x_labels, -0.15, width=0.3, color='b', label=self.y1_label)
        self._plot_bar(y2, x_labels, +0.15, width=0.3, color='r', label=self.y2_label)
        self.axes.legend()
        self._update_figure()
