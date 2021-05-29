from typing import List


class TransactionClassifier:

    def __init__(self, transformer, model, categories):
        self.transformer = transformer
        self.model = model
        self.categories = categories

    def predict(self, words: List[str]) -> List[str]:
        x = self.transformer.transform(words)
        predictions = self.model.predict(x)
        return [self.categories[p] for p in predictions]
