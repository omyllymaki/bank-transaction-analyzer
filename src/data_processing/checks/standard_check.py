import logging
from typing import Optional, Tuple, Union

import numpy as np
import pandas as pd

from src.data_processing.checks.base_check import Check
from src.data_processing.data_filtering import filter_data

logger = logging.getLogger(__name__)

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
            result = pd.Series({"value": result})

        if result.shape[0] == 0:
            logger.warning("Result is empty")
            return True, pd.DataFrame()

        passed = self.f_comp(result, self.reference_values)
        all_passed = np.all(passed)
        result = result.to_frame()
        result["reference"] = self.reference_values
        result["passed"] = passed
        return all_passed, result
