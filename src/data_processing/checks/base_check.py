from abc import abstractmethod
from typing import Tuple

import pandas as pd


class Check:
    """
    Interface for check. This needs bo implemented by actual checks.
    """
    name = ""

    @abstractmethod
    def apply(self, df: pd.DataFrame) -> Tuple[bool, pd.DataFrame]:
        """Apply check.
        Args:
            df: data for checking.

        Returns:
            Tuple[bool, pd.DataFrame]: check passes, results of the check
        """
        raise NotImplementedError

    def __repr__(self):
        return self.name
