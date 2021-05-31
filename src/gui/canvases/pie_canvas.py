from typing import List

import numpy as np

from src.gui.canvases.base_canvas import BaseCanvas


class PieCanvas(BaseCanvas):
    def __init__(self, figure_title='', x_axis_title='', y_axis_title='', threshold=0.001):
        super().__init__(figure_title, x_axis_title, y_axis_title)
        self._initialize_figure()
        self.threshold = threshold

    def plot(self, y: np.ndarray, labels: np.ndarray):
        self._initialize_figure()
        i = y > self.threshold
        self.axes.pie(y[i], labels=labels[i], autopct='%1.1f%%')
        self.axes.axis("equal")
        self._update_figure()
