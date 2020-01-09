from typing import Dict

import pandas as pd
from PyQt5.QtWidgets import QWidget, QHBoxLayout

from gui.figures import Plotter
from gui.sidebar import SideBar


class MainView(QWidget):
    def __init__(self):
        super().__init__()
        self.sidebar = SideBar()
        self.plotter = Plotter()
        self._set_layout()
        self._set_connections()

    def _set_layout(self):
        layout = QHBoxLayout()
        layout.addLayout(self.sidebar.layout, 1)
        layout.addLayout(self.plotter.layout, 6)
        self.setLayout(layout)

    def _set_connections(self):
        self.sidebar.analyze_button_clicked.connect(self._handle_plotting)

    def _handle_plotting(self, data: Dict[str, pd.DataFrame]):
        self.plotter.show_data(data)
