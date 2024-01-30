import cProfile
import inspect
import json
import os
import pickle
import pstats
from functools import wraps
from time import time


def load_json(path):
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_pickle(path):
    with open(path, 'rb') as handle:
        return pickle.load(handle)


def save_pickle(path, data):
    with open(path, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)


def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()

        # Get information about the calling module
        calling_module = inspect.getmodule(inspect.currentframe().f_back)
        calling_module_name = calling_module.__name__ if calling_module else "unknown_module"

        print(f"func:{f.__name__} in module:{calling_module_name} took {te - ts} s")
        return result

    return wrap


def profile_decorator(filename):
    def decorator(func):
        def wrapper(*args, **kwargs):
            profiler = cProfile.Profile()
            profiler.enable()

            result = func(*args, **kwargs)

            profiler.disable()
            profiler.dump_stats(filename)
            stats = pstats.Stats(filename)
            stats.sort_stats("cumulative")
            stats.print_stats()
            stats.dump_stats(f"{filename}.stats")
            os.system(f"snakeviz {filename}.stats")

            return result

        return wrapper

    return decorator
