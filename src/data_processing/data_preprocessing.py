import hashlib
import logging
import re
from typing import List, Dict, Tuple

import pandas as pd

from constants import COLUMNS
from src.data_processing.data_analysis import categorize, extract_labels
from src.data_processing.loaders.new_nordea_loader import NewNordeaLoader
from src.data_processing.loaders.nordea_loader import NordeaLoader
from src.data_processing.transformers.new_nordea_transformer import NewNordeaTransformer
from src.data_processing.transformers.nordea_transformer import NordeaTransformer
from src.data_processing.validation import validate

logger = logging.getLogger(__name__)


class Bank:

    def __init__(self, loader, transformer, regexp_pattern):
        self.loader = loader
        self.transformer = transformer
        self.regexp_pattern = regexp_pattern

    def get_data(self, path):
        return self.transformer.transform(self.loader.load([path]))


class DataPreprocessor:

    def __init__(self):
        self.banks = [
            Bank(NordeaLoader(), NordeaTransformer(), "Tapahtumat"),
            Bank(NewNordeaLoader(), NewNordeaTransformer(), "KÄYTTÖTILI"),
        ]

    def get_data(self,
                 file_paths: List[str],
                 notes: Dict[str, str],
                 drop_data: Dict[str, list] = None,
                 categories: dict = None,
                 labels: dict = None) -> Tuple[pd.DataFrame, pd.DataFrame]:

        combined_transformed_data = pd.DataFrame()
        for path in file_paths:
            bank_found = False
            for bank in self.banks:
                if re.search(bank.regexp_pattern, path):
                    bank_data = bank.get_data(path)
                    combined_transformed_data = pd.concat([combined_transformed_data, bank_data], ignore_index=True)
                    bank_found = True
                    break

            if not bank_found:
                raise Exception(f"Unknown bank for file: {path}")

        validate(combined_transformed_data)
        preprocessed_data = self.preprocess_data(combined_transformed_data)
        if categories:
            preprocessed_data["category"] = categorize(preprocessed_data, categories)
        else:
            preprocessed_data["category"] = "NA"

        if labels:
            labels = extract_labels(preprocessed_data, labels)
            preprocessed_data["labels"] = [" ; ".join(l) for l in labels]
        else:
            preprocessed_data["labels"] = "NA"

        preprocessed_data["notes"] = ""
        for event_id, note in notes.items():
            preprocessed_data.loc[preprocessed_data.id == event_id, "notes"] = note

        filtered_data, removed_data = self.drop_rows(preprocessed_data, drop_data=drop_data)
        return filtered_data, removed_data

    @staticmethod
    def preprocess_data(data: pd.DataFrame) -> pd.DataFrame:
        str_columns = ['account_number', 'message', 'event', 'target']
        data[str_columns] = data[str_columns].fillna("NA")
        data['year'] = data['time'].dt.year
        data['month'] = data['time'].dt.month
        data['week'] = data['time'].dt.isocalendar().week
        data['day'] = data['time'].dt.day
        s = (data['account_number'] + data['target'] + data['value'].astype(str) + data['time'].astype(str)).values
        data['id'] = [hashlib.md5(i.encode('utf-8')).hexdigest() for i in s]
        data_processed = data.sort_values('time')
        return data_processed

    @staticmethod
    def drop_rows(data: pd.DataFrame, drop_data: Dict[str, list]) -> Tuple[pd.DataFrame, pd.DataFrame]:
        data_removed = pd.DataFrame(columns=data.columns)
        for column_name, row_name in drop_data.items():
            i = data[column_name].isin(row_name)
            data_removed = pd.concat([data_removed, data.loc[i]])
            data = data.loc[~i]
        return data, data_removed
