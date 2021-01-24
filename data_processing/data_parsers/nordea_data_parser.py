from datetime import datetime

import pandas as pd

from data_processing.data_parsers.data_parser_interface import DataParserInterface


class NordeaDataParser(DataParserInterface):

    def parse(self, data: pd.DataFrame) -> pd.DataFrame:
        data_cleaned = pd.DataFrame()
        data_cleaned['target'] = data['Saaja/Maksaja']
        data_cleaned['account_number'] = data['account_number']
        data_cleaned['message'] = data['Viesti']
        data_cleaned['event'] = data['Tapahtuma']
        data_cleaned['value'] = data['Määrä'].apply(self._convert_string_to_float)
        data_cleaned['time'] = data['Kirjauspäivä'].apply(self._convert_string_to_datetime)
        return data_cleaned

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
