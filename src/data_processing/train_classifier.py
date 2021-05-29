import argparse
import os

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import confusion_matrix

from src.data_processing.bank_selection import get_bank
from src.data_processing.classifier import TransactionClassifier
from src.data_processing.prepare_data import prepare_data
from src.utils import load_json, save_pickle

CATEGORIES = [
    "Food & Drink",
    "Shopping",
    "Beauty & Health",
    "Transport",
    "Other"
]

REGEXP_PATTERNS = {
    "Food & Drink": "sale|prisma|citymarket|k market|s market|k supermarket|kylävalinta|lidl|siwa",
    "Shopping": "power|dressmann|clas ohlson|new yorker|hennes mauritz|kirjakauppa|sokos|tokmanni|verkkokauppa|gigantti",
    "Beauty & Health": "apteekki|parturi|specsavers|optikko|instrumentarium",
    "Transport": "vr|taksi|abc|teboil|neste"
}

TRAIN_PROPORTION = 0.7
SHUFFLE = False
DROP_DATA = "../../configurations/drop_data.json"
OUTPUT_PATH = 'classifier.p'


def load_data(path) -> pd.DataFrame:
    files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(".txt")]
    drop_data = load_json(DROP_DATA)
    bank = get_bank("Nordea")
    data = prepare_data(file_paths=files,
                        data_loader=bank.loader,
                        data_transformer=bank.transformer,
                        drop_data=drop_data)
    return data


def add_categories_based_on_regexps(data, regexp_patterns):
    data["y"] = CATEGORIES.index("Other")
    for category, pattern in regexp_patterns.items():
        i_match = data.input.str.contains(pattern, case=False)
        data["y"][i_match] = CATEGORIES.index(category)
    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", default="data", help="Path to data files.")
    args = parser.parse_args()

    df = load_data(args.path)
    df.sort_values(by="time", inplace=True)
    data = pd.DataFrame()
    data["input"] = df.target
    data.dropna(inplace=True)
    data.input = data.input.str.lower()

    data = add_categories_based_on_regexps(data, REGEXP_PATTERNS)

    y = data.y.values
    input_words = data.input.values

    if SHUFFLE:
        i = np.arange(0, len(y))
        np.random.shuffle(i)
        input_words = input_words[i]
        y = y[i]

    n_train = int(TRAIN_PROPORTION * len(y))
    words_train = input_words[:n_train]
    y_train = y[:n_train]
    words_valid = input_words[n_train:]
    y_valid = y[n_train:]

    transformer = TfidfVectorizer(
        sublinear_tf=True,
        analyzer='char',
        ngram_range=(2, 6),
        max_features=50000)

    transformer.fit(words_train)

    X_train = transformer.transform(words_train)
    X_valid = transformer.transform(words_valid)

    weights = 1 / np.sqrt(data.groupby("y").count()).values
    label_weights = {k: v for k, v in enumerate(weights)}

    model = RandomForestClassifier(class_weight=label_weights)
    model.fit(X_train, y_train)

    train_pred = model.predict(X_train)
    print("Train accuracy: ", (y_train == train_pred).mean())

    valid_pred = model.predict(X_valid)
    print("Valid accuracy: ", (y_valid == valid_pred).mean())

    cm = pd.DataFrame(confusion_matrix(y_valid, valid_pred), columns=CATEGORIES, index=CATEGORIES)
    print("Confusion matrix for validation data: \n", cm)

    all_words = data.input.values
    y = data.y.values
    X = transformer.fit_transform(all_words)
    weights = 1 / np.sqrt(data.groupby("y").count()).values
    label_weights = {k: v for k, v in enumerate(weights)}

    final_model = RandomForestClassifier(class_weight=label_weights)
    final_model.fit(X, y)

    classifier = TransactionClassifier(transformer, final_model, CATEGORIES)

    save_pickle(OUTPUT_PATH, classifier)


if __name__ == "__main__":
    main()
