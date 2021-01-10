from typing import Dict

import pandas as pd
from PyQt5.QtWidgets import QWidget, QHBoxLayout

from gui.tabs import TabHandler
from gui.sidebar import SideBar


class MainView(QWidget):
    def __init__(self):
        super().__init__()
        self.sidebar = SideBar()
        self.plotter = TabHandler()
        self._set_layout()
        self._set_connections()

    def _set_layout(self):
        layout = QHBoxLayout()
        layout.addLayout(self.sidebar.layout, 1)
        layout.addLayout(self.plotter.layout, 6)
        self.setLayout(layout)

    def _set_connections(self):
        self.sidebar.analyze_button_clicked.connect(self._handle_plotting)

    def _handle_plotting(self, data: pd.DataFrame):
        self.plotter.show_data(data)
