import os
from os import listdir

import matplotlib.pyplot as plt
import pandas as pd
from mpldatacursor import datacursor

from analyses.color_generation import generate_colors
from config import DROP_DATA
from data_processing.load_clean_prefilter_data import load_clean_and_prefilter_data

# Path where txt files can be found
PATH = "./data"


def calculate_pivot_table(df, threshold=0.1):
    df_pivot = df.pivot_table(columns='target',
                              index=["year", "month"],
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


def plot_pivot_as_stacked_bar(df, title=""):
    colors = generate_colors(df.shape[1], pastel_factor=0.1)
    df.plot(kind="bar", stacked=True, legend=False, color=colors, edgecolor="black")
    datacursor(formatter='{label}'.format, display='multiple', draggable=True)
    plt.title(title)


files = [os.path.join(PATH, f) for f in listdir(PATH) if f.endswith(".txt")]
data = load_clean_and_prefilter_data(files, DROP_DATA)

incomes = data[data.value > 0]
outcomes = data[data.value < 0]
outcomes["value"] = abs(outcomes["value"])

df_pivot_incomes = calculate_pivot_table(incomes)
df_pivot_outcomes = calculate_pivot_table(outcomes)
plot_pivot_as_stacked_bar(df_pivot_incomes, "Income")
plot_pivot_as_stacked_bar(df_pivot_outcomes, "outcome")
plt.show()
