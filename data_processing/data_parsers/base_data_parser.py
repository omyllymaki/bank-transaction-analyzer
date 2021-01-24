from abc import abstractmethod
import pandas as pd

from data_processing.data_parsers.data_validation import validate


class BaseDataParser:

    def parse_and_validate(self, data: pd.DataFrame) -> pd.DataFrame:
        parsed_data = self.parse(data)
        validate(parsed_data)
        return parsed_data

    @abstractmethod
    def parse(self, data: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError
