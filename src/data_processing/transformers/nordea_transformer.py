from datetime import datetime

import numpy as np
import pandas as pd

from src.data_processing.transformers.transformer_interface import TransformerInterface


class NordeaTransformer(TransformerInterface):
    mapping = {
        "target": "Saaja/Maksaja",
        "message": "Viesti",
        "event": "Tapahtuma",
        "value": "Määrä",
        "time": "Kirjauspäivä",
        "account_number": "Tilinumero"
    }

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        transformed_data = pd.DataFrame()
        for col_target, col_source in self.mapping.items():
            transformed_data[col_target] = data[col_source]
        transformed_data["value"] = pd.to_numeric(transformed_data["value"].str.replace(',', '.'))
        transformed_data["time"] = transformed_data["time"].astype(str)
        transformed_data["time"] = pd.to_datetime(transformed_data["time"], errors="coerce", format='%d.%m.%Y')
        transformed_data["bank"] = "Nordea (old format)"
        return transformed_data


