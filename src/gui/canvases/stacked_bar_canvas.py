import pandas as pd
from PyQt5.QtCore import pyqtSignal

from src.gui.canvases.base_bar_canvas import BaseBarCanvas
from src.gui.canvases.color_generation import generate_colors


class StackedBarsCanvas(BaseBarCanvas):
    data_selected_signal = pyqtSignal(tuple)

    def __init__(self, figure_title='', x_axis_title='', y_axis_title=''):
        super().__init__(figure_title, x_axis_title, y_axis_title, add_grid=False)
        self.figure.canvas.mpl_connect('pick_event', self._handle_selection)
        self.colors = None

    def plot(self, data: pd.DataFrame):
        self.axes.cla()
        self.data = data

        self.colors = generate_colors(self.data.shape[1])
        color_map = {target: color for target, color in zip(self.data.columns, self.colors)}

        x = 0
        for _, row in self.data.iterrows():
            values_sum = 0
            for target, value in row.items():
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

    def _handle_selection(self, event):
        if event.mouseevent.button == 3:  # right click
            rectangle = event.artist
            index = int(rectangle.get_x() + rectangle.get_width() / 2)
            data_picked = self.data.iloc[index, :]
            self.data_selected_signal.emit((data_picked, self.colors))
