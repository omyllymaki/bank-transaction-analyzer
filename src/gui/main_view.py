import pandas as pd
from PyQt5.QtWidgets import QWidget, QHBoxLayout

from src.gui.sidebar import SideBar
from src.gui.tabs.tab_handler import TabHandler


class MainView(QWidget):
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        config = self.config_manager.get_config()
        self.sidebar = SideBar(config)
        self.tab_handler = TabHandler()
        self._set_layout()
        self._set_connections()

    def _set_layout(self):
        layout = QHBoxLayout()
        layout.addLayout(self.sidebar.layout, 1)
        layout.addLayout(self.tab_handler.layout, 6)
        self.setLayout(layout)

    def _set_connections(self):
        self.sidebar.data_filtered_signal.connect(self._handle_plotting)
        self.sidebar.data_loaded_signal.connect(self._handle_data_loaded)
        self.sidebar.new_category_created_signal.connect(self._handle_new_category_created)
        self.sidebar.new_label_created_signal.connect(self._handle_new_label_created)
        self.tab_handler.tabs["Events"].drop_data_added_signal.connect(self._handle_drop_data_added)

    def _handle_plotting(self, data: pd.DataFrame):
        self.tab_handler.handle_data(data)

    def _handle_data_loaded(self, data: pd.DataFrame):
        self.tab_handler.handle_prefiltered_data(data)

    def _handle_drop_data_added(self, data: tuple):
        name = data[0]
        value = data[1]
        self.config_manager.add_drop_data(name, value)
        self.config_manager.save_config()
        self.sidebar.load_data()

    def _handle_new_category_created(self, data: tuple):
        name = data[0]
        values = data[1]
        self.config_manager.add_category(name, values)
        self._handle_category_or_label_config_updates()

    def _handle_new_label_created(self, data: tuple):
        name = data[0]
        values = data[1]
        self.config_manager.add_label(name, values)
        self._handle_category_or_label_config_updates()

    def _handle_category_or_label_config_updates(self):
        self.config_manager.save_config()
        config = self.config_manager.get_config()
        self.sidebar.set_config(config)
