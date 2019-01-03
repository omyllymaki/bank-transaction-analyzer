import sys

from PyQt5.QtWidgets import QApplication

from gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    app.exec()


if __name__ == "__main__":
    main()
