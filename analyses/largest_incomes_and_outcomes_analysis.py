import os
from os import listdir

import matplotlib.pyplot as plt

from data_processing.load_and_clean_data import load_and_clean_data

# Path where txt files can be found
PATH = "./data"

files = [os.path.join(PATH, f) for f in listdir(PATH) if f.endswith(".txt")]
data = load_and_clean_data(files)
data.target = data.target.str.lower()

data_grouped = data.groupby(by=["target"]).sum()
data_grouped = data_grouped

incomes = data_grouped[data_grouped.value > 0]
outcomes = data_grouped[data_grouped.value < 0]
outcomes.value = abs(outcomes.value)

outcomes.sort_values("value", ascending=False, inplace=True)
incomes.sort_values("value", ascending=False, inplace=True)

outcomes["value_relative"] = outcomes.value / outcomes.value.sum()
incomes["value_relative"] = incomes.value / incomes.value.sum()

plt.figure()
plt.subplot(1, 2, 1)
outcomes["value"][:10].plot(kind="barh")
plt.grid()
plt.subplot(1, 2, 2)
incomes["value"][:10].plot(kind="barh")
plt.grid()
