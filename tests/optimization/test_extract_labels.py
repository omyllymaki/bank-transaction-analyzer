import os
import random
import timeit
import unittest
from functools import partial
from multiprocessing import Pool

import numpy as np
import pandas as pd

from src.config_manager import ConfigManager, LABELS_KEY
from src.data_processing.data_analysis import extract_labels
from src.data_processing.data_filtering import filter_data
from src.data_processing.data_preprocessing import DataPreprocessor
from tests.optimization.base_test import BaseTest

random.seed(42)


def extract_labels_ref(df: pd.DataFrame, specifications: dict) -> np.array:
    dfc = df.copy()
    dfc.reset_index(inplace=True, drop=True)
    indices_map = {}
    for label, label_specs in specifications.items():
        filtered_data = filter_data(dfc, **label_specs)
        indices_map[label] = filtered_data.index.tolist()

    dfc["labels"] = [[] for r in range(dfc.shape[0])]
    for label, indices in indices_map.items():
        for i in indices:
            dfc["labels"].loc[i].append(label)

    return dfc["labels"].values.tolist()


class TestExtractLabels(BaseTest):

    def test_extract_labels(self):
        label_specs = self.config[LABELS_KEY]
        ref_labels = extract_labels_ref(self.data, label_specs)
        test_labels = extract_labels(self.data, label_specs)
        self.assertListEqual(test_labels, ref_labels)

    def test_extract_labels_performance(self):
        label_specs = self.config[LABELS_KEY]
        time_extract_labels_ref = timeit.timeit(lambda: extract_labels_ref(self.data, label_specs), number=10)
        time_extract_labels = timeit.timeit(lambda: extract_labels(self.data, label_specs), number=10)

        print(f"Time for extract_labels_ref: {time_extract_labels_ref:.5f} seconds")
        print(f"Time for extract_labels: {time_extract_labels:.5f} seconds")

        self.assertLess(time_extract_labels, time_extract_labels_ref)
