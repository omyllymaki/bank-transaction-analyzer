import json
import types
from tkinter import Tk, messagebox

from src.alert_checks.check import StandardCheck
from src.alert_checks.options import Criteria, Grouping, Aggregation

FILTERING_KEYS = ["min_date",
                  "max_date",
                  "target",
                  "account_number",
                  "message",
                  "event",
                  "min_value",
                  "max_value"]


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
        c.filtering = {k: v for k, v in values.items() if k in FILTERING_KEYS}
        c.name = name
        c.description = values.get("description")
        checks.append(c)
    return checks
