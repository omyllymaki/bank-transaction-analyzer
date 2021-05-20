import logging
import os

import pandas as pd

from alert_checks.check import Check
from alert_checks.checker import Checker
from data_processing.bank_selection import get_bank
from data_processing.prepare_data import prepare_data

pd.options.mode.chained_assignment = None  # default='warn'

PATH = "./test_data"

logging.basicConfig(level=logging.INFO)


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
        return df.groupby(["year", "month"]).sum().value

    def is_ok(self, value) -> bool:
        return value < self.ref_val


class LargestOutcome(Check):

    def calculate_values(self, data: pd.DataFrame):
        df = data[data.value < 0]
        df.value = abs(df.value)
        return df.value.max()

    def is_ok(self, value) -> bool:
        return value < self.ref_val


class MonthlyIncomesMean(Check):

    def calculate_values(self, data: pd.DataFrame):
        df = data[data.value > 0]
        return df.groupby(["year", "month"]).value.mean().mean()

    def is_ok(self, value) -> bool:
        return value > self.ref_val


class Duplicates(Check):

    def calculate_values(self, data: pd.DataFrame):
        return data.duplicated().sum()

    def is_ok(self, value) -> bool:
        return value == self.ref_val


def main():
    data = load_data()
    checks = [MonthlyOutcome(1000.0),
              LargestOutcome(1000),
              MonthlyIncomesMean(1000),
              Duplicates(0)]
    checker = Checker()
    checker.run(data, checks)


if __name__ == "__main__":
    main()
