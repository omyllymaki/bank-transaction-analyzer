import pandas as pd
from PyQt5.QtWidgets import QWidget, QHBoxLayout

from src.gui.sidebar import SideBar
from src.gui.tabs.tab_handler import TabHandler
from src.utils import load_configurations


class MainView(QWidget):
    def __init__(self, config):
        super().__init__()
        self.orig_config = config
        self._update_config()
        self.sidebar = SideBar(self.updated_config)
        self.tab_handler = TabHandler(self.updated_config)
        self._set_layout()
        self._set_connections()

    def _set_layout(self):
        layout = QHBoxLayout()
        layout.addLayout(self.sidebar.layout, 1)
        layout.addLayout(self.tab_handler.layout, 6)
        self.setLayout(layout)

    def _set_connections(self):
        self.sidebar.analyze_button_clicked.connect(self._handle_plotting)
        self.sidebar.new_indicator_created.connect(self._handle_new_indicator_created)
        self.tab_handler.tabs["Events"].drop_data_added.connect(self._handle_drop_data_added)

    def _handle_plotting(self, data: pd.DataFrame):
        self.tab_handler.handle_data(data)

    def _update_config(self):
        self.updated_config = {**self.orig_config, **load_configurations(self.orig_config["paths"])}

    def _handle_new_indicator_created(self):
        self._update_config()
        self.tab_handler.update_config(self.updated_config)

    def _handle_drop_data_added(self):
        self._update_config()
        self.sidebar.config = self.updated_config
        self.sidebar.load_data()

