import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QComboBox, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget

from src.data_processing.data_analysis import fill_by_time
from src.gui.canvases.heatmap_canvas import HeatmapCanvas
from src.gui.widgets import FloatLineEdit, IntLineEdit


class HeatmapTab(QTabWidget):
    time_grouping_options = {
        "Year": ["year"],
        "Month": ["year", "month"],
        "Week": ["year", "week"],
        "Day": ["year", "month", "day"],
    }
    index_grouping_options = {
        "Target": "target",
        "Category": "category",
    }
    aggregation_options = {
        "Sum": "sum",
        "Count": "count",
    }

    def __init__(self):
        super().__init__()

        self.data = None
        self.pivot_df = None
        self.pivot_df_subset = None

        self.time_grouping_selector = QComboBox()
        self.time_grouping_selector.addItems(list(self.time_grouping_options.keys()))

        self.index_grouping_selector = QComboBox()
        self.index_grouping_selector.addItems(list(self.index_grouping_options.keys()))

        self.aggregation_selector = QComboBox()
        self.aggregation_selector.addItems(list(self.aggregation_options.keys()))

        self.heatmap_canvas = HeatmapCanvas(y_axis_title="", x_axis_title="Year, Month")
        self.heatmap_bounds = FloatLineEdit()
        self.max_rows_to_show = IntLineEdit()
        self.max_rows_to_show.setText("30")

        self._set_layout()
        self._set_connections()

    def _set_layout(self):
        self.layout = QVBoxLayout()

        grouping_layout = QHBoxLayout()
        grouping_layout.addWidget(QLabel("Grouping"))
        grouping_layout.addWidget(self.time_grouping_selector)
        grouping_layout.addWidget(self.index_grouping_selector)
        self.layout.addLayout(grouping_layout)

        aggregation_layout = QHBoxLayout()
        aggregation_layout.addWidget(QLabel("Aggregation"))
        aggregation_layout.addWidget(self.aggregation_selector)
        self.layout.addLayout(aggregation_layout)

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
        self.index_grouping_selector.currentIndexChanged.connect(self._analysis)
        self.time_grouping_selector.currentIndexChanged.connect(self._analysis)
        self.aggregation_selector.currentIndexChanged.connect(self._analysis)
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
        index = self.index_grouping_options[self.index_grouping_selector.currentText()]
        columns = self.time_grouping_options[self.time_grouping_selector.currentText()]
        agg = self.aggregation_options[self.aggregation_selector.currentText()]
        df = fill_by_time(self.data)
        self.pivot_df = df.pivot_table(index=index,
                                       columns=columns,
                                       aggfunc=agg,
                                       fill_value=0,
                                       values="value")
        self.pivot_df.drop("FILLED", inplace=True, errors="ignore")

    def _get_pivot_table_subset(self):
        row_sum = abs(self.pivot_df).sum(axis=1)
        n_rows, is_valid = self.max_rows_to_show.get_value()
        i = np.argsort(row_sum)[-n_rows:]
        self.pivot_df_subset = self.pivot_df.iloc[i]

    def _set_limits(self):
        if not self.pivot_df.empty:
            limit = int(3 * abs(self.pivot_df_subset).mean().mean())
            self.heatmap_bounds.setText(str(limit))

    def _update_canvas(self):
        bound, is_valid = self.heatmap_bounds.get_value()
        self.heatmap_canvas.plot(self.pivot_df_subset, -bound, bound)
