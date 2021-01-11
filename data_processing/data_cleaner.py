from datetime import datetime
from typing import Dict

import pandas as pd


class DataCleaner:

    def clean_data(self,
                   data: pd.DataFrame) -> pd.DataFrame:
        data_cleaned = pd.DataFrame()
        data_cleaned['target'] = data['Saaja/Maksaja']
        data_cleaned['account_number'] = data['account_number']
        data_cleaned['message'] = data['Viesti']
        data_cleaned['event'] = data['Tapahtuma']
        data_cleaned['value'] = data['Määrä'].apply(self.convert_string_to_float)
        data_cleaned['time'] = data['Kirjauspäivä'].apply(self.convert_string_to_datetime)
        str_columns = ['account_number', 'message', 'event', 'target']
        data_cleaned[str_columns] = data_cleaned[str_columns].fillna("NA")
        data_cleaned['year'] = data_cleaned['time'].apply(self.get_year)
        data_cleaned['month'] = data_cleaned['time'].apply(self.get_month)
        data_cleaned['week'] = data_cleaned['time'].apply(self.get_week)
        data_cleaned['day'] = data_cleaned['time'].apply(self.get_day)
        data_cleaned = data_cleaned.sort_values('time')
        return data_cleaned

    @staticmethod
    def _reject_rows(data: pd.DataFrame, drop_data: Dict[str, list]):
        for column_name, row_name in drop_data.items():
            data = data.loc[~data[column_name].isin(row_name)]
        return data

    @staticmethod
    def convert_string_to_datetime(date_str: str) -> datetime:
        date_datetime = datetime.strptime(date_str, '%d.%m.%Y')
        return date_datetime

    @staticmethod
    def get_year(date_time: datetime) -> int:
        year = date_time.year
        return year

    @staticmethod
    def get_month(date_time: datetime) -> int:
        month = date_time.month
        return month

    @staticmethod
    def get_week(date_time: datetime) -> int:
        week = date_time.isocalendar()[1]
        return week

    @staticmethod
    def get_day(date_time: datetime) -> int:
        day = date_time.day
        return day

    @staticmethod
    def convert_string_to_float(value: str) -> float:
        value_str_dot_decimal = value.replace(',', '.')
        value_float = float(value_str_dot_decimal)
        return value_float
