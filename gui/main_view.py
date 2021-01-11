import pandas as pd
from PyQt5.QtWidgets import QWidget, QHBoxLayout

from gui.sidebar import SideBar
from gui.tabs import TabHandler


class MainView(QWidget):
    def __init__(self):
        super().__init__()
        self.sidebar = SideBar()
        self.tab_handler = TabHandler()
        self._set_layout()
        self._set_connections()

    def _set_layout(self):
        layout = QHBoxLayout()
        layout.addLayout(self.sidebar.layout, 1)
        layout.addLayout(self.tab_handler.layout, 6)
        self.setLayout(layout)

    def _set_connections(self):
        self.sidebar.analyze_button_clicked.connect(self._handle_plotting)

    def _handle_plotting(self, data: pd.DataFrame):
        self.tab_handler.show_data(data)
