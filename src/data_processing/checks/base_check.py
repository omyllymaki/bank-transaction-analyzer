from abc import abstractmethod
from typing import Tuple

import pandas as pd


class Check:
    """
    Interface for check. This needs bo implemented by actual checks.
    """

    @abstractmethod
    def apply(self, df: pd.DataFrame) -> Tuple[bool, pd.DataFrame]:
        """
        Apply check.

        Args:
            df: data for checking.

        Returns:
            Tuple[bool, pd.DataFrame]: check passes, results of the check.
            Results of the check needs to be dataframe, other than that it doesn't have to have any specific format.
        """
        raise NotImplementedError

    @abstractmethod
    def get_name(self) -> str:
        """
        Get name of the check.
        """
        raise NotImplementedError

    def __repr__(self):
        return self.get_name()
