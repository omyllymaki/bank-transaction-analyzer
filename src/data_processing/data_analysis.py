from functools import partial
from typing import List, Tuple

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


def truncated_pivot_analysis(df, group_by, columns="category", threshold=100, time_fill=True):
    if time_fill:
        df = fill_by_time(df)
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


def forecast_by_daily_means(data: pd.DataFrame, fields: Tuple[str]) -> pd.DataFrame:
    daily_means = data.groupby('day_of_month')[list(fields)].mean().reset_index()

    current_day_of_year = data['day_of_year'].max()
    is_leap_year = data['year'][0] % 4 == 0 and (data['year'][0] % 100 != 0 or data['year'][0] % 400 == 0)
    days_in_year = 366 if is_leap_year else 365
    days_remaining = days_in_year - current_day_of_year

    last_date = pd.to_datetime(data.index.max())
    remaining_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=days_remaining)

    predicted_data = pd.DataFrame({
        'time': remaining_dates,
        'day_of_year': remaining_dates.dayofyear,
        'day_of_month': remaining_dates.day
    })

    predicted_data = predicted_data.merge(daily_means, on='day_of_month', how='left')
    data['predicted'] = False
    predicted_data['predicted'] = True
    combined_data = pd.concat([data, predicted_data], ignore_index=True)

    return combined_data


def yearly_analysis(df_input,
                    fields=("outcome", "income", "total"),
                    forecast_year=None,
                    min_amount_data_for_forecasting=31):
    if df_input.shape[0] == 0:
        return {}
    df = df_input.copy()
    df["year"] = df.index.year
    df["month"] = df.index.month
    df["day_of_year"] = df.index.dayofyear
    df["day_of_month"] = df.index.day

    output = {}
    unique_years = np.unique(df.year)
    for year in unique_years:
        result_filtered = df[df.year == year]
        result_filtered["predicted"] = False
        if (year == forecast_year) and (result_filtered.shape[0] >= min_amount_data_for_forecasting):
            result_filtered = forecast_by_daily_means(result_filtered, fields)
        for i, field in enumerate(fields):
            result_filtered[field + "_cumulative"] = result_filtered[field].cumsum().values
        output[year] = result_filtered

    return output


def fill_by_time(df, time_column="time", freq="D", start=None, end=None):
    if df.empty:
        return df
    if start is None:
        start = df[time_column].min()
    if end is None:
        end = df[time_column].max()
    all_dates = pd.DataFrame({time_column: pd.date_range(start=start, end=end, freq=freq)})
    filled_data = pd.merge(all_dates, df, on=time_column, how="left")

    numeric_columns = filled_data.select_dtypes(include='number').columns
    non_numeric_columns = filled_data.select_dtypes(exclude='number').columns
    filled_data[numeric_columns] = filled_data[numeric_columns].fillna(0)
    filled_data[non_numeric_columns] = filled_data[non_numeric_columns].fillna("FILLED")

    filled_data['year'] = filled_data['time'].dt.year
    filled_data['month'] = filled_data['time'].dt.month
    filled_data['week'] = filled_data['time'].dt.isocalendar().week
    filled_data['day'] = filled_data['time'].dt.day

    return filled_data
