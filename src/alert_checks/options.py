import logging
from enum import Enum

logger = logging.getLogger(__name__)


class Criteria(Enum):
    larger = lambda _, val, ref: val > ref
    smaller = lambda _, val, ref: val < ref
    equal = lambda _, val, ref: val == ref


class OnFail(Enum):
    log_error = lambda _, msg: logger.error(msg)
    exception = lambda _, msg: Exception(msg)


class Grouping(Enum):
    daily = ["year", "month", "day"]
    weekly = ["year", "month", "week"]
    monthly = ["year", "month"]
    yearly = ["year"]


class Aggregation(Enum):
    sum = "sum"
    mean = "mean"
    count = "count"
    min = "min"
    max = "max"
