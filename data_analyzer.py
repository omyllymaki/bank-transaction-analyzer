from datetime import datetime
from typing import Dict

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

    @staticmethod
    def _calculate_grouped_data(data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        yearly_data = pd.DataFrame()
        yearly_data['total'] = data.groupby(['year']).sum()['value']
        yearly_data['income'] = data.groupby(['year']).sum()['income']
        yearly_data['outcome'] = data.groupby(['year']).sum()['outcome']
        yearly_data['total_cumulative'] = yearly_data['total'].cumsum()

        monthly_data = pd.DataFrame()
        monthly_data['total'] = data.groupby(['year', 'month']).sum()['value']
        monthly_data['income'] = data.groupby(['year', 'month']).sum()['income']
        monthly_data['outcome'] = data.groupby(['year', 'month']).sum()['outcome']
        monthly_data['total_cumulative'] = monthly_data['total'].cumsum()

        data_grouped_by_target = data.groupby('target', as_index=False).sum()
        data_grouped_by_target = data_grouped_by_target.sort_values('outcome', ascending=False)
        data_grouped_by_target['ratio'] = data_grouped_by_target['outcome'] / data['outcome'].sum()

        output = {
            'by_event': data,
            'by_year': yearly_data,
            'by_year_and_month': monthly_data,
            'by_target': data_grouped_by_target,
        }
        return output
