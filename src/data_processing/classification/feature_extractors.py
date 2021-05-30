from typing import List

import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer


class TextFeatureExtractor:

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            sublinear_tf=True,
            analyzer='char',
            ngram_range=(2, 6),
            max_features=10000,
            min_df=3)

        self.svd = TruncatedSVD(n_components=15)

    def fit(self, sentences: List[str]) -> None:
        X = self.vectorizer.fit_transform(sentences)
        self.svd.fit(X)

    def extract(self, sentences: List[str]) -> np.ndarray:
        X = self.vectorizer.transform(sentences)
        return self.svd.transform(X)


class CategoryFeatureExtractor:

    def __init__(self):
        self.unique_categories = None

    def fit(self, categories: List[str]) -> None:
        self.unique_categories = np.unique(categories).tolist()

    def extract(self, categories: List[str]) -> np.ndarray:
        output = []
        for c in categories:
            if c in self.unique_categories:
                cat = self.unique_categories.index(c) + 1
            else:
                cat = 0
            output.append(cat)
        return np.array(output).reshape(-1, 1)


class FeatureExtractor:

    def __init__(self):
        self.cf_extractor = CategoryFeatureExtractor()
        self.tf_extractor = TextFeatureExtractor()

    def fit(self, df):
        self.cf_extractor.fit(df.event)
        self.tf_extractor.fit(df.target.values)

    def extract(self, df):
        X_cat = self.cf_extractor.extract(df.event.values)
        X_text = self.tf_extractor.extract(df.target.values)
        X_num = df[["value"]].values
        return np.hstack([X_text, X_cat, X_num])
