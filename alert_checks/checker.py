import logging
from typing import List

import pandas as pd

from alert_checks.check import Check

logger = logging.getLogger(__name__)


class Checker:

    def run(self, data: pd.DataFrame, checks: List[Check]) -> bool:
        logger.info("Start alert checks")
        n_checks = len(checks)
        n_passed = 0
        all_ok = True
        not_passed = []
        for i, check in enumerate(checks, 1):
            logger.info(f"Performing check {i}/{n_checks}: {check.name}")
            if check.run(data):
                n_passed += 1
            else:
                all_ok = False
                not_passed.append(check.name)
        logger.info(f"Alert checks done: {n_passed}/{n_checks} ({100 * n_passed / n_checks:0.1f} %) passed")
        logger.info(f"Checks that didn't pass: {not_passed}")
        return all_ok
