import logging
from typing import List, Dict

import pandas as pd

from src.data_processing.categorizer import Categorizer
from src.data_processing.data_filtering import filter_data
from src.data_processing.validation import validate

logger = logging.getLogger(__name__)


def preprocess_data(data: pd.DataFrame) -> pd.DataFrame:
    str_columns = ['account_number', 'message', 'event', 'target']
    data[str_columns] = data[str_columns].fillna("NA")
    data['year'] = data['time'].dt.year
    data['month'] = data['time'].dt.month
    data['week'] = data['time'].dt.isocalendar().week
    data['day'] = data['time'].dt.day
    data_processed = data.sort_values('time')
    return data_processed


def prepare_data(file_paths: List[str],
                 data_loader,
                 data_transformer,
                 drop_data: Dict[str, list] = None,
                 categorizer: Categorizer = None) -> pd.DataFrame:
    raw_data = data_loader.load(file_paths)
    duplicates = raw_data[raw_data.duplicated(keep=False)]
    n_duplicates = duplicates.shape[0]
    if n_duplicates > 0:
        logger.warning(
            f"Warning: loaded data contains {n_duplicates} duplicate rows. Duplicate rows:\n {duplicates.to_markdown()}")
    transformed_data = data_transformer.transform(raw_data)
    validate(transformed_data)
    preprocessed_data = preprocess_data(transformed_data)
    filtered_data = filter_data(preprocessed_data, drop_data=drop_data)
    if categorizer:
        filtered_data["category"] = categorizer.categorize(filtered_data)
    else:
        filtered_data["category"] = "NA"
    return filtered_data
