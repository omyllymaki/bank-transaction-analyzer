import pandas as pd

from gui.canvases.base_bar_canvas import BaseBarCanvas
from gui.canvases.color_generation import generate_colors


class StackedBarsCanvas(BaseBarCanvas):
    def __init__(self, figure_title='', x_axis_title='', y_axis_title=''):
        super().__init__(figure_title, x_axis_title, y_axis_title, add_grid=False)
        self._initialize_figure()

    def plot(self, data: pd.DataFrame):
        self._initialize_figure()
        self.data = data

        colors = generate_colors(self.data.shape[1])
        color_map = {target: color for target, color in zip(self.data.columns, colors)}

        x = 0
        for _, row in self.data.iterrows():
            values_sum = 0
            for target, value in row.iteritems():
                if value > 0:
                    self.axes.bar(x,
                                  value,
                                  bottom=values_sum,
                                  label=target,
                                  color=color_map[target],
                                  picker=True,
                                  edgecolor="black")
                    values_sum += value
            x += 1

        x_labels = self.data.index.tolist()
        self._set_xlabels(x_labels)

        self._add_hover()
        self._update_figure()
