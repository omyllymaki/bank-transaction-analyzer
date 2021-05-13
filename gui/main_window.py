from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow

from gui.main_view import MainView


class MainWindow(QMainWindow):
    def __init__(self, config):
        super().__init__(flags=Qt.Window)
        self.setWindowTitle('Bank Transaction Analyzer')
        self.main_view = MainView(config)
        self.setCentralWidget(self.main_view)
