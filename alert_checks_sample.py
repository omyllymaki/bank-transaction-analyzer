import os

import pandas as pd

from alert_checks.alert_logging import configure_logging
from alert_checks.check import Check, Criteria, StandardCheck
from alert_checks.check_runner import CheckRunner
from data_processing.bank_selection import get_bank
from data_processing.prepare_data import prepare_data

pd.options.mode.chained_assignment = None  # default='warn'

PATH = "./test_data"


def load_data() -> pd.DataFrame:
    files = [os.path.join(PATH, f) for f in os.listdir(PATH) if f.endswith(".txt")]
    bank = get_bank("Nordea")
    data = prepare_data(file_paths=files,
                        data_loader=bank.loader,
                        data_transformer=bank.transformer)
    return data


class MonthlyIncomes(StandardCheck):
    filtering = {"min_value": 0}
    group_by = ["year", "month"]
    aggregation = "sum"
    ref_values = 1200
    criteria = Criteria.larger


class MonthlyOutcomes(StandardCheck):
    filtering = {"max_value": 0}
    group_by = ["year", "month"]
    aggregation = "sum"
    ref_values = -3700
    criteria = Criteria.larger


class LargestOutcome(StandardCheck):
    filtering = {"max_value": 0}
    aggregation = "min"
    ref_values = -1500
    criteria = Criteria.larger


class MeanForAimee(StandardCheck):
    filtering = {"target": "Aimee Dodd"}
    group_by = ["year", "month"]
    aggregation = "mean"
    ref_values = -15
    criteria = Criteria.larger


class Duplicates(Check):
    ref_values = 0
    criteria = Criteria.equal

    def pipeline(self, df: pd.DataFrame):
        return df[df.duplicated(keep=False)].value.count()


def main():
    configure_logging()
    data = load_data()
    checks = [MonthlyIncomes(),
              MonthlyOutcomes(),
              LargestOutcome(),
              MeanForAimee(),
              Duplicates()]

    checker = CheckRunner()
    checker.run_checks(data, checks, True)


if __name__ == "__main__":
    main()
