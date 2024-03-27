from typing import List

from src.data_processing.checks.base_check import Check
from src.data_processing.checks.standard_check import StandardCheck


def get_checks(specifications):
    checks = []
    for specification in specifications:
        checks.append(StandardCheck(**specification))
    return checks


def run_checks(checks: List[Check], df):
    all_passed = True
    all_results = []
    for check in checks:
        passed, results = check.apply(df.copy())
        all_results.append(results)
        print(f"Check: {check.name}")
        print(f"Passed: {passed}")
        print(f"Results:\n {results}")
        if not passed:
            all_passed = False
    return all_passed, all_results
