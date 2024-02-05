from datetime import datetime, date

import numpy as np
import pandas as pd

from src.data_processing.transformers.transformer_interface import TransformerInterface


class NewNordeaTransformer(TransformerInterface):
    mapping = {
        "target": "Otsikko",
        "value": "Määrä",
        "time": "Kirjauspäivä",
        "account_number": "Tilinumero"
    }

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        transformed_data = pd.DataFrame()
        for col_target, col_source in self.mapping.items():
            transformed_data[col_target] = data[col_source]
        transformed_data["value"] = pd.to_numeric(transformed_data["value"].str.replace(',', '.'))
        transformed_data["time"] = pd.to_datetime(transformed_data["time"], errors="coerce", format='%Y/%m/%d')
        transformed_data["message"] = np.nan
        transformed_data["event"] = np.nan
        transformed_data["bank"] = "Nordea (new format)"
        transformed_data = transformed_data.dropna(subset=["time", "value"])
        return transformed_data
