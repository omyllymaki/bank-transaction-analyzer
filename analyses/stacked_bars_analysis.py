import os
from os import listdir

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle
from matplotlib.text import Text

from analyses.color_generation import generate_colors
from config import DROP_DATA
from data_processing.load_clean_prefilter_data import load_clean_and_prefilter_data

# Path where txt files can be found
PATH = "/data/"
GROUP_BY = ("year")
THRESHOLD = 0.02


def calculate_pivot_table(df, group_by, threshold=0.1):
    df_pivot = df.pivot_table(columns='target',
                              index=group_by,
                              aggfunc='sum',
                              fill_value=0,
                              values='value')

    row_sums = df_pivot.sum(axis=1)
    relative_proportions = df_pivot.divide(row_sums, axis=0)

    output = []
    for i, row in df_pivot.iterrows():
        important = row[relative_proportions.loc[i] > threshold]
        rest = row[relative_proportions.loc[i] <= threshold]
        d = important.to_dict()
        d["REST"] = rest.sum()
        output.append(d)

    df_pivot_processed = pd.DataFrame.from_dict(output)
    df_pivot_processed.index = df_pivot.index
    df_pivot_processed.fillna(0, inplace=True)

    return df_pivot_processed


class Plotter:

    def plot(self, data: pd.DataFrame):
        self.data = data
        colors = generate_colors(data.shape[1], pastel_factor=0.1)
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, gridspec_kw={'width_ratios': [3, 1]})
        self.ax1.grid()
        self.data.plot(kind="bar", ax=self.ax1, stacked=True, legend=False, color=colors, edgecolor="black",
                       picker=True)
        for label in self.ax1.get_xticklabels():
            label.set_picker(True)

        self.fig.canvas.mpl_connect('pick_event', self._handle_pick)

        self.annotation = self.ax1.annotate("", xy=(0, 0), xytext=(0.5, 30), textcoords="offset points",
                                            bbox=dict(boxstyle="round", fc="black", ec="b", lw=2),
                                            arrowprops=dict(arrowstyle="->"))
        self.annotation.set_visible(False)

        self.column_data = self.data.iloc[-1]
        self._update_pie_chart(self.column_data.name)

    def _handle_pick(self, event):
        if isinstance(event.artist, Rectangle):
            self._handle_rectangle_pick(event)

        elif isinstance(event.artist, Text):
            text = event.artist.get_text()
            x_index = eval(text)

            self.ax2.cla()
            self.column_data = self.data.loc[x_index]

            self._update_pie_chart(text)
        else:
            print("Unknown event")

    def _update_pie_chart(self, title):
        self.column_data = self.column_data[self.column_data > 0]
        self.column_data.plot(kind="pie", autopct='%1.0f%%', title=title, ax=self.ax2, fontsize=8)
        self.ax2.axis("equal")
        self.ax2.set_ylabel('')
        self.fig.canvas.draw()

    def _handle_rectangle_pick(self, event):
        rect = event.artist
        handles, labels = rect.axes.get_legend_handles_labels()

        # Search for your current artist within all plot groups
        labels = [label for h, label in zip(handles, labels) if rect in h.get_children()]

        # Should only be one entry but just double check
        if len(labels) == 1:
            label = labels[0]
        else:
            label = None

        self.annotation.set_visible(True)
        width = rect.get_width()
        height = rect.get_height()
        x = rect.get_x() + width / 2
        y = rect.get_y() + height / 2
        self.annotation.xy = (x, y)
        text = f"{label}: {height:0.0f}"
        self.annotation.set_text(text)
        self.annotation.get_bbox_patch().set_alpha(0.4)
        self.fig.canvas.draw_idle()


files = [os.path.join(PATH, f) for f in listdir(PATH) if f.endswith(".txt")]
data = load_clean_and_prefilter_data(files, DROP_DATA)

incomes = data[data.value > 0]
outcomes = data[data.value < 0]
outcomes["value"] = abs(outcomes["value"])

df_pivot_incomes = calculate_pivot_table(incomes, group_by=GROUP_BY, threshold=THRESHOLD)
df_pivot_outcomes = calculate_pivot_table(outcomes, group_by=GROUP_BY, threshold=THRESHOLD)

df = df_pivot_outcomes

plotter = Plotter()
plotter.plot(df)
