import os
import timeit
import unittest
from datetime import datetime

import numpy as np
import pandas as pd

from src.data_processing.loaders.nordea_loader import NordeaLoader
from src.data_processing.transformers.nordea_transformer import NordeaTransformer
from src.data_processing.transformers.transformer_interface import TransformerInterface


class NordeaTransformerRef(TransformerInterface):
    mapping = {
        "target": "Saaja/Maksaja",
        "message": "Viesti",
        "event": "Tapahtuma",
        "value": "Määrä",
        "time": "Kirjauspäivä",
        "account_number": "Tilinumero"
    }

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        transformed_data = pd.DataFrame()
        for col_target, col_source in self.mapping.items():
            transformed_data[col_target] = data[col_source]
        transformed_data["value"] = transformed_data["value"].apply(self._convert_string_to_float)
        transformed_data["time"] = transformed_data["time"].astype(str)
        transformed_data["time"] = transformed_data["time"].apply(self._convert_string_to_datetime)
        transformed_data["bank"] = "Nordea (old format)"
        return transformed_data

    @staticmethod
    def _convert_string_to_datetime(date_str: str) -> datetime:
        try:
            return datetime.strptime(date_str, '%d.%m.%Y')
        except ValueError:
            return None

    @staticmethod
    def _convert_string_to_float(value: str) -> float:
        try:
            value_str_dot_decimal = value.replace(',', '.')
        except AttributeError:
            value_str_dot_decimal = value
        value_float = float(value_str_dot_decimal)
        return value_float


class TestNordeaTransformer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        root_path = os.path.abspath(os.path.dirname(__file__))
        data_path = os.path.join(root_path, "../test_data/Tapahtumat_FI12345_2017.txt")
        cls.data = NordeaLoader().load([data_path])

    def test_transform(self):
        df_ref = NordeaTransformerRef().transform(self.data)
        df_test = NordeaTransformer().transform(self.data)

        pd.testing.assert_frame_equal(df_test, df_ref)

    def test_transform_performance(self):
        time_transform_ref = timeit.timeit(lambda: NordeaTransformerRef().transform(self.data), number=10)
        time_transform_test = timeit.timeit(lambda: NordeaTransformer().transform(self.data), number=10)

        print(f"Time for transform ref: {time_transform_ref:.5f} seconds")
        print(f"Time for transform test: {time_transform_test:.5f} seconds")

        self.assertLess(time_transform_test, time_transform_ref)
