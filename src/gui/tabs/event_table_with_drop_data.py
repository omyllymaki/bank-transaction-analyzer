from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMenu, QAction

from src.gui.dialog_boxes import show_warning
from src.gui.tabs.event_table import EventTableTab
from src.utils import load_json, save_json


class EventTableWithDropDataTab(EventTableTab):
    drop_data_added_signal = pyqtSignal(tuple)

    def __init__(self):
        super().__init__()

    def contextMenuEvent(self, event):
        if not self.group_by_target:
            self.menu = QMenu(self)
            action = QAction('Add to drop data file', self)
            action.triggered.connect(lambda: self.add_to_drop_data(event))
            self.menu.addAction(action)
            self.menu.popup(QtGui.QCursor.pos())

    def add_to_drop_data(self, event):
        col_index = self.table_view.currentIndex().column()
        row_index = self.table_view.currentIndex().row()
        column = self.table_data_sorted.columns[col_index]
        content = self.table_data_sorted.iloc[row_index, col_index]
        self.drop_data_added_signal.emit((column, content))
