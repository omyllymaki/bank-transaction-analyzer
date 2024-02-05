import argparse
import sys
import time

import pandas as pd
from PyQt5.QtWidgets import QApplication

from src.config_manager import ConfigManager
from src.gui.main_window import MainWindow
from src.utils import profile_decorator

pd.options.mode.chained_assignment = None  # default='warn'

PROFILE = False


@profile_decorator("profile_data")
def profile_main_window(config_manager):
    return MainWindow(config_manager)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default="config.json", help="Path to configuration.")
    args = parser.parse_args()
    print(f"Reading configuration from {args.config}")
    config_manager = ConfigManager(args.config)
    app = QApplication(sys.argv)
    mw = profile_main_window(config_manager) if PROFILE else MainWindow(config_manager)
    mw.show()
    app.exec()


if __name__ == "__main__":
    main()
