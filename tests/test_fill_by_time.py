import pandas as pd

from src.data_processing.data_analysis import fill_by_time
from tests.base_test import BaseTest


class TestFillByTime(BaseTest):

    def test_empty_input_will_return_empty_output(self):
        df = pd.DataFrame
        df_out = fill_by_time(df)
        self.assertTrue(df_out.empty)

    def test_fill(self):
        df_out = fill_by_time(self.data, freq="D")
        self.assertGreater(df_out.shape[0], self.data.shape[0])

        unique_days = df_out["time"].unique()
        date_max = self.data["time"].max()
        date_min = self.data["time"].min()
        n_days = (date_max - date_min).days
        self.assertEqual(len(unique_days) - 1, n_days)
