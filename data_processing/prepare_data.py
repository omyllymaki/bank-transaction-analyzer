from typing import List, Dict

import pandas as pd

from config import DATA_LOADER, DATA_PARSER
from data_processing.data_filtering import DataFilter
from data_processing.data_preprocessor import DataPreprocessor


def prepare_data(file_paths: List[str],
                 drop_data: Dict[str, list] = None) -> pd.DataFrame:
    data_loader = DATA_LOADER
    data_parser = DATA_PARSER
    data_preprocessor = DataPreprocessor()
    data_filter = DataFilter()

    raw_data = data_loader.load_data(file_paths)
    parsed_data = data_parser.parse(raw_data)
    preprocessed_data = data_preprocessor.process(parsed_data)
    filtered_data = data_filter.filter(preprocessed_data, drop_data=drop_data)
    return filtered_data
