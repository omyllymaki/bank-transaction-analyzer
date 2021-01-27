from datetime import datetime

import pandas as pd

from data_processing.data_parsers.base_data_parser import BaseDataParser


class NordeaDataParser(BaseDataParser):
    mapping = {
        "target": "Saaja/Maksaja",
        "message": "Viesti",
        "event": "Tapahtuma",
        "value": "Määrä",
        "time": "Kirjauspäivä",
        "account_number": "Tilinumero"
    }

    def _parse(self, data: pd.DataFrame) -> pd.DataFrame:
        parsed_data = pd.DataFrame()
        for col_target, col_source in self.mapping.items():
            parsed_data[col_target] = data[col_source]
        parsed_data["value"] = parsed_data["value"].apply(self._convert_string_to_float)
        parsed_data["time"] = parsed_data["time"].apply(self._convert_string_to_datetime)
        return parsed_data

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
