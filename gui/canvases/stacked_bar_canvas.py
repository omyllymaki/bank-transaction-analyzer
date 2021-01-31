import pandas as pd

from gui.canvases.base_bar_canvas import BaseBarCanvas
from gui.canvases.color_generation import generate_colors


class StackedBarsCanvas(BaseBarCanvas):
    def __init__(self, figure_title='', x_axis_title='', y_axis_title=''):
        super().__init__(figure_title, x_axis_title, y_axis_title)
        self._initialize_figure()

    def plot(self, data: pd.DataFrame):
        self._initialize_figure()
        self.data = data
        colors = generate_colors(data.shape[1], pastel_factor=0.1)
        self.data.plot(kind="bar",
                       ax=self.axes,
                       stacked=True,
                       legend=False,
                       color=colors,
                       edgecolor="black",
                       picker=True)
        self._add_hover()
        self._update_figure()
