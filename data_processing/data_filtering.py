import datetime
import re
from typing import Dict

import pandas as pd
import regex


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
               event: str = None,
               drop_data: Dict[str, list] = None
               ) -> pd.DataFrame:

        if drop_data is not None:
            data = self._reject_rows(data, drop_data)
        if min_date is not None:
            data = data[data['time'] >= pd.to_datetime(min_date)]
        if max_date is not None:
            data = data[data['time'] <= pd.to_datetime(max_date)]
        if target is not None:
            data = data[data['target'].apply(self.regex_find, args=(target.strip(),))]
        if account_number is not None:
            data = data[data['account_number'].apply(self.regex_find, args=(account_number.strip(),))]
        if message is not None:
            data = data[data['message'].apply(self.regex_find, args=(message.strip(),))]
        if event is not None:
            data = data[data['event'].apply(self.regex_find, args=(event.strip(),))]
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

    @staticmethod
    def regex_find(string, pattern):
        match = regex.search(pattern, string, flags=re.IGNORECASE)
        return match is not None
