import re
from typing import List

import pandas as pd

from src.data_processing.loaders.loader_interface import LoaderInterface


class NewNordeaLoader(LoaderInterface):

    def load(self, file_paths: List[str]) -> pd.DataFrame:
        raw_data_list = []
        for path in file_paths:
            df = pd.read_csv(path, sep=';', header=0)
            df["Tilinumero"] = re.findall("TILI (.*) -", path)[0]
            raw_data_list.append(df)
        data = pd.concat(raw_data_list)
        return data