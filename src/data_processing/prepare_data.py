import logging
import re
from typing import List, Dict

import pandas as pd

from src.data_processing.data_analysis import categorize
from src.data_processing.data_filtering import filter_data
from src.data_processing.loaders.new_nordea_loader import NewNordeaLoader
from src.data_processing.loaders.nordea_loader import NordeaLoader
from src.data_processing.transformers.new_nordea_transformer import NewNordeaTransformer
from src.data_processing.transformers.nordea_transformer import NordeaTransformer
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
                 drop_data: Dict[str, list] = None,
                 categories: dict = None) -> pd.DataFrame:
    nordea_loader_old_format_loader = NordeaLoader()
    nordea_loader_new_format = NewNordeaLoader()
    nordea_transformer_old_format = NordeaTransformer()
    nordea_transformer_new_format = NewNordeaTransformer()
    old_format_paths, new_format_paths = [], []
    for path in file_paths:
        if re.search("Tapahtumat", path):
            old_format_paths.append(path)
        else:
            new_format_paths.append(path)

    combined_transformed_data = pd.DataFrame(columns=['value', 'time', 'target', 'message', 'event', 'account_number'])
    if len(old_format_paths) > 0:
        raw_data = nordea_loader_old_format_loader.load(old_format_paths)
        transformed_data = nordea_transformer_old_format.transform(raw_data)
        combined_transformed_data = pd.concat([combined_transformed_data, transformed_data])
    if len(new_format_paths) > 0:
        raw_data = nordea_loader_new_format.load(new_format_paths)
        transformed_data = nordea_transformer_new_format.transform(raw_data)
        combined_transformed_data = pd.concat([combined_transformed_data, transformed_data])

    validate(combined_transformed_data)
    preprocessed_data = preprocess_data(combined_transformed_data)
    filtered_data = filter_data(preprocessed_data, drop_data=drop_data)
    if categories:
        filtered_data["category"] = categorize(filtered_data, categories)
    else:
        filtered_data["category"] = "NA"
    return filtered_data
