from typing import List, Dict

import pandas as pd

from config import DATA_LOADER, DATA_TRANSFORMER
from data_processing.data_filtering import DataFilter
from data_processing.data_preprocessor import DataPreprocessor
from data_processing.validation import validate


def prepare_data(file_paths: List[str],
                 drop_data: Dict[str, list] = None) -> pd.DataFrame:
    data_loader = DATA_LOADER
    data_transformer = DATA_TRANSFORMER
    data_preprocessor = DataPreprocessor()
    data_filter = DataFilter()

    raw_data = data_loader.load(file_paths)
    transformed_data = data_transformer.transform(raw_data)
    validate(transformed_data)
    preprocessed_data = data_preprocessor.process(transformed_data)
    filtered_data = data_filter.filter(preprocessed_data, drop_data=drop_data)
    return filtered_data
