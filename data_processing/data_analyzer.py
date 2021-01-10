from typing import List

import pandas as pd


class DataAnalyzer:

    def analyze_data(self,
                     data: pd.DataFrame,
                     group_data_by: List[str] = None) -> pd.DataFrame:

        if data.shape[0] > 0:
            data = self._fill_missing_days(data)
        data = self._calculate_indicators(data)
        if group_data_by is None:
            return self._group_data_by_columns(data, ["day"])
        else:
            return self._group_data_by_columns(data, group_data_by)

    @staticmethod
    def _fill_missing_days(original_data: pd.DataFrame) -> pd.DataFrame:
        data = pd.DataFrame()
        grouped_data = original_data.groupby("time")
        data["value"] = grouped_data["value"].sum()
        data = data.asfreq('D').fillna(0)
        data["year"] = data.index.year
        data["month"] = data.index.month
        data["week"] = data.index.week
        data["day"] = data.index.day
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
