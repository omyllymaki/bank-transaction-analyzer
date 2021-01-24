from typing import List, Dict

import pandas as pd

from data_processing.data_parsers.nordea_data_parser import NordeaDataParser
from data_processing.data_filtering import DataFilter
from data_processing.data_loaders.nordea_data_loader import NordeaDataLoader
from data_processing.data_preprocessor import DataPreprocessor


def prepare_data(file_paths: List[str],
                 drop_data: Dict[str, list] = None) -> pd.DataFrame:

    data_loader = NordeaDataLoader()
    data_parser = NordeaDataParser()
    data_preprocessor = DataPreprocessor()
    data_filter = DataFilter()

    raw_data = data_loader.load_data(file_paths)
    parsed_data = data_parser.parse(raw_data)
    preprocessed_data = data_preprocessor.process(parsed_data)
    filtered_data = data_filter.filter(preprocessed_data, drop_data=drop_data)
    return filtered_data
