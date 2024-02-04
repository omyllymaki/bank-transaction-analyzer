from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from functools import partial, wraps
from typing import List

import numpy as np
import pandas as pd

from src.data_processing.data_filtering import filter_data


def calculate_incomes_and_outcomes(data: pd.DataFrame,
                                   group_by: str = None) -> pd.DataFrame:
    data = _separate_incomes_and_outcomes(data)
    data = _calculate_cumulative_values(data)
    if group_by is None:
        return _group_data_by_columns(data, "D")
    else:
        return _group_data_by_columns(data, group_by)


def calculate_pivot_table(df, group_by, columns="category", threshold=100):
    df_pivot = df.pivot_table(columns=columns,
                              index=group_by,
                              aggfunc='sum',
                              fill_value=0,
                              values='value')

    output = []
    for i, row in df_pivot.iterrows():
        important = row[row > threshold]
        rest = row[row <= threshold]
        d = important.to_dict()
        d["REST"] = rest.sum()
        output.append(d)

    df_pivot_processed = pd.DataFrame.from_dict(output)
    df_pivot_processed.index = df_pivot.index
    df_pivot_processed.fillna(0, inplace=True)

    return df_pivot_processed


def _separate_incomes_and_outcomes(data: pd.DataFrame) -> pd.DataFrame:
    data['income'] = data['value']
    data['income'][data['income'] < 0] = 0
    data['outcome'] = data['value']
    data['outcome'][data['outcome'] > 0] = 0
    data['outcome'] = abs(data['outcome'])
    return data


def _calculate_cumulative_values(data: pd.DataFrame) -> pd.DataFrame:
    data['cumulative_value'] = data['value'].cumsum()
    data['cumulative_income'] = data['income'].cumsum()
    data['cumulative_outcome'] = data['outcome'].cumsum()
    data['cumulative_ratio'] = data['cumulative_outcome'] / data['cumulative_income']
    return data


def _group_data_by_columns(data: pd.DataFrame, group_by: str) -> pd.DataFrame:
    data_copy = data.copy()
    grouped_data = pd.DataFrame()
    data_copy.set_index("time", inplace=True)
    grouped_sums = data_copy.groupby(pd.Grouper(freq=group_by)).sum()
    grouped_data['total'] = grouped_sums['value']
    grouped_data['income'] = grouped_sums['income']
    grouped_data['outcome'] = grouped_sums['outcome']
    grouped_data['ratio'] = grouped_data['outcome'] / grouped_data['income']
    grouped_data['total_cumulative'] = grouped_data['total'].cumsum()
    return grouped_data


def _categorize(df: pd.DataFrame, specifications: dict) -> List[str]:
    dfc = df.copy()
    dfc.reset_index(inplace=True, drop=True)
    dfc["category"] = "Other"
    for name, filter_values in specifications.items():
        filtered = filter_data(dfc, **filter_values)
        dfc["category"].loc[filtered.index.values] = name
    return dfc["category"].values.tolist()


def _extract_labels(df: pd.DataFrame, specifications: dict) -> List[List[str]]:
    dfc = df.copy()
    dfc.reset_index(inplace=True, drop=True)
    indices_map = {}
    for label, label_specs in specifications.items():
        filtered_data = filter_data(dfc, **label_specs)
        indices_map[label] = filtered_data.index.tolist()

    index_labels = {index: [] for index in dfc.index}
    for label, indices in indices_map.items():
        for i in indices:
            index_labels[i].append(label)

    return list(index_labels.values())


def extract_labels(df: pd.DataFrame, specifications: dict, n_processes=4) -> List[List[str]]:
    tasks = np.array_split(df, n_processes)
    f_extract_labels = partial(_extract_labels, specifications=specifications)
    with ProcessPoolExecutor() as executor:
        result = executor.map(f_extract_labels, tasks)

    return [item for sublist in result for item in sublist]


def categorize(df: pd.DataFrame, specifications: dict, n_processes=4) -> List[str]:
    tasks = np.array_split(df, n_processes)
    f_categorize = partial(_categorize, specifications=specifications)
    with ProcessPoolExecutor() as executor:
        result = executor.map(f_categorize, tasks)

    return [item for sublist in result for item in sublist]
