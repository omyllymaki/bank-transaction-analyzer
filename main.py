import argparse
import sys

import pandas as pd
from PyQt5.QtWidgets import QApplication

from src.config_manager import ConfigManager
from src.gui.main_window import MainWindow

pd.options.mode.chained_assignment = None  # default='warn'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default="config.json", help="Path to configuration.")
    args = parser.parse_args()
    print(f"Reading configuration from {args.config}")
    config_manager = ConfigManager(args.config)

    app = QApplication(sys.argv)
    mw = MainWindow(config_manager)
    mw.show()
    app.exec()


if __name__ == "__main__":
    main()
