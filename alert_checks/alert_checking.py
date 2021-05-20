import logging
from collections import Iterable

import pandas as pd

logger = logging.getLogger(__name__)


def run_checks(data: pd.DataFrame, alert_checks: list) -> None:
    logger.info("Start alert checks")
    n_checks = len(alert_checks)
    n_passed = 0
    for i, check in enumerate(alert_checks, 1):

        logger.info(f"Performing check {i}/{n_checks}: {check.name}")
        values = check.calculate_values(data.copy())
        if not isinstance(values, Iterable):
            values = [values]

        all_values_ok = True
        for value in values:
            is_ok = check.comparison_function(value, check.expected)
            logger.debug(is_ok, value, check.expected)
            if not is_ok:
                check.error_function(check.name, value, check.expected)
                all_values_ok = False

        if all_values_ok:
            n_passed += 1

    logger.info(f"Alert checks done: {n_passed}/{n_checks} ({100*n_passed/n_checks:0.1f} %) passed")
