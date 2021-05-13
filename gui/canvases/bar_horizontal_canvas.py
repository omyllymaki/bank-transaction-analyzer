from typing import List

import numpy as np

from gui.canvases.base_canvas import BaseCanvas


class BarHorizontalCanvas(BaseCanvas):
    def __init__(self, figure_title='', x_axis_title='', y_axis_title=''):
        super().__init__(figure_title, x_axis_title, y_axis_title)
        self._initialize_figure()

    def plot(self, y: np.ndarray, x_labels: List[str]):
        self._initialize_figure()
        y_plot = self.axes.barh(x_labels, y, color='b')
        self._update_figure()
