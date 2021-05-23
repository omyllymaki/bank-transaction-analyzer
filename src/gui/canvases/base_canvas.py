from abc import abstractmethod

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib import pyplot
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class BaseCanvas(QWidget):
    def __init__(self, figure_title='', x_axis_title='', y_axis_title='', add_toolbar=True, add_grid=True):
        super().__init__()

        self.add_toolbar = add_toolbar
        self.add_grid = add_grid
        self.figure_title = figure_title
        self.x_axis_title = x_axis_title
        self.y_axis_title = y_axis_title
        self.figure, self.axes = pyplot.subplots()
        self.canvas = FigureCanvas(self.figure)
        if self.add_toolbar:
            self.toolbar = NavigationToolbar(self.canvas, self)
        else:
            self.toolbar = None
        self._set_layout()
        self._initialize_figure()

    def _update_figure(self):
        if self.toolbar is not None:
            self.toolbar.update()
        self.canvas.draw()

    def _set_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        if self.toolbar is not None:
            layout.addWidget(self.toolbar)
        self.setLayout(layout)

    def _initialize_figure(self):
        self.figure.clf()
        self.axes = self.figure.add_subplot(111)
        self.axes.set_title(self.figure_title)
        self.axes.set_xlabel(self.x_axis_title)
        self.axes.set_ylabel(self.y_axis_title)
        if self.add_grid:
            self.axes.grid()
        self.figure.subplots_adjust(bottom=0.3)
        self.canvas.draw()

    def clear(self):
        self._initialize_figure()

    @abstractmethod
    def plot(self, *args):
        raise NotImplementedError
