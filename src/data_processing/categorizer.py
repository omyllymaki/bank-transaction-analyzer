import pandas as pd
import numpy as np

from src.data_processing.data_filtering import filter_data


class Categorizer:

    def __init__(self, specifications: dict):
        self.specifications = specifications

    def categorize(self, df: pd.DataFrame) -> np.array:
        dfc = df.copy()
        dfc.reset_index(inplace=True, drop=True)
        dfc["category"] = "Other"
        for name, filter_values in self.specifications.items():
            filtered = filter_data(dfc, **filter_values)
            dfc["category"].loc[filtered.index.values] = name
        return dfc["category"].values
