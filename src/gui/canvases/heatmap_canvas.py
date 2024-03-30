import matplotlib.pyplot as plt
import seaborn as sns

from src.gui.canvases.base_canvas import BaseCanvas


class HeatmapCanvas(BaseCanvas):
    def __init__(self, figure_title='', x_axis_title='', y_axis_title=''):
        super().__init__(figure_title, x_axis_title, y_axis_title, add_grid=False)
        self.df = None
        self.annotation = None

    def plot(self, df, lb, ub):
        self.axes.cla()
        sns.heatmap(df, cmap="bwr", yticklabels=True, vmin=lb, vmax=ub, linewidths=0.5, linecolor='black',
                    ax=self.axes, cbar=False)
        self.df = df
        self._add_hover()
        self._update_figure()

    def _add_hover(self):
        self.annotation = self.axes.annotate("", xy=(0, 0), xytext=(0.5, 30), textcoords="offset points",
                                             bbox=dict(boxstyle="round", fc="yellow", ec="b", lw=2),
                                             arrowprops=dict(arrowstyle="->"))
        self.annotation.set_visible(False)

        self.figure.canvas.mpl_connect('motion_notify_event', self.hover)

    def hover(self, event):
        if self.df is not None:
            if event.inaxes == self.axes:
                row, col = int(round(event.ydata + 0.5)) - 1, int(round(event.xdata + 0.5)) - 1
                if 0 <= row < len(self.df.index) and 0 <= col < len(self.df.columns):
                    value = self.df.iat[row, col]
                    index_label = self.df.index[row]
                    column_label = self.df.columns[col]
                    self.annotation.set_visible(True)
                    x, y = event.xdata, event.ydata
                    self.annotation.xy = (x, y)
                    self.annotation.set_text(f'Value: {value:0.0f}\nRow: {index_label}\nColumn: {column_label}')
                else:
                    self.annotation.set_visible(False)
            else:
                self.annotation.set_visible(False)
            self.figure.canvas.draw_idle()
