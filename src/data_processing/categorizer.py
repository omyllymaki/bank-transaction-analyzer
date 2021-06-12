from src.data_processing.data_filtering import DataFilter
import pandas as pd


class Categorizer:

    def __init__(self, specifications: dict):
        self.specifications = specifications
        self.filtering = DataFilter()

    def add_categories(self, df: pd.DataFrame):
        df.reset_index(inplace=True, drop=True)
        df["category"] = "Other"
        for name, filter_values in self.specifications.items():
            filtered = self.filtering.filter(df, **filter_values)
            df["category"].loc[filtered.index.values] = name
