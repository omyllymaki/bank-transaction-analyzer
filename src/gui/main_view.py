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
        self.sidebar.analyze_button_clicked.connect(self._handle_plotting)
        self.sidebar.new_indicator_or_category_created.connect(self._handle_new_indicator_created)
        self.tab_handler.tabs["Events"].drop_data_added.connect(self._handle_drop_data_added)

    def _handle_plotting(self, data: pd.DataFrame):
        self.tab_handler.handle_data(data)

    def _handle_new_indicator_created(self):
        self.tab_handler.tabs["Indicators"].load_indicators()

    def _handle_drop_data_added(self):
        self.sidebar.load_data()
