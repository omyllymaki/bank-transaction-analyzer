from typing import List

import pandas as pd

from config import DROP_DATA
from data_cleaner import DataCleaner
from data_loader import DataLoader


def load_and_clean_data(file_paths: List[str]) -> pd.DataFrame:
    data_loader = DataLoader()
    data_cleaner = DataCleaner()
    raw_data = data_loader.load_data(file_paths)
    cleaned_data = data_cleaner.clean_data(raw_data, DROP_DATA)
    return cleaned_data
