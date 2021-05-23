from typing import List

import numpy as np

from src.gui.canvases.base_bar_canvas import BaseBarCanvas


class BarCanvas(BaseBarCanvas):
    def __init__(self, figure_title='', x_axis_title='', y_axis_title=''):
        super().__init__(figure_title, x_axis_title, y_axis_title)
        self._initialize_figure()

    def plot(self, y: np.ndarray, x_labels: List[str], plot_average=True):
        self._initialize_figure()
        self._plot_bar(y, x_labels, width=0.3, color='b', plot_average=plot_average)
        self._update_figure()
