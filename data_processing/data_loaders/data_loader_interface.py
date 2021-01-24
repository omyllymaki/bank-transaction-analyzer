from abc import ABC, abstractmethod
import pandas as pd


class DataLoaderInterface(ABC):

    def __init__(self, *args, **kwargs):
        super().__init__()

    @abstractmethod
    def load_data(self, *args, **kwargs) -> pd.DataFrame:
        raise NotImplementedError
