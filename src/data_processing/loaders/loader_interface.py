from abc import ABC, abstractmethod
from typing import List

import pandas as pd


class LoaderInterface(ABC):
    """
    Abstract class that needs to be inherited by any Loader.
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def load(self, file_paths: List[str]) -> pd.DataFrame:
        """
        Load data from file paths and return data as pandas DataFrame. This needs to be implemented by inheritor.
        @param file_paths: List of file paths
        @return raw data.
        """
        raise NotImplementedError
