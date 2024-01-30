from datetime import datetime
from typing import List

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCalendarWidget, QLabel, QLineEdit, QPushButton, QFileDialog, \
    QInputDialog, QHBoxLayout

from src.gui.widgets import FloatLineEdit, TextLineEdit


class SideBar(QWidget):
    load_data_signal = pyqtSignal(list)
    filter_values_changed_signal = pyqtSignal(dict)
    new_category_created_signal = pyqtSignal(tuple)
    new_label_created_signal = pyqtSignal(tuple)

    def __init__(self, default_data_dir):
        super().__init__()
        self.default_data_dir = default_data_dir
        self.min_date_selector = QCalendarWidget(self)
        self.max_date_selector = QCalendarWidget(self)
        self.target_line = TextLineEdit(self)
        self.account_number_line = TextLineEdit(self)
        self.message_line = TextLineEdit(self)
        self.event_line = TextLineEdit(self)
        self.category_line = TextLineEdit(self)
        self.labels_line = TextLineEdit(self)
        self.id_line = TextLineEdit(self)
        self.notes_line = TextLineEdit(self)
        self.is_duplicate_line = QLineEdit(self)
        self.min_value_line = FloatLineEdit(self)
        self.max_value_line = FloatLineEdit(self)
        self.load_button = QPushButton('Load data')
        self.create_label_button = QPushButton('Create label from existing filters')
        self.create_category_button = QPushButton('Create category from existing filters')
        self._set_layout()
        self._set_connections()

    def _create_hbox_with_text(self, text, widget):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(text, widget))
        layout.addWidget(widget)
        return layout

    def _set_layout(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel('Min date'))
        self.layout.addWidget(self.min_date_selector)
        self.layout.addWidget(QLabel('Max date'))
        self.layout.addWidget(self.max_date_selector)
        layout = QHBoxLayout()
        layout.addWidget(QLabel('Min value'))
        layout.addWidget(self.min_value_line)
        layout.addWidget(QLabel('Max value'))
        layout.addWidget(self.max_value_line)
        self.layout.addLayout(layout)

        hbox_widgets = [
            ("Target:", self.target_line),
            ("Account:", self.account_number_line),
            ("Message:", self.message_line),
            ("Event:", self.event_line),
            ("Category:", self.category_line),
            ("Labels:", self.labels_line),
            ("Id:", self.id_line),
            ("Notes:", self.notes_line),
            ("Is duplicate:", self.is_duplicate_line)
        ]
        for item in hbox_widgets:
            layout = self._create_hbox_with_text(item[0], item[1])
            self.layout.addLayout(layout)

        self.layout.addWidget(self.load_button)
        self.layout.addWidget(self.create_label_button)
        self.layout.addWidget(self.create_category_button)

    def _set_connections(self):
        self.load_button.clicked.connect(self._handle_load_button_clicked)
        self.create_label_button.clicked.connect(self._handle_create_new_label)
        self.create_category_button.clicked.connect(self._handle_create_new_category)
        self.min_date_selector.selectionChanged.connect(self._handle_filtering_values_changed)
        self.max_date_selector.selectionChanged.connect(self._handle_filtering_values_changed)
        self.min_value_line.returnPressed.connect(self._handle_filtering_values_changed)
        self.max_value_line.returnPressed.connect(self._handle_filtering_values_changed)
        self.target_line.returnPressed.connect(self._handle_filtering_values_changed)
        self.account_number_line.returnPressed.connect(self._handle_filtering_values_changed)
        self.message_line.returnPressed.connect(self._handle_filtering_values_changed)
        self.event_line.returnPressed.connect(self._handle_filtering_values_changed)
        self.category_line.returnPressed.connect(self._handle_filtering_values_changed)
        self.labels_line.returnPressed.connect(self._handle_filtering_values_changed)
        self.id_line.returnPressed.connect(self._handle_filtering_values_changed)
        self.notes_line.returnPressed.connect(self._handle_filtering_values_changed)
        self.is_duplicate_line.returnPressed.connect(self._handle_filtering_values_changed)

    def _handle_load_button_clicked(self):
        file_paths = self._get_file_paths()
        if not file_paths:
            return None
        self.load_data_signal.emit(file_paths)

    def _handle_filtering_values_changed(self):
        filter_values = self.get_filter_values()
        self.filter_values_changed_signal.emit(filter_values)

    def set_dates(self, datetime_min, datetime_max):
        self.min_date_selector.selectionChanged.disconnect(self._handle_filtering_values_changed)
        self.max_date_selector.selectionChanged.disconnect(self._handle_filtering_values_changed)
        self.min_date_selector.setSelectedDate(QtCore.QDate(datetime_min.year, datetime_min.month, datetime_min.day))
        self.max_date_selector.setSelectedDate(QtCore.QDate(datetime_max.year, datetime_max.month, datetime_max.day))
        self.min_date_selector.selectionChanged.connect(self._handle_filtering_values_changed)
        self.max_date_selector.selectionChanged.connect(self._handle_filtering_values_changed)

    def get_filter_values(self):
        return dict(
            min_date=self._get_min_date(),
            max_date=self._get_max_date(),
            target=self.target_line.get_value(),
            account_number=self.account_number_line.get_value(),
            message=self.message_line.get_value(),
            event=self.event_line.get_value(),
            min_value=self.min_value_line.get_value()[0],
            max_value=self.max_value_line.get_value()[0],
            category=self.category_line.get_value(),
            labels=self.labels_line.get_value(),
            id=self.id_line.get_value(),
            notes=self.notes_line.get_value(),
            is_duplicate=self._get_is_duplicate()
        )

    def _handle_create_new_label(self):
        name, ok = QInputDialog.getText(self, 'New label', 'Type the name of new label')
        if not ok:
            return
        new_label_data = self.get_filter_values()
        self.new_label_created_signal.emit((name, new_label_data))

    def _handle_create_new_category(self):
        name, ok = QInputDialog.getText(self, 'New category', 'Type the name of new category')
        if not ok:
            return
        new_category_data = self.get_filter_values()
        self.new_category_created_signal.emit((name, new_category_data))

    def _get_file_paths(self) -> List[str]:
        file_paths, _ = QFileDialog.getOpenFileNames(caption='Choose files for analysis',
                                                     directory=self.default_data_dir)
        return file_paths

    def _get_min_date(self) -> datetime:
        return self.min_date_selector.selectedDate().toPyDate()

    def _get_max_date(self) -> datetime:
        return self.max_date_selector.selectedDate().toPyDate()

    def _get_is_duplicate(self) -> bool:
        text = self.is_duplicate_line.text()
        if text == "True":
            return True
        elif text == "False":
            return False
        else:
            return None
