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

COLUMNS = ['value', 'time', 'target', 'message', 'event', 'account_number', 'bank']


class Bank:

    def __init__(self, loader, transformer, regexp_pattern):
        self.loader = loader
        self.transformer = transformer
        self.regexp_pattern = regexp_pattern
        self.paths = []

    def get_data(self):
        if len(self.paths) > 0:
            raw_data = self.loader.load(self.paths)
            return self.transformer.transform(raw_data)
        else:
            return pd.DataFrame(columns=COLUMNS)

    def clear(self):
        self.paths = []


class DataPreprocessor:

    def __init__(self):
        self.banks = [
            Bank(NordeaLoader(), NordeaTransformer(), "Tapahtumat"),
            Bank(NewNordeaLoader(), NewNordeaTransformer(), "KÄYTTÖTILI"),
        ]

    def get_data(self,
                 file_paths: List[str],
                 drop_data: Dict[str, list] = None,
                 categories: dict = None) -> pd.DataFrame:

        for bank in self.banks:
            bank.clear()

        for path in file_paths:
            found_bank = False
            for bank in self.banks:
                if re.search(bank.regexp_pattern, path):
                    bank.paths.append(path)
                    found_bank = True
            if not found_bank:
                raise Exception(f"Unknown bank for file: {path}")

        combined_transformed_data = pd.DataFrame(columns=COLUMNS)
        for bank in self.banks:
            bank_data = bank.get_data()
            combined_transformed_data = pd.concat([combined_transformed_data, bank_data])

        validate(combined_transformed_data)
        preprocessed_data = self.preprocess_data(combined_transformed_data)
        filtered_data = filter_data(preprocessed_data, drop_data=drop_data)
        if categories:
            filtered_data["category"] = categorize(filtered_data, categories)
        else:
            filtered_data["category"] = "NA"
        return filtered_data

    @staticmethod
    def preprocess_data(data: pd.DataFrame) -> pd.DataFrame:
        str_columns = ['account_number', 'message', 'event', 'target']
        data[str_columns] = data[str_columns].fillna("NA")
        data['year'] = data['time'].dt.year
        data['month'] = data['time'].dt.month
        data['week'] = data['time'].dt.isocalendar().week
        data['day'] = data['time'].dt.day
        data_processed = data.sort_values('time')
        return data_processed
