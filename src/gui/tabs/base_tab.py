import pandas as pd
from PyQt5.QtWidgets import QTabWidget


class BaseTab(QTabWidget):
    def __init__(self):
        super().__init__()
        self._set_connections()
        self._set_layout()

    def handle_data(self, data: pd.DataFrame):
        raise NotImplementedError

    def _set_layout(self):
        raise NotImplementedError

    def _set_connections(self):
        raise NotImplementedError
