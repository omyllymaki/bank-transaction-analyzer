from typing import List, Union

import numpy as np
import pandas as pd

from alert_checks.error_functions import log_error


class Check:
    expected = None
    comparison_function = None
    name = None
    error_function = log_error

    @classmethod
    def calculate_values(cls, data: pd.DataFrame) -> Union[List[float], float, np.ndarray, pd.Series]:
        raise NotImplementedError
