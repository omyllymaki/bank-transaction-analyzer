import os

import pandas as pd

from alert_checks.alert_logging import configure_logging
from alert_checks.check import Check, Criteria, StandardCheck
from alert_checks.check_runner import CheckRunner
from alert_checks.utils import checks_from_csv
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


class Duplicates(Check):
    name = "Duplicates"
    ref_values = 0
    criteria = Criteria.equal

    def pipeline(self, df: pd.DataFrame):
        return df[df.duplicated(keep=False)].value.count()


def main():
    configure_logging()
    data = load_data()
    checks = checks_from_csv("alert_checks.csv") + [Duplicates()]

    checker = CheckRunner()
    checker.run_checks(data, checks, True)


if __name__ == "__main__":
    main()
