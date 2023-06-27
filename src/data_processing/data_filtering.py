import datetime
import re

import pandas as pd
import regex


def filter_data(data: pd.DataFrame,
                min_date: datetime = None,
                max_date: datetime = None,
                min_value: float = None,
                max_value: float = None,
                target: str = None,
                account_number: str = None,
                message: str = None,
                event: str = None,
                category: str = None,
                labels: str = None,
                notes: str = None,
                id: str = None,
                is_duplicate: bool = None
                ) -> pd.DataFrame:
    filtered_data = data.copy()

    filters = [
        [date_min_filter, "time", min_date],
        [date_max_filter, "time", max_date],
        [float_min_filter, "value", min_value],
        [float_max_filter, "value", max_value],
        [string_filter, "target", target],
        [string_filter, "account_number", account_number],
        [string_filter, "message", message],
        [string_filter, "event", event],
        [string_filter, "category", category],
        [string_filter, "labels", labels],
        [string_filter, "notes", notes],
        [string_filter, "id", id],
        [boolean_filter, "is_duplicate", is_duplicate]
    ]

    for f in filters:
        func, col, val = f
        if val is not None:
            filtered_data = func(filtered_data, col, val)
            if filtered_data.empty:
                return filtered_data

    return filtered_data


def date_min_filter(data, filter_by, date):
    return data[data[filter_by] >= pd.to_datetime(date)]


def date_max_filter(data, filter_by, date):
    return data[data[filter_by] <= pd.to_datetime(date)]


def float_min_filter(data, filter_by, value):
    return data[data[filter_by] >= value]


def float_max_filter(data, filter_by, value):
    return data[data[filter_by] <= value]

def boolean_filter(data, filter_by, value):
    return data[data[filter_by] == value]


def string_filter(data, filter_by, pattern):
    return data[data[filter_by].apply(regex_find, args=(pattern.strip(),))]


def regex_find(string, pattern):
    match = regex.search(pattern, string, flags=re.IGNORECASE)
    return match is not None
