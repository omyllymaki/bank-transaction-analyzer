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
               category: str = None,
               drop_data: Dict[str, list] = None
               ) -> pd.DataFrame:

        filtered_data = data.copy()
        if drop_data is not None:
            filtered_data = self._reject_rows(filtered_data, drop_data)

        filters = [
            [self._date_min_filter, "time", min_date],
            [self._date_max_filter, "time", max_date],
            [self._float_min_filter, "value", min_value],
            [self._float_max_filter, "value", max_value],
            [self._string_filter, "target", target],
            [self._string_filter, "account_number", account_number],
            [self._string_filter, "message", message],
            [self._string_filter, "event", event],
            [self._string_filter, "category", category],
        ]

        for f in filters:
            func, col, val = f
            if val is not None:
                filtered_data = func(filtered_data, col, val)
                if filtered_data.empty:
                    return filtered_data

        return filtered_data

    def _date_min_filter(self, data, filter_by, date):
        return data[data[filter_by] >= pd.to_datetime(date)]

    def _date_max_filter(self, data, filter_by, date):
        return data[data[filter_by] <= pd.to_datetime(date)]

    def _float_min_filter(self, data, filter_by, value):
        return data[data[filter_by] >= value]

    def _float_max_filter(self, data, filter_by, value):
        return data[data[filter_by] <= value]

    def _string_filter(self, data, filter_by, pattern):
        return data[data[filter_by].apply(self.regex_find, args=(pattern.strip(),))]

    @staticmethod
    def _reject_rows(data: pd.DataFrame, drop_data: Dict[str, list]) -> pd.DataFrame:
        for column_name, row_name in drop_data.items():
            data = data.loc[~data[column_name].isin(row_name)]
        return data

    @staticmethod
    def regex_find(string, pattern):
        match = regex.search(pattern, string, flags=re.IGNORECASE)
        return match is not None
