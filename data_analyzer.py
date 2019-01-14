from datetime import datetime
from typing import Dict, List

import pandas as pd


class DataAnalyzer:

    def analyze_data(self,
                     data: pd.DataFrame,
                     min_date: datetime = None,
                     max_date: datetime = None,
                     target: str = None,
                     account_number: str = None) -> Dict[str, pd.DataFrame]:
        data = self._filter_data(data, min_date, max_date, target, account_number)
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
                     target: str = None,
                     account_number: str = None,
                     ) -> pd.DataFrame:
        if min_date:
            data = data[data['time'] > min_date]
        if max_date:
            data = data[data['time'] < max_date]
        if target:
            data = data[data['target'].str.contains(target, na=False)]
        if account_number:
            data = data[data['account_number'].str.contains(account_number, na=False)]
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
        grouped_data['total_cumulative'] = grouped_data['total'].cumsum()
        return grouped_data
