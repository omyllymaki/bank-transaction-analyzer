import json
import types
from tkinter import Tk, messagebox

from src.alert_checks.check import StandardCheck
from src.alert_checks.options import Criteria, Grouping, Aggregation, OnFail


def checks_from_json(path):
    with open(path) as f:
        data = json.load(f)
    return dict_to_checks(data)


def dict_to_checks(data):
    checks = []
    for name, values in data.items():
        c = StandardCheck()
        c.ref_values = values["ref_value"]
        criteria = getattr(Criteria, values["criteria"])
        c.criteria = types.MethodType(criteria, StandardCheck())
        grouping = values.get("grouping")
        if grouping:
            c.group_by = getattr(Grouping, grouping)
        aggregation = values["aggregation"]
        if aggregation:
            c.aggregation = getattr(Aggregation, aggregation)
        on_fail = values.get("on_fail")
        if on_fail:
            c.on_fail = types.MethodType(getattr(OnFail, on_fail), StandardCheck())
        c.filtering = values.get("filtering")
        c.name = name
        c.description = values.get("description")
        checks.append(c)
    return checks
