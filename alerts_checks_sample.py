import logging
import os

import pandas as pd
import numpy as np

from alert_checks.alert_logging import configure_logging
from alert_checks.check import Check
from alert_checks.checker import Checker
from data_processing.bank_selection import get_bank
from data_processing.prepare_data import prepare_data

pd.options.mode.chained_assignment = None  # default='warn'

PATH = "./test_data"

configure_logging()


def load_data() -> pd.DataFrame:
    files = [os.path.join(PATH, f) for f in os.listdir(PATH) if f.endswith(".txt")]
    bank = get_bank("Nordea")
    data = prepare_data(file_paths=files,
                        data_loader=bank.loader,
                        data_transformer=bank.transformer)
    return data


class MonthlyOutcome(Check):

    def calculate_values(self, data: pd.DataFrame):
        df = data[data.value < 0]
        df.value = abs(df.value)
        return df.groupby(["year", "month"]).sum().value, 1000.0

    def is_ok(self, value, ref_value) -> bool:
        return value < ref_value


class LargestOutcome(Check):

    def calculate_values(self, data: pd.DataFrame):
        df = data[data.value < 0]
        df.value = abs(df.value)
        return df.value.max(), 1000.0

    def is_ok(self, value, ref_value) -> bool:
        return value < ref_value


class MonthlyIncomesMean(Check):

    def calculate_values(self, data: pd.DataFrame):
        df = data[data.value > 0]
        return df.groupby(["year", "month"]).value.mean().mean(), 700.0

    def is_ok(self, value, ref_value) -> bool:
        return value > ref_value


class Duplicates(Check):

    def calculate_values(self, data: pd.DataFrame):
        return data.duplicated().sum(), 0

    def is_ok(self, value, ref_value) -> bool:
        return value == ref_value


class InputDimensions(Check):

    def calculate_values(self, data: pd.DataFrame):
        return data.shape, (100, 10)

    def is_ok(self, value, ref_value) -> bool:
        return value >= ref_value

    def on_fail(self, value, ref_val):
        raise Exception(
            f"Critical error. Input data dimensions do not match with requirements: test {value}; requirement {ref_val}")


class YearlyIncomeAndOutcomeComparison(Check):

    def calculate_values(self, data: pd.DataFrame):
        data = data[data.year > 2016]
        incomes = data[data.value > 0].groupby(["year"]).sum().value
        outcomes = abs(data[data.value < 0].groupby(["year"]).sum().value)
        return incomes, outcomes

    def is_ok(self, value, ref_value) -> bool:
        return value >= ref_value


class MonthlyIncomeTrend(Check):

    def calculate_values(self, data: pd.DataFrame):
        monthly_incomes = data[data.value > 0].groupby(["year", "month"]).sum().value.values
        x = [k for k in range(len(monthly_incomes))]
        slope = np.polyfit(x, monthly_incomes, 1)[0]
        return slope, 0

    def is_ok(self, value, ref_value) -> bool:
        return value >= ref_value


def main():
    data = load_data()
    checks = [InputDimensions(),
              MonthlyOutcome(),
              LargestOutcome(),
              MonthlyIncomesMean(),
              Duplicates(),
              YearlyIncomeAndOutcomeComparison(),
              MonthlyIncomeTrend()]

    checker = Checker()
    checker.run(data, checks)


if __name__ == "__main__":
    main()
