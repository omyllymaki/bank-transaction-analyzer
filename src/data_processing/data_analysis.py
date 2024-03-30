import os
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from functools import partial, wraps
from typing import List, Callable

import numpy as np
import pandas as pd

from src.data_processing.data_filtering import filter_data
from src.data_processing.parallelization import process_df_parallel


def calculate_incomes_and_outcomes(data: pd.DataFrame,
                                   group_by: str = None) -> pd.DataFrame:
    data = _separate_incomes_and_outcomes(data)
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


def extract_labels(df: pd.DataFrame, specifications: dict, n_tasks=None) -> List[List[str]]:
    f_extract_labels = partial(_extract_labels, specifications=specifications)
    results = process_df_parallel(df, f_extract_labels, n_tasks)
    return [item for sublist in results for item in sublist]


def categorize(df: pd.DataFrame, specifications: dict, n_tasks=None) -> List[str]:
    f_categorize = partial(_categorize, specifications=specifications)
    results = process_df_parallel(df, f_categorize, n_tasks)
    return [item for sublist in results for item in sublist]


def yearly_analysis(df_input, fields=("outcome", "income", "total")):
    if df_input.shape[0] == 0:
        return {}
    df = df_input.copy()
    df["year"] = df.index.year
    df["month"] = df.index.month
    df["day_of_year"] = df.index.dayofyear

    output = {}
    unique_years = np.unique(df.year)
    for year in unique_years:
        result_filtered = df[df.year == year]
        for i, field in enumerate(fields):
            result_filtered[field + "_cumulative"] = result_filtered[field].cumsum().values
        output[year] = result_filtered

    return output


def calculate_time_filled_pivot_table(df, index, columns, agg, values, time_column="time", freq="D"):
    all_dates = pd.DataFrame(
        {'time': pd.date_range(start=df[time_column].min(), end=df[time_column].max(), freq=freq)})

    filled_data = pd.merge(all_dates, df, on="time", how="left").fillna(0)
    filled_data['year'] = filled_data['time'].dt.year
    filled_data['month'] = filled_data['time'].dt.month
    filled_data['week'] = filled_data['time'].dt.isocalendar().week
    filled_data['day'] = filled_data['time'].dt.day

    pivot_df = filled_data.pivot_table(index=index,
                                       columns=columns,
                                       aggfunc=agg,
                                       fill_value=0,
                                       values=values)
    pivot_df.drop(0, inplace=True)
    return pivot_df
