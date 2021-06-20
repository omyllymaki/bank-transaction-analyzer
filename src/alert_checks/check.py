from abc import abstractmethod
from typing import List, Union

import pandas as pd

from src.alert_checks.options import OnFail, Grouping, Aggregation
from src.data_processing.data_filtering import filter_data


class Check:
    ref_values = None
    criteria = None
    name = None
    column = "value"
    on_fail = OnFail.log_error
    description = None

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
    filtering: dict = None
    group_by: Grouping = None
    aggregation: Aggregation = None

    def __init__(self, ):
        super().__init__()

    def pipeline(self, df: pd.DataFrame) -> Union[float, List[float]]:
        if self.filtering:
            df = filter_data(df, **self.filtering)
        if self.group_by:
            df = df.set_index("time").groupby(pd.Grouper(freq=self.group_by.value))
        if self.aggregation:
            df = df.agg(self.aggregation.value)
        return df.fillna(0)[self.column].tolist()
