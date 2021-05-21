import logging
from abc import abstractmethod
from collections import Iterable
from typing import Tuple, Union

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

Values = Union[list, float, int, np.ndarray]


class Check:

    def __init__(self, name=None):
        if name is None:
            self.name = self.get_class_name()

    @abstractmethod
    def calculate_values(self, data: pd.DataFrame) -> Tuple[Values, Values]:
        raise NotImplementedError

    @abstractmethod
    def is_ok(self, test_value, ref_value) -> bool:
        raise NotImplementedError

    def on_fail(self, value, ref_val):
        logger.error(f"Check {self.name} doesn't pass: calculated {value}; reference {ref_val}")

    def run(self, data: pd.DataFrame):
        self.calculate_values(data)
        test_values, ref_values = self.calculate_values(data)

        if not isinstance(test_values, Iterable):
            test_values = [test_values]
        if not isinstance(ref_values, Iterable):
            ref_values = [ref_values for _ in range(len(test_values))]

        if len(test_values) != len(ref_values):
            raise Exception("Number of calculated values doesn't match with number of reference values")

        all_values_ok = True
        for value, ref_value in zip(test_values, ref_values):
            is_ok = self.is_ok(value, ref_value)
            logger.debug(f"Test: {is_ok}, {value}, {ref_value}")
            if not is_ok:
                self.on_fail(value, ref_value)
                all_values_ok = False

        return all_values_ok

    @classmethod
    def get_class_name(cls) -> str:
        return cls.__name__
