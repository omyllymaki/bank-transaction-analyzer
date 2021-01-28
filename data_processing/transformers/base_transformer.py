from abc import abstractmethod
import pandas as pd

from data_processing.transformers.validation import validate


class BaseTransformer:
    """
    Base class that needs to be inherited by any Transformer.
    """

    @validate
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform raw data to specified data format and validate it.
        @param data: Raw data.
        @return: Transformed data.
        """
        return self._transform(data)

    @abstractmethod
    def _transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform raw data to specified data format; see validation.py for expected data format. This needs to be
        implemented by inheritor.
        @param data: Raw data.
        @return data: Transformed data that needs to pass validation.
        """
        raise NotImplementedError
