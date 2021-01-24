from typing import List

import pandas as pd

from data_processing.data_loaders.data_loader_interface import DataLoaderInterface


class NordeaDataLoader(DataLoaderInterface):

    def load_data(self, file_paths: List[str]) -> pd.DataFrame:
        raw_data_list = []
        for path in file_paths:
            df = pd.read_csv(path, sep='\t', header=1)
            df["account_number"] = pd.read_csv(path, sep='\t', nrows=1, header=None)[1].values[0]
            raw_data_list.append(df)
        data = pd.concat(raw_data_list)
        return data
