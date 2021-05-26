import pandas as pd
from PyQt5.QtWidgets import QWidget, QHBoxLayout

from src.gui.sidebar import SideBar
from src.gui.tabs.tab_handler import TabHandler


class MainView(QWidget):
    def __init__(self, config):
        super().__init__()
        self.sidebar = SideBar(config)
        self.tab_handler = TabHandler(config)
        self._set_layout()
        self._set_connections()

    def _set_layout(self):
        layout = QHBoxLayout()
        layout.addLayout(self.sidebar.layout, 1)
        layout.addLayout(self.tab_handler.layout, 6)
        self.setLayout(layout)

    def _set_connections(self):
        self.sidebar.all_data_signal.connect(self._handle_non_filtered_data_received)
        self.sidebar.filtered_data_signal.connect(self._handle_filtered_data_received)
        self.sidebar.new_indicator_signal.connect(self._handle_new_indicator_created)

    def _handle_filtered_data_received(self, data: pd.DataFrame):
        self.tab_handler.handle_filtered_data(data)

    def _handle_new_indicator_created(self):
        self.tab_handler.tabs["Indicators"].load_indicators()

    def _handle_non_filtered_data_received(self, data: pd.DataFrame):
        self.tab_handler.handle_non_filtered_data(data)
