import logging
from abc import abstractmethod
from collections import Iterable
from typing import List, Union

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class Check:

    def __init__(self, reference_value, name=None):
        self.ref_val = reference_value
        if name is None:
            self.name = self.get_class_name()

    @abstractmethod
    def calculate_values(self, data: pd.DataFrame) -> Union[List[float], float, np.ndarray, pd.Series]:
        raise NotImplementedError

    @abstractmethod
    def is_ok(self, value) -> bool:
        raise NotImplementedError

    def on_fail(self, value):
        logger.error(f"Check {self.name} doesn't pass: calculated {value}; reference {self.ref_val}")

    def run(self, data: pd.DataFrame):
        values = self.calculate_values(data)
        if not isinstance(values, Iterable):
            values = [values]

        all_values_ok = True
        for value in values:
            is_ok = self.is_ok(value)
            logger.debug(f"Check: {is_ok}, {value}, {self.ref_val}")
            if not is_ok:
                self.on_fail(value)
                all_values_ok = False

        return all_values_ok

    @classmethod
    def get_class_name(cls) -> str:
        return cls.__name__
