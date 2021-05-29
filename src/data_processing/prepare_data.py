import pickle
from typing import List, Dict

import pandas as pd

from src.data_processing.data_filtering import DataFilter
from src.data_processing.data_preprocessor import DataPreprocessor
from src.data_processing.validation import validate
from src.data_processing.classifier import TransactionClassifier


def prepare_data(file_paths: List[str],
                 data_loader,
                 data_transformer,
                 drop_data: Dict[str, list] = None,
                 classifier=None) -> pd.DataFrame:
    data_preprocessor = DataPreprocessor()
    data_filter = DataFilter()
    raw_data = data_loader.load(file_paths)
    transformed_data = data_transformer.transform(raw_data)
    validate(transformed_data)
    preprocessed_data = data_preprocessor.process(transformed_data)
    filtered_data = data_filter.filter(preprocessed_data, drop_data=drop_data)
    if classifier:
        filtered_data["category"] = classifier.predict(filtered_data.target.values)
    else:
        filtered_data["category"] = "Unknown"



    return filtered_data
