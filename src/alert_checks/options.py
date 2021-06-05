import logging
from enum import Enum
from tkinter import Tk, messagebox

logger = logging.getLogger(__name__)


def show_info_box(msg):
    root = Tk()
    root.withdraw()
    messagebox.showinfo("Alert check info", msg)


def show_warning_box(msg):
    root = Tk()
    root.withdraw()
    messagebox.showwarning("Alert check warning", msg)


class Criteria(Enum):
    larger = lambda val, ref: val > ref
    smaller = lambda val, ref: val < ref
    equal = lambda val, ref: val == ref


class OnFail(Enum):
    log_error = lambda msg: logger.error(msg)
    exception = lambda msg: Exception(msg)
    info_box = lambda msg: show_info_box(msg)
    warning_box = lambda msg: show_warning_box(msg)


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
