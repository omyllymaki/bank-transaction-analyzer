from abc import ABC, abstractmethod
import pandas as pd


class DataParserInterface(ABC):

    def __init__(self, *args, **kwargs):
        super().__init__()

    @abstractmethod
    def parse(self, data: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError
