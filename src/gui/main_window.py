from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow

from src.gui.main_view import MainView


class MainWindow(QMainWindow):
    def __init__(self, config_manager):
        super().__init__(flags=Qt.Window)
        self.setWindowTitle(f'Bank Transaction Analyzer')
        self.main_view = MainView(config_manager)
        self.setCentralWidget(self.main_view)
