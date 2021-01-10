from typing import List, Dict

import pandas as pd

from data_processing.data_cleaner import DataCleaner
from data_processing.data_filtering import DataFilter
from data_processing.data_loader import DataLoader


def load_clean_and_prefilter_data(file_paths: List[str],
                                  drop_data: Dict[str, list] = None) -> pd.DataFrame:
    data_loader = DataLoader()
    data_cleaner = DataCleaner()
    data_filter = DataFilter()
    raw_data = data_loader.load_data(file_paths)
    cleaned_data = data_cleaner.clean_data(raw_data)
    filtered_data = data_filter.filter(cleaned_data, drop_data=drop_data)
    return filtered_data
