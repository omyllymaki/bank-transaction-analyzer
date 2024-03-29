import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QComboBox, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget

from src.gui.canvases.heatmap_canvas import HeatmapCanvas
from src.gui.widgets import FloatLineEdit, IntLineEdit


class HeatmapTab(QTabWidget):
    options = ["target", "category"]

    def __init__(self):
        super().__init__()
        self.data = None
        self.pivot_df = None
        self.pivot_df_subset = None
        self.current_output_option = "target"
        self.heatmap_canvas = HeatmapCanvas(y_axis_title="", x_axis_title="Year, Month")
        self.output_selector = QComboBox()
        self.output_selector.addItems(self.options)
        self.heatmap_bounds = FloatLineEdit()
        self.max_rows_to_show = IntLineEdit()
        self.max_rows_to_show.setText("30")

        self._set_layout()
        self._set_connections()

    def _set_layout(self):
        self.layout = QVBoxLayout()

        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output"))
        output_layout.addWidget(self.output_selector)
        self.layout.addLayout(output_layout)

        items_to_show_layout = QHBoxLayout()
        items_to_show_layout.addWidget(QLabel("Max rows to show"))
        items_to_show_layout.addWidget(self.max_rows_to_show)
        self.layout.addLayout(items_to_show_layout)

        bounds_layout = QHBoxLayout()
        bounds_layout.addWidget(QLabel("Bounds"))
        bounds_layout.addWidget(self.heatmap_bounds)
        self.layout.addLayout(bounds_layout)

        self.layout.addWidget(self.heatmap_canvas)
        self.setLayout(self.layout)

    def _set_connections(self):
        self.output_selector.currentIndexChanged.connect(self._analysis)
        self.heatmap_bounds.returnPressed.connect(self._update_canvas)
        self.max_rows_to_show.returnPressed.connect(self._handle_max_rows_to_show_changed)

    def handle_data(self, data: pd.DataFrame):
        self.data = data
        self._analysis()

    def _analysis(self):
        self._calculate_pivot_table()
        self._get_pivot_table_subset()
        self._set_limits()
        self._update_canvas()
    
    def _handle_max_rows_to_show_changed(self):
        self._get_pivot_table_subset()
        self._set_limits()
        self._update_canvas()

    def _calculate_pivot_table(self):
        df = self.data.copy()
        df['year_month'] = list(zip(df['year'], df['month']))
        group_by = self.output_selector.currentText()
        self.pivot_df = df.pivot_table(index=group_by, columns='year_month', aggfunc='sum', fill_value=0,
                                       values="value")

    def _get_pivot_table_subset(self):
        row_sum = abs(self.pivot_df).sum(axis=1)
        n_rows, is_valid = self.max_rows_to_show.get_value()
        i = np.argsort(row_sum)[-n_rows:]
        self.pivot_df_subset = self.pivot_df.iloc[i]

    def _set_limits(self):
        limit = int(3 * abs(self.pivot_df_subset).mean().mean())
        self.heatmap_bounds.setText(str(limit))

    def _update_canvas(self):
        bound, is_valid = self.heatmap_bounds.get_value()
        self.heatmap_canvas.plot(self.pivot_df_subset, -bound, bound)
