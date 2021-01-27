from abc import abstractmethod
import pandas as pd

from data_processing.data_parsers.data_validation import validate


class BaseDataParser:
    """
    Base class that needs to be inherited by any DataParser.
    """

    @validate
    def parse(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Parse raw data and validate it.
        @param data: Raw data.
        @return: Parsed data.
        """
        return self._parse(data)

    @abstractmethod
    def _parse(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Parse raw data to specified data format. This needs to be implemented by inheritor.
        @param data: Raw data.
        @return data: Parsed data that needs to pass validation.
        """
        raise NotImplementedError
