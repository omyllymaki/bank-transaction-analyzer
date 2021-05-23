from datetime import datetime

import pandas as pd


class DataPreprocessor:

    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        data_processed = data.copy()
        str_columns = ['account_number', 'message', 'event', 'target']
        data_processed[str_columns] = data[str_columns].fillna("NA")
        data_processed['year'] = data['time'].apply(self._get_year)
        data_processed['month'] = data_processed['time'].apply(self._get_month)
        data_processed['week'] = data_processed['time'].apply(self._get_week)
        data_processed['day'] = data_processed['time'].apply(self._get_day)
        data_processed = data_processed.sort_values('time')
        return data_processed

    @staticmethod
    def _get_year(date_time: datetime) -> int:
        year = date_time.year
        return year

    @staticmethod
    def _get_month(date_time: datetime) -> int:
        month = date_time.month
        return month

    @staticmethod
    def _get_week(date_time: datetime) -> int:
        week = date_time.isocalendar()[1]
        return week

    @staticmethod
    def _get_day(date_time: datetime) -> int:
        day = date_time.day
        return day
