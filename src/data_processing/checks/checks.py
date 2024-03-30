from datetime import datetime
from typing import Tuple, Optional, Union

import numpy as np
import pandas as pd

from src.data_processing.checks.base_check import Check
from src.data_processing.data_analysis import fill_by_time
from src.data_processing.data_filtering import filter_data


class StandardCheck(Check):
    """
    Standard check implements check that can be used for many cases. It contains
    - optional filtering
    - optional grouping
    - optional aggregation
    - comparison between calculated values and reference values
    """

    def __init__(self,
                 name: str,
                 filtering: Optional[dict],
                 grouping: Optional[list],
                 aggregation: Optional[str],
                 reference_values: Union[np.array, float],
                 criteria: str):
        self.name = name
        self.filtering = filtering
        self.grouping = grouping
        self.aggregation = aggregation
        self.reference_values = reference_values
        if criteria == "larger":
            self.f_comp = lambda x, y: x > y
        elif criteria == "smaller":
            self.f_comp = lambda x, y: x < y
        elif criteria == "equal":
            self.f_comp = lambda x, y: x == y
        else:
            raise ValueError("Unknown criteria. Options are: 'larger', 'smaller', 'equal'")

    def apply(self, df: pd.DataFrame) -> Tuple[bool, pd.DataFrame]:
        if self.filtering is not None:
            df = filter_data(df, **self.filtering)
        if self.grouping:
            result = df.groupby(self.grouping)["value"]
        else:
            result = df["value"]
        if self.aggregation:
            result = result.aggregate(self.aggregation)

        if not hasattr(result, '__iter__'):
            result = pd.Series([result])
            result.name = "value"

        if result.shape[0] == 0:
            return True, pd.DataFrame()

        passed = self.f_comp(result, self.reference_values)
        all_passed = np.all(passed)
        result = result.to_frame()
        result["reference"] = self.reference_values
        result["passed"] = passed
        return all_passed, result

    def get_name(self) -> str:
        return self.name


class TrendCheck(Check):

    def __init__(self, name, min_threshold, filtering=None):
        self.name = name
        self.min_threshold = min_threshold
        self.filtering = filtering

    def apply(self, df: pd.DataFrame) -> Tuple[bool, pd.DataFrame]:
        if self.filtering is not None:
            df = filter_data(df, **self.filtering)
        results = df.groupby(["year", "month"])["value"].aggregate("sum")
        y = results.values
        if len(y) < 2:
            return True, pd.DataFrame()
        x = np.arange(len(y))
        trend = np.polyfit(x, y, 1)[0]
        passed = trend > self.min_threshold
        output = pd.DataFrame({"value": [trend], "reference": [self.min_threshold], "passed": passed})
        return passed, output

    def get_name(self) -> str:
        return self.name


class MonthlyCountCheck(Check):

    def __init__(self, name, min_count, filtering=None):
        self.name = name
        self.min_count = min_count
        self.filtering = filtering

    def apply(self, df: pd.DataFrame) -> Tuple[bool, pd.DataFrame]:
        if self.filtering is not None:
            df = filter_data(df, **self.filtering)
        df = fill_by_time(df)
        results = df.groupby(["year", "month"])["value"].aggregate(lambda x: (abs(x) > 0).sum())
        results.name = "value"
        results = results.to_frame()
        results["reference"] = self.min_count
        results["passed"] = results.value > self.min_count
        results = results.sort_index(level=['year', 'month'])
        return np.all(results.passed), results

    def get_name(self) -> str:
        return self.name
