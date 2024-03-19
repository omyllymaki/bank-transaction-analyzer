from typing import List

import numpy as np

from src.gui.canvases.base_bar_canvas import BaseBarCanvas
from src.gui.canvases.base_canvas import BaseCanvas


class LineCanvas(BaseCanvas):
    def __init__(self, figure_title='', x_axis_title='', y_axis_title=''):
        super().__init__(figure_title, x_axis_title, y_axis_title)

    def clear(self):
        self.axes.cla()
        self._update_figure()

    def plot(self, x: np.ndarray, y: np.ndarray, *args, **kwargs):
        self.axes.grid(True)
        self.axes.plot(x, y, *args, **kwargs)
        self._update_figure()

    def text(self, x, y, text):
        self.axes.text(x, y, text)
        self._update_figure()
