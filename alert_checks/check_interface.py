from abc import abstractmethod
from typing import List, Union

import pandas as pd
import numpy as np

from alert_checks.error_functions import log_error


class Check:
    expected = None
    comparison_function = None
    name = None
    error_function = log_error

    @abstractmethod
    def calculate_values(self, data: pd.DataFrame) -> Union[List[float], float, np.ndarray, pd.Series]:
        raise NotImplementedError
