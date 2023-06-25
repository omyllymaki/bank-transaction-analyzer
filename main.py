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

    # Save the current notes
    df = mw.main_view.tab_handler.tabs['Events'].data[["id", "notes"]]
    df = df[df.notes.str.len() > 0]
    notes_dict = dict(zip(df.id, df.notes))
    save_json(config["paths"]["notes"], notes_dict)

if __name__ == "__main__":
    main()
