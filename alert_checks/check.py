import logging
from abc import abstractmethod
from enum import Enum
from typing import List, Union

import pandas as pd

from data_processing.data_filtering import DataFilter

logger = logging.getLogger(__name__)


class Criteria(Enum):
    larger = lambda _, val, ref: val > ref
    smaller = lambda _, val, ref: val < ref
    equal = lambda _, val, ref: val == ref


class OnFail(Enum):
    log_error = lambda _, msg: logger.error(msg)
    exception = lambda _, msg: Exception(msg)


class Check:
    ref_values = None
    criteria = None
    name = None
    column = "value"
    on_fail = OnFail.log_error

    def __init__(self):
        if self.name is None:
            self.name = self.get_class_name()

    @abstractmethod
    def pipeline(self, df: pd.DataFrame) -> Union[List[float], float]:
        raise NotImplementedError

    @classmethod
    def get_class_name(cls) -> str:
        return cls.__name__

    def __repr__(self):
        return self.name


class StandardCheck(Check):
    filtering = None
    group_by = None
    aggregation = None

    def __init__(self, ):
        super().__init__()

    def pipeline(self, df: pd.DataFrame) -> Union[float, List[float]]:
        if self.filtering:
            df = DataFilter().filter(df, **self.filtering)
        if self.group_by:
            df = df.groupby(self.group_by)
        if self.aggregation:
            df = df.agg(self.aggregation)
        return df[self.column].tolist()

