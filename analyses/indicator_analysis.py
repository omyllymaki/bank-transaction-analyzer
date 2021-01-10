import os
from os import listdir

import matplotlib.pyplot as plt
import numpy as np

from data_processing.load_clean_prefilter_data import load_clean_and_prefilter_data

# Grouping criteria; by default groups by year and month
GROUP_BY = ["year", "month"]

# Path where txt files can be found
PATH = "./data/"

# Map of indicators that we want to follow
# Key is indicator name
# Value is regexp pattern used to filter all the events with matching criteria
INDICATORS = {
    "VR": "vr",
    "Store": "sale|prisma|citymarket|k market|s market|k supermarket",
    "All": ".*"
}

files = [os.path.join(PATH, f) for f in listdir(PATH) if f.endswith(".txt")]
data = load_clean_and_prefilter_data(files)
data.target = data.target.str.lower()
time_data = data.groupby(GROUP_BY).first()

fig1, axes1 = plt.subplots()
fig2, axes2 = plt.subplots(4, sharex=True)

figure_counter = 0
for i, (indicator, pattern) in enumerate(INDICATORS.items()):
    indicator_data = data[data["target"].str.contains(pattern, na=False, case=False)]
    indicator_data_grouped = indicator_data.groupby(GROUP_BY, dropna=False).sum()
    unique_targets = indicator_data["target"].unique().tolist()

    print(f"Indicator: {indicator}")
    print(f"Found {len(unique_targets)} individual targets: {unique_targets}")

    df = time_data.join(indicator_data_grouped, lsuffix="l_").fillna(0)
    y = df["value"]
    y_avg = np.array([np.mean(y) for _ in range(len(y))])
    x = np.array([k for k in range(len(y))])
    x_labels = df.index.tolist()

    n = int(x.shape[0] / 10)
    if n == 0:
        n = 1
    x_trunc = x[::n]
    x_labels_trunc = x_labels[::n]

    p = axes1.plot(x, y, "-", label=indicator)
    color = p[-1].get_color()
    axes1.set_xticks(x_trunc)
    axes1.set_xticklabels(x_labels_trunc, rotation=-60)

    ax = axes2[figure_counter]
    ax.bar(x, y)
    ax.plot(x, y_avg, linewidth=2.3, color="r")
    ax.set_xticks(x_trunc)
    ax.set_xticklabels(x_labels_trunc, rotation=-60)
    ax.set_title(indicator)
    ax.grid()

    if figure_counter == 3:
        fig2, axes2 = plt.subplots(4, sharex=True)
        figure_counter = 0
    else:
        figure_counter += 1

axes2[-1].set_xticks(x_trunc)
axes2[-1].set_xticklabels(x_labels_trunc, rotation=-60)
axes1.legend()
axes1.grid()
plt.show()
