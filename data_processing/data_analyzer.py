from datetime import datetime
from typing import Dict, List

import pandas as pd


class DataAnalyzer:

    def analyze_data(self,
                     data: pd.DataFrame,
                     min_date: datetime = None,
                     max_date: datetime = None,
                     min_value: float = None,
                     max_value: float = None,
                     target: str = None,
                     account_number: str = None,
                     message: str = None) -> Dict[str, pd.DataFrame]:
        data = self._filter_data(data, min_date, max_date, min_value, max_value, target, account_number, message)
        data = self._calculate_indicators(data)
        data = self._calculate_grouped_data(data)
        return data

    def _calculate_grouped_data(self, data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        output = {
            'by_event': data,
            'by_year': self._group_data_by_columns(data, ['year']),
            'by_year_and_month': self._group_data_by_columns(data, ['year', 'month']),
        }
        return output

    @staticmethod
    def _filter_data(data: pd.DataFrame,
                     min_date: datetime = None,
                     max_date: datetime = None,
                     min_value: float = None,
                     max_value: float = None,
                     target: str = None,
                     account_number: str = None,
                     message: str = None,
                     ) -> pd.DataFrame:
        if min_date is not None:
            data = data[data['time'] >= pd.to_datetime(min_date)]
        if max_date is not None:
            data = data[data['time'] <= pd.to_datetime(max_date)]
        if target is not None:
            data = data[data['target'].str.contains(target.strip(), na=False, case=False)]
        if account_number is not None:
            data = data[data['account_number'].str.contains(account_number.strip(), na=False)]
        if message is not None:
            data = data[data['message'].str.contains(message.strip(), na=False, case=False)]
        if min_value is not None:
            data = data[data['value'] >= min_value]
        if max_value is not None:
            data = data[data['value'] <= max_value]
        return data

    @staticmethod
    def _calculate_indicators(data: pd.DataFrame) -> pd.DataFrame:
        data['cumulative_value'] = data['value'].cumsum()
        data['income'] = data['value']
        data['income'][data['income'] < 0] = 0
        data['outcome'] = data['value']
        data['outcome'][data['outcome'] > 0] = 0
        data['outcome'] = abs(data['outcome'])
        data['cumulative_income'] = data['income'].cumsum()
        data['cumulative_outcome'] = data['outcome'].cumsum()
        data['cumulative_ratio'] = data['cumulative_outcome'] / data['cumulative_income']
        return data

    def _group_data_by_columns(self, data: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        grouped_data = pd.DataFrame()
        grouped_data['total'] = data.groupby(columns).sum()['value']
        grouped_data['income'] = data.groupby(columns).sum()['income']
        grouped_data['outcome'] = data.groupby(columns).sum()['outcome']
        grouped_data['ratio'] = grouped_data['outcome'] / grouped_data['income']
        grouped_data['total_cumulative'] = grouped_data['total'].cumsum()
        return grouped_data
