import pandas as pd
from matplotlib.patches import Rectangle
from matplotlib.text import Text

from gui.canvases.base_canvas import BaseCanvas
from gui.canvases.color_generation import generate_colors


class StackedBarsCanvas(BaseCanvas):
    def __init__(self, figure_title='', x_axis_title='', y_axis_title=''):
        super().__init__(figure_title, x_axis_title, y_axis_title)
        self._initialize_figure()

    def plot(self, data: pd.DataFrame):
        self._initialize_figure()
        self.data = data
        colors = generate_colors(data.shape[1], pastel_factor=0.1)
        self.data.plot(kind="bar", ax=self.axes, stacked=True, legend=False, color=colors, edgecolor="black",
                       picker=True)
        for label in self.axes.get_xticklabels():
            label.set_picker(True)

        self.figure.canvas.mpl_connect('pick_event', self._handle_pick)

        self.annotation = self.axes.annotate("", xy=(0, 0), xytext=(0.5, 30), textcoords="offset points",
                                             bbox=dict(boxstyle="round", fc="black", ec="b", lw=2),
                                             arrowprops=dict(arrowstyle="->"))
        self.annotation.set_visible(False)
        self._update_figure()

    def _handle_pick(self, event):
        if isinstance(event.artist, Rectangle):
            self._handle_rectangle_pick(event)

        elif isinstance(event.artist, Text):
            print("Send signal to pie chart canvas")
            # TODO: implement pie chart
        else:
            print("Unknown event")

    def _handle_rectangle_pick(self, event):
        rect = event.artist
        handles, labels = rect.axes.get_legend_handles_labels()

        # Search for your current artist within all plot groups
        labels = [label for h, label in zip(handles, labels) if rect in h.get_children()]

        # Should only be one entry but just double check
        if len(labels) == 1:
            label = labels[0]
        else:
            label = None

        self.annotation.set_visible(True)
        width = rect.get_width()
        height = rect.get_height()
        x = rect.get_x() + width / 2
        y = rect.get_y() + height / 2
        self.annotation.xy = (x, y)
        text = f"{label}: {height:0.0f}"
        self.annotation.set_text(text)
        self.annotation.get_bbox_patch().set_alpha(0.4)
        self.figure.canvas.draw_idle()
