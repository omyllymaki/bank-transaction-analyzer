from datetime import datetime, date

import numpy as np
import pandas as pd

from src.data_processing.transformers.transformer_interface import TransformerInterface


class NewNordeaTransformer(TransformerInterface):
    mapping = {
        "target": "Otsikko",
        "value": "Määrä",
        "time": "Kirjauspäivä",
        "account_number": "Tilinumero"
    }

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        transformed_data = pd.DataFrame()
        for col_target, col_source in self.mapping.items():
            transformed_data[col_target] = data[col_source]
        transformed_data["value"] = transformed_data["value"].apply(self._convert_string_to_float)
        transformed_data["time"] = transformed_data["time"].apply(self._convert_string_to_datetime)
        transformed_data["message"] = np.nan
        transformed_data["event"] = np.nan
        transformed_data["bank"] = "Nordea (new format)"
        transformed_data = transformed_data.dropna(subset=["time", "value"])
        return transformed_data

    @staticmethod
    def _convert_string_to_datetime(date_str: str) -> datetime:
        if date_str == "Varaus":
            return datetime.now()
        try:
            return datetime.strptime(date_str, '%d.%m.%Y')
        except ValueError:
            return datetime.strptime(date_str, '%Y/%m/%d')

    @staticmethod
    def _convert_string_to_float(value: str) -> float:
        try:
            value_str_dot_decimal = value.replace(',', '.')
        except AttributeError:
            value_str_dot_decimal = value
        value_float = float(value_str_dot_decimal)
        return value_float
