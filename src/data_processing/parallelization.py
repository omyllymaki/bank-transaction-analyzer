import os
from concurrent.futures import ProcessPoolExecutor
from typing import Callable

import numpy as np
import pandas as pd


def process_df_parallel(df: pd.DataFrame, run_func: Callable, output_conversion_func: Callable = None,
                        n_tasks: int = None):
    if n_tasks is None:
        n_tasks = os.cpu_count()
    tasks = np.array_split(df, n_tasks)
    with ProcessPoolExecutor() as executor:
        results = executor.map(run_func, tasks)
    if output_conversion_func:
        return output_conversion_func(results)
    else:
        return results
