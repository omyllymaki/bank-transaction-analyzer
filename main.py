import argparse
import sys

import pandas as pd
from PyQt5.QtWidgets import QApplication

from src.gui.main_window import MainWindow
from src.utils import load_json, load_configurations, save_json

pd.options.mode.chained_assignment = None  # default='warn'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default="configurations/config.json", help="Path to configuration.")
    args = parser.parse_args()
    print(f"Reading configuration from {args.config}")
    config = load_json(args.config)

    app = QApplication(sys.argv)
    mw = MainWindow(config)
    mw.show()
    app.exec()

    # Save the notes when the app is closed
    current_notes = load_json(config["paths"]["notes"])
    new_notes = mw.main_view.tab_handler.get_notes()
    combined_notes = {**current_notes, **new_notes}
    save_json(config["paths"]["notes"], combined_notes)

if __name__ == "__main__":
    main()
