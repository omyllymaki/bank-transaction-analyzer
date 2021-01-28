from typing import List

import pandas as pd

from data_processing.loaders.loader_interface import LoaderInterface


class NordeaLoader(LoaderInterface):

    def load(self, file_paths: List[str]) -> pd.DataFrame:
        raw_data_list = []
        for path in file_paths:
            df = pd.read_csv(path, sep='\t', header=1)
            df["Tilinumero"] = pd.read_csv(path, sep='\t', nrows=1, header=None)[1].values[0]
            raw_data_list.append(df)
        data = pd.concat(raw_data_list)
        return data
