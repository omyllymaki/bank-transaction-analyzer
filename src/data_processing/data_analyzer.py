from typing import List, Tuple

import pandas as pd


class DataAnalyzer:

    def calculate_incomes_and_outcomes(self,
                                       data: pd.DataFrame,
                                       group_data_by: List[str] = None) -> pd.DataFrame:

        data = self._separate_incomes_and_outcomes(data)
        if data.shape[0] > 0:
            data = self._fill_missing_days(data)
        data = self._calculate_cumulative_values(data)
        if group_data_by is None:
            return self._group_data_by_columns(data, ["day"])
        else:
            return self._group_data_by_columns(data, group_data_by)

    @staticmethod
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

    @staticmethod
    def calculate_top_incomes_and_outcomes(data: pd.DataFrame,
                                           criteria="sum",
                                           relative=False) -> Tuple[pd.Series, pd.Series]:

        data.target = data.target.str.lower()
        data = data[["target", "value"]]

        if criteria == "mean":
            values = data.groupby(by="target").mean()["value"]
            incomes = values[values > 0]
            outcomes = values[values < 0]
        elif criteria == "sum":
            values = data.groupby(by="target").sum()["value"]
            incomes = values[values > 0]
            outcomes = values[values < 0]
        elif criteria == "max":
            incomes = data.groupby(by="target").max()["value"]
            outcomes = data.groupby(by="target").min()["value"]
        else:
            raise Exception("Unsupported method")

        outcomes = abs(outcomes)

        outcomes = outcomes.sort_values(ascending=False)
        incomes = incomes.sort_values(ascending=False)

        if relative:
            outcomes = outcomes / outcomes.sum()
            incomes = incomes / incomes.sum()

        return incomes, outcomes

    @staticmethod
    def _separate_incomes_and_outcomes(data: pd.DataFrame) -> pd.DataFrame:
        data['income'] = data['value']
        data['income'][data['income'] < 0] = 0
        data['outcome'] = data['value']
        data['outcome'][data['outcome'] > 0] = 0
        data['outcome'] = abs(data['outcome'])
        return data

    @staticmethod
    def _fill_missing_days(original_data: pd.DataFrame) -> pd.DataFrame:
        data = pd.DataFrame()
        grouped_data = original_data.groupby("time")
        data["value"] = grouped_data["value"].sum()
        data["income"] = grouped_data["income"].sum()
        data["outcome"] = grouped_data["outcome"].sum()
        data = data.asfreq('D').fillna(0)
        data["year"] = data.index.year
        data["month"] = data.index.month
        data["week"] = data.index.isocalendar().week
        data["day"] = data.index.day
        return data

    @staticmethod
    def _calculate_cumulative_values(data: pd.DataFrame) -> pd.DataFrame:
        data['cumulative_value'] = data['value'].cumsum()
        data['cumulative_income'] = data['income'].cumsum()
        data['cumulative_outcome'] = data['outcome'].cumsum()
        data['cumulative_ratio'] = data['cumulative_outcome'] / data['cumulative_income']
        return data

    def _group_data_by_columns(self, data: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        grouped_data = pd.DataFrame()
        grouped_data['total'] = data.groupby(columns).sum()['value']
        grouped_data['income'] = data.groupby(columns).sum()['income']
        grouped_data['outcome'] = data.groupby(columns).sum()['outcome']
        grouped_data['ratio'] = grouped_data['outcome'] / grouped_data['income']
        grouped_data['total_cumulative'] = grouped_data['total'].cumsum()
        return grouped_data
