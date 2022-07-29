import argparse
import sys

import pandas as pd
from PyQt5.QtWidgets import QApplication

from src.gui.main_window import MainWindow

pd.options.mode.chained_assignment = None  # default='warn'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default="personal_configurations/new_config.json",
                        help="Path to configuration.")
    args = parser.parse_args()
    app = QApplication(sys.argv)
    mw = MainWindow(args.config)
    mw.show()
    app.exec()


if __name__ == "__main__":
    main()
