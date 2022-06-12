import datetime

import numpy as np
import pandas as pd
import pandas_schema
from pandas_schema import Column
from pandas_schema.validation import CustomElementValidation


class InvalidDataFrame(Exception):
    pass


def check_decimal(x):
    return isinstance(x, float)


def check_datetime(x):
    return isinstance(x, datetime.date)


def check_is_string_or_nan(x):
    return isinstance(x, str) or np.isnan(x)


def validate(data: pd.DataFrame):
    decimal_validation = [CustomElementValidation(lambda x: check_decimal(x), 'is not decimal')]
    datetime_validation = [CustomElementValidation(lambda x: check_datetime(x), 'is not datetime')]
    string_validation = [CustomElementValidation(lambda x: check_is_string_or_nan(x), 'is not string')]
    nan_validation = [CustomElementValidation(lambda x: x is not np.nan, 'this field cannot be NaN')]

    schema = pandas_schema.Schema([
        Column('value', decimal_validation + nan_validation),
        Column('time', datetime_validation + nan_validation),
        Column('bank', string_validation + nan_validation),
        Column('target', string_validation),
        Column('message', string_validation),
        Column('event', string_validation),
        Column('account_number', string_validation),
    ])

    errors = schema.validate(data)
    if len(errors) > 0:
        for error in errors:
            print(error)
        raise InvalidDataFrame("Invalid dataframe!")
