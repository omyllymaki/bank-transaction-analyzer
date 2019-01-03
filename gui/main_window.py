from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow

from gui.main_view import MainView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(flags=Qt.Window)
        self.setWindowTitle('Nordea Account Analyzer')
        self.main_view = MainView()
        self.setCentralWidget(self.main_view)
