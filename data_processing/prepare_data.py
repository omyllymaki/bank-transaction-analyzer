from typing import List, Dict

import pandas as pd

from data_processing.data_filtering import DataFilter
from data_processing.data_preprocessor import DataPreprocessor
from data_processing.validation import validate


def prepare_data(file_paths: List[str],
                 data_loader,
                 data_transformer,
                 drop_data: Dict[str, list] = None) -> pd.DataFrame:
    data_preprocessor = DataPreprocessor()
    data_filter = DataFilter()
    raw_data = data_loader.load(file_paths)
    transformed_data = data_transformer.transform(raw_data)
    validate(transformed_data)
    preprocessed_data = data_preprocessor.process(transformed_data)
    filtered_data = data_filter.filter(preprocessed_data, drop_data=drop_data)
    return filtered_data
