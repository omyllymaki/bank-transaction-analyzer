from typing import List
import pandas as pd


class TransactionClassifier:

    def __init__(self, extractor, model, categories):
        self.extractor = extractor
        self.model = model
        self.categories = categories

    def predict(self, df: pd.DataFrame) -> List[str]:
        X = self.extractor.extract(df)
        predictions = self.model.predict(X)
        return [self.categories[p] for p in predictions]
