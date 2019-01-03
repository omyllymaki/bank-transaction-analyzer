from typing import List

import pandas as pd
import re


class DataLoader:

    def load_data(self, file_paths: List[str]) -> pd.DataFrame:
        raw_data_list = []
        for path in file_paths:
            df = pd.read_csv(path, sep='\t', header=1)
            df['account_number'] = self._extract_account_name_from_file_path(path)
            raw_data_list.append(df)
        data = pd.concat(raw_data_list)
        return data

    @staticmethod
    def _extract_account_name_from_file_path(file_path: str) -> str:
        try:
            account_name = re.findall('FI\d+', file_path)[0]
        except:
            account_name = None
        return account_name
