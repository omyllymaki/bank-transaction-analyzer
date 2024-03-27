from datetime import datetime
from typing import Tuple

import numpy as np
import pandas as pd

from src.data_processing.checks.base_check import Check


class TrendCheck(Check):
    name = "Trend Check"

    def __init__(self, min_threshold):
        self.min_threshold = min_threshold

    def apply(self, df: pd.DataFrame) -> Tuple[bool, pd.DataFrame]:
        results = df.groupby(["year", "month"])["value"].aggregate("sum")
        y = results.values
        x = np.arange(len(y))
        trend = np.polyfit(x, y, 1)[0]
        passed = trend > self.min_threshold
        output = pd.DataFrame({"value": [trend], "reference": [self.min_threshold], "passed": passed})
        return passed, output


class MonthlyCountCheck(Check):
    name = "Monthly count check"

    def __init__(self, min_count):
        self.min_count = min_count

    def apply(self, df: pd.DataFrame) -> Tuple[bool, pd.DataFrame]:
        results = df.groupby(["year", "month"])["value"].aggregate("count")
        results = results.unstack(fill_value=0).unstack()
        current_year = datetime.now().year
        current_month = datetime.now().month
        i1 = results.index.get_level_values('year') > current_year
        i2 = results.index.get_level_values('year') == current_year
        i3 = results.index.get_level_values('month') > current_month
        i_future = i1 | (i2 & i3)
        results = results.loc[~i_future]
        results.name = "value"
        results = results.to_frame()
        results["reference"] = self.min_count
        results["passed"] = results.value > self.min_count
        results = results.sort_index(level=['year', 'month'])
        return np.all(results.passed), results


CUSTOM_CHECKS = [
    TrendCheck(1.0),
    MonthlyCountCheck(0)
]
