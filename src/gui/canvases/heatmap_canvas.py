import seaborn as sns
from matplotlib import pyplot as plt

from src.gui.canvases.base_canvas import BaseCanvas

class HeatmapCanvas(BaseCanvas):
    def __init__(self, figure_title='', x_axis_title='', y_axis_title=''):
        super().__init__(figure_title, x_axis_title, y_axis_title, add_grid=False)

    def plot(self, df, lb, ub):
        self.axes.cla()

        sns.heatmap(df, fmt="d", cmap="bwr", yticklabels=True, vmin=lb, vmax=ub, linewidths=0.5,
                                    linecolor='black', ax=self.axes, cbar=False)
        self._update_figure()
