import logging
from collections import Iterable
from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.alert_checks.check import Check
from src.alert_checks.options import OnFail

logger = logging.getLogger(__name__)


class CheckRunner:

    def run_checks(self, df: pd.DataFrame,
                   checks: List[Check],
                   plot=False,
                   on_fail=OnFail.log_error) -> Tuple[bool, List[Check]]:
        logger.info("Start alert checks")
        n_checks = len(checks)
        n_passed = 0
        all_ok = True
        not_passed = []
        for i, check in enumerate(checks, 1):
            logger.info(f"Performing check {i}/{n_checks}: {check.name}")
            is_ok = self.run_check(df.copy(), check, plot)
            if is_ok:
                n_passed += 1
            else:
                all_ok = False
                not_passed.append(check)
        logger.info(f"Alert checks done: {n_passed}/{n_checks} ({100 * n_passed / n_checks:0.1f} %) passed")
        if not all_ok:
            msg = f"{len(not_passed)} checks failed. Failed checks: {not_passed}"
            on_fail(msg)
        return all_ok, not_passed

    def run_check(self, df: pd.DataFrame,
                  check: Check,
                  plot=False) -> bool:

        test_values = check.pipeline(df)

        if not isinstance(test_values, Iterable):
            test_values = [test_values]
        if not isinstance(check.ref_values, Iterable):
            ref_values = [check.ref_values for _ in range(len(test_values))]
        else:
            ref_values = check.ref_values

        if len(test_values) != len(ref_values):
            raise Exception("Number of calculated values doesn't match with number of reference values")

        all_values_ok = True
        results = []
        for value, ref_value in zip(test_values, ref_values):
            is_ok = check.criteria.__func__(value, ref_value)
            results.append(is_ok)
            logger.debug(f"Test: {is_ok}, {value}, {ref_value}")
            if not is_ok:
                msg = f"Check {check.name} doesn't pass: calculated {value}; reference {ref_value}"
                check.on_fail.__func__(msg)
                all_values_ok = False

        if plot:
            self.visualize_results(test_values, ref_values, results, check.name)

        return all_values_ok

    @staticmethod
    def visualize_results(test_values, ref_values, results, title):
        x = np.array([k for k in range(len(test_values))])
        plt.bar(x, test_values, color='g')
        plt.bar(x[~np.array(results)], np.array(test_values)[~np.array(results)], color='r')
        if len(ref_values) > 1:
            plt.plot(x, ref_values, color="k", linewidth=2)
        else:
            plt.plot([x - 0.5, x + 0.5], [ref_values, ref_values], "r")
        plt.title(title)
        plt.show()
