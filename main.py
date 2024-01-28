import argparse
import cProfile
import logging
import pstats
import sys
import os

import pandas as pd
from PyQt5.QtWidgets import QApplication

from src.config_manager import ConfigManager
from src.gui.main_window import MainWindow

pd.options.mode.chained_assignment = None  # default='warn'

PROFILE = True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default="config.json", help="Path to configuration.")
    args = parser.parse_args()
    print(f"Reading configuration from {args.config}")
    config_manager = ConfigManager(args.config)
    profiler = cProfile.Profile()

    if PROFILE:
        profiler.enable()

    app = QApplication(sys.argv)
    mw = MainWindow(config_manager)
    mw.show()
    app.exec()

    if PROFILE:
        profiler.disable()
        profiler.dump_stats("profile_data")
        stats = pstats.Stats("profile_data")
        stats.sort_stats("cumulative")
        stats.print_stats()
        stats.dump_stats("profile_data.stats")
        os.system("snakeviz profile_data.stats")


if __name__ == "__main__":
    main()
