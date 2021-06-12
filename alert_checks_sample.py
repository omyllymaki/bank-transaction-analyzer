import os

import pandas as pd

from src.alert_checks.alert_logging import configure_logging
from src.alert_checks.check import Check
from src.alert_checks.check_runner import CheckRunner
from src.alert_checks.options import Criteria, OnFail
from src.alert_checks.utils import checks_from_json
from src.data_processing.bank_selection import get_bank
from src.data_processing.prepare_data import prepare_data

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
    on_fail = OnFail.info_box

    def pipeline(self, df: pd.DataFrame):
        return df[df.duplicated(keep=False)].value.count()


def main():
    configure_logging()
    data = load_data()
    standard_checks = checks_from_json("configurations/alert_checks.json")
    custom_checks = [Duplicates()]
    checks = standard_checks + custom_checks

    checker = CheckRunner()
    checker.run_checks(data, checks, plot=True, on_fail=OnFail.warning_box)


if __name__ == "__main__":
    main()
