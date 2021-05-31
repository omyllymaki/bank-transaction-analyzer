import os
import os
import time
from pprint import pprint

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix

from src.data_processing.bank_selection import get_bank
from src.data_processing.classification.classifier import TransactionClassifier
from src.data_processing.classification.feature_extractors import FeatureExtractor
from src.data_processing.classification.parameters import DROP_DATA, CATEGORIES, REGEXP_PATTERNS, TRAIN_PROPORTION, \
    SHUFFLE, OUTPUT_PATH, DATA_PATH
from src.data_processing.prepare_data import prepare_data
from src.utils import load_json, save_pickle


def load_data(path) -> pd.DataFrame:
    files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(".txt")]
    drop_data = load_json(DROP_DATA)
    bank = get_bank("Nordea")
    data = prepare_data(file_paths=files,
                        data_loader=bank.loader,
                        data_transformer=bank.transformer,
                        drop_data=drop_data)
    return data


def add_labels_based_on_regexps(data, regexp_patterns):
    data["true_label"] = CATEGORIES.index("Other")
    for category, pattern in regexp_patterns.items():
        i_match = data.target.str.contains(pattern, case=False)
        print(f"Category {category} matches {i_match.sum()}: ")
        pprint(data["target"][i_match].unique().tolist())
        data["true_label"][i_match] = CATEGORIES.index(category)
    return data


def divide_to_train_and_valid_set(df, train_proportion=0.7, shuffle=False):
    if shuffle:
        df = df.sample(frac=1)
    n_train = int(train_proportion * df.shape[0])
    df_train = df.iloc[:n_train]
    df_valid = df.iloc[n_train:]

    return df_train, df_valid


def main():
    raw_data = load_data(DATA_PATH)

    raw_data.sort_values(by="time", inplace=True)
    df = raw_data[["value", "event"]]
    df["target"] = raw_data["target"].str.lower()
    df.dropna(inplace=True)

    df = add_labels_based_on_regexps(df, REGEXP_PATTERNS)

    df_train, df_valid = divide_to_train_and_valid_set(df, TRAIN_PROPORTION, SHUFFLE)

    t1 = time.time()
    feature_extractor = FeatureExtractor()
    feature_extractor.fit(df_train)
    X_train = feature_extractor.extract(df_train)
    X_valid = feature_extractor.extract(df_valid)
    t2 = time.time()
    print(f"Feature extraction took {t2 - t1} s")

    weights = 1 / np.sqrt(df_train.groupby("true_label").count().target).values
    label_weights = {k: v for k, v in enumerate(weights)}

    t1 = time.time()
    model = RandomForestClassifier(n_estimators=100, class_weight=label_weights)
    model.fit(X_train, df_train.true_label.values)
    t2 = time.time()
    print(f"Model training took {t2 - t1} s")

    t1 = time.time()
    predicted_labels_train = model.predict(X_train)
    predicted_labels_valid = model.predict(X_valid)
    t2 = time.time()
    print(f"Predictions took {t2 - t1} s")

    print("Train accuracy: ", (df_train.true_label.values == predicted_labels_train).mean())
    print("Valid accuracy: ", (df_valid.true_label.values == predicted_labels_valid).mean())

    cm_train = pd.DataFrame(confusion_matrix(df_train.true_label.values, predicted_labels_train),
                            columns=CATEGORIES,
                            index=CATEGORIES)
    cm_valid = pd.DataFrame(confusion_matrix(df_valid.true_label.values, predicted_labels_valid),
                            columns=CATEGORIES,
                            index=CATEGORIES)

    plt.subplot(1, 2, 1)
    sns.heatmap(cm_train / np.sum(cm_train), annot=True, fmt='.2%', cmap='Blues')
    plt.title("Train")
    plt.subplot(1, 2, 2)
    sns.heatmap(cm_valid / np.sum(cm_valid), annot=True, fmt='.2%', cmap='Blues')
    plt.title("Valid")

    feature_extractor.fit(df)
    X = feature_extractor.extract(df)

    weights = 1 / np.sqrt(df.groupby("true_label").count().target).values
    label_weights = {k: v for k, v in enumerate(weights)}

    final_model = RandomForestClassifier(class_weight=label_weights)
    final_model.fit(X, df.true_label)

    classifier = TransactionClassifier(feature_extractor, final_model, CATEGORIES)

    save_pickle(OUTPUT_PATH, classifier)

    plt.show()


if __name__ == "__main__":
    main()
