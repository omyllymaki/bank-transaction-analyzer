from abc import abstractmethod, ABC

import pandas as pd


class TransformerInterface(ABC):
    """
    Abstract class that needs to be inherited by any Transformer.
    """

    @abstractmethod
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform raw data to specified data format; see data_processing/validation.py for expected data format.
        This method needs needs to be implemented by inheritor.
        @param data: Raw data.
        @return data: Transformed data that needs to pass validation.
        """
        raise NotImplementedError
