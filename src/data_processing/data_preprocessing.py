import hashlib
import logging
import re
from typing import List, Dict, Tuple

import numpy as np
import pandas as pd

from src.config_manager import CATEGORIES_KEY, LABELS_KEY, NOTES_KEY
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

    def get_data(self, file_paths: List[str]) -> pd.DataFrame:

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
        return preprocessed_data

    def drop_data(self, data, drop_data):
        filtered_data, removed_data = self.drop_rows(data, drop_data=drop_data)
        return filtered_data, removed_data

    def update_extra_columns(self, data: pd.DataFrame, config: dict):
        categories = config.get(CATEGORIES_KEY)
        labels = config.get(LABELS_KEY)
        notes = config.get(NOTES_KEY)
        self.update_categories(data, categories)
        self.update_labels(data, labels)
        self.update_notes(data, notes)
        self.update_is_duplicate(data)
        return data

    @staticmethod
    def update_is_duplicate(data):
        grouped_by_id = data.groupby("id").count()
        duplicates_ids = np.unique(grouped_by_id[grouped_by_id.target > 1].index)
        data["is_duplicate"] = False
        for duplicate_id in duplicates_ids:
            data['is_duplicate'][data.id == duplicate_id] = True

    @staticmethod
    def update_notes(data, notes):
        data["notes"] = ""
        if notes is not None:
            for event_id, note in notes.items():
                data.loc[data.id == event_id, "notes"] = note

    @staticmethod
    def update_labels(data, labels):
        if labels is not None:
            data_labels = extract_labels(data, labels)
            data["labels"] = [" ; ".join(l) for l in data_labels]
        else:
            data["labels"] = "NA"

    @staticmethod
    def update_categories(data, categories):
        if categories is not None:
            data["category"] = categorize(data, categories)
        else:
            data["category"] = "NA"

    @staticmethod
    def get_ids(data: pd.DataFrame) -> List[str]:
        s = data['account_number'].copy()
        s += " " + data['target']
        s += " " + data['message']
        s += " " + data['account_number']
        s += " " + data['event']
        s += " " + data['value'].astype(str)
        s += " " + data['time'].astype(str)
        return [hashlib.md5(i.encode('utf-8')).hexdigest() for i in s]

    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        str_columns = ['account_number', 'message', 'event', 'target']
        data[str_columns] = data[str_columns].fillna("NA")
        data['year'] = data['time'].dt.year
        data['month'] = data['time'].dt.month
        data['week'] = data['time'].dt.isocalendar().week
        data['day'] = data['time'].dt.day
        data['id'] = self.get_ids(data)
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
