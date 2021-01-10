import datetime
from typing import Dict

import pandas as pd


class DataFilter:

    def filter(self,
               data: pd.DataFrame,
               min_date: datetime = None,
               max_date: datetime = None,
               min_value: float = None,
               max_value: float = None,
               target: str = None,
               account_number: str = None,
               message: str = None,
               drop_data: Dict[str, list] = None
               ) -> pd.DataFrame:

        if drop_data is not None:
            data = self._reject_rows(data, drop_data)
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
    def _reject_rows(data: pd.DataFrame, drop_data: Dict[str, list]) -> pd.DataFrame:
        for column_name, row_name in drop_data.items():
            data = data.loc[~data[column_name].isin(row_name)]
        return data
