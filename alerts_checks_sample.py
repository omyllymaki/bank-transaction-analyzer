import json
import logging
import os

import pandas as pd

from alert_checks.alert_checking import run_checks
from alert_checks.check_interface import Check
from alert_checks.comparators import is_equal, is_smaller, is_larger
from alert_checks.error_functions import log_error
from data_processing.bank_selection import get_bank
from data_processing.prepare_data import prepare_data

pd.options.mode.chained_assignment = None  # default='warn'

PATH = "./test_data"
CONFIG = "config.json"

logging.basicConfig(level=logging.INFO)


def load_data() -> pd.DataFrame:
    with open(CONFIG) as f:
        config = json.load(f)
    files = [os.path.join(PATH, f) for f in os.listdir(PATH) if f.endswith(".txt")]
    bank = get_bank(config["bank"])
    data = prepare_data(file_paths=files,
                        data_loader=bank.loader,
                        data_transformer=bank.transformer,
                        drop_data=config["drop_data"])
    return data


class MonthlyOutcome(Check):
    expected = 3500.0
    comparison_function = is_smaller
    error_function = log_error
    name = "Monthly outcome"

    def calculate_values(self, data: pd.DataFrame):
        df = data[data.value < 0]
        df.value = abs(df.value)
        return df.groupby(["year", "month"]).sum().value


class LargestOutcome(Check):
    expected = 1000.0
    comparison_function = is_smaller
    error_function = log_error
    name = "Largest outcome"

    def calculate_values(self, data: pd.DataFrame):
        df = data[data.value < 0]
        df.value = abs(df.value)
        return df.value.max()


class MonthlyIncomesMean(Check):
    expected = 1000.0
    comparison_function = is_larger
    error_function = log_error
    name = "Monthly income mean"

    def calculate_values(self, data: pd.DataFrame):
        df = data[data.value > 0]
        return df.groupby(["year", "month"]).value.mean().mean()


class Duplicates(Check):
    expected = 0
    comparison_function = is_equal
    error_function = log_error
    name = "Number of duplicates"

    def calculate_values(self, data: pd.DataFrame):
        return data.duplicated().sum()


def main():
    data = load_data()
    alert_checks = [MonthlyOutcome, LargestOutcome, MonthlyIncomesMean, Duplicates]
    run_checks(data, alert_checks)


if __name__ == "__main__":
    main()
