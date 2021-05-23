import types

import pandas as pd

from src.alert_checks.check import StandardCheck, Criteria

FILTERING_KEYS = ["min_date",
                  "max_date",
                  "target",
                  "account_number",
                  "message",
                  "event",
                  "min_value",
                  "max_value"]


def checks_from_csv(path):
    df = pd.read_csv(path)
    return df_to_checks(df)


def df_to_checks(df):
    df = df.where(pd.notnull(df), None)
    checks = []
    for i, row in df.transpose().iteritems():
        c = StandardCheck()
        c.ref_values = row.ref_value
        criteria = getattr(Criteria, row.criteria)
        c.criteria = types.MethodType(criteria, StandardCheck())
        c.group_by = row["group_by"].strip('][').split(', ') if row["group_by"] is not None else None
        c.aggregation = row["aggregation"]
        c.filtering = row[row.index.isin(FILTERING_KEYS)].to_dict()
        print(c.filtering)
        c.name = row["name"]
        checks.append(c)
    return checks
