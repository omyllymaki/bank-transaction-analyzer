from datetime import datetime

import pandas as pd

from data_processing.transformers.base_transformer import BaseTransformer


class NordeaTransformer(BaseTransformer):
    mapping = {
        "target": "Saaja/Maksaja",
        "message": "Viesti",
        "event": "Tapahtuma",
        "value": "Määrä",
        "time": "Kirjauspäivä",
        "account_number": "Tilinumero"
    }

    def _transform(self, data: pd.DataFrame) -> pd.DataFrame:
        transformed_data = pd.DataFrame()
        for col_target, col_source in self.mapping.items():
            transformed_data[col_target] = data[col_source]
        transformed_data["value"] = transformed_data["value"].apply(self._convert_string_to_float)
        transformed_data["time"] = transformed_data["time"].apply(self._convert_string_to_datetime)
        return transformed_data

    @staticmethod
    def _convert_string_to_datetime(date_str: str) -> datetime:
        date_datetime = datetime.strptime(date_str, '%d.%m.%Y')
        return date_datetime

    @staticmethod
    def _convert_string_to_float(value: str) -> float:
        try:
            value_str_dot_decimal = value.replace(',', '.')
        except AttributeError:
            value_str_dot_decimal = value
        value_float = float(value_str_dot_decimal)
        return value_float
