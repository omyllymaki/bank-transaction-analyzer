from typing import List

from src.data_processing.checks.checks import *


def get_checks(specifications):
    checks = []
    for specification in specifications:
        specification_copy = specification.copy()
        check_type = specification_copy.pop("type")
        check_obj = globals()[check_type]
        kwargs = specification_copy["arguments"]
        checks.append(check_obj(**kwargs))

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
