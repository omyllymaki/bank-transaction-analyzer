import os
import unittest

from src.config_manager import ConfigManager, DROP_DATA_KEY
from src.data_processing.data_preprocessing import DataPreprocessor


class BaseTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        root_path = os.path.abspath(os.path.dirname(__file__))
        data_path = os.path.join(root_path, "test_data")
        config_path = os.path.join(root_path, "test_configuration/config.json")
        files = [os.path.join(data_path, f) for f in os.listdir(data_path) if f.endswith(".txt")]
        data_processor = DataPreprocessor()
        config_manager = ConfigManager(config_path)
        config = config_manager.get_config()
        data_all = data_processor.get_data(files)
        data_all = data_processor.update_extra_columns(data_all, config)
        cls.data, cls.data_filtered_out = data_processor.drop_data(data_all, config[DROP_DATA_KEY])

    def _compare_dicts(self, test_dict, ref_dict, test_name):

        test_keys = list(test_dict.keys())
        ref_keys = list(ref_dict.keys())

        msg = f"{test_name}: Test and reference dict do not contain same keys"
        self.assertListEqual(test_keys, ref_keys, msg)

        for key in test_keys:
            test_values = list(test_dict[key].values())
            ref_values = list(ref_dict[key].values())
            if len(test_values) == 0 and len(ref_values) == 0:
                continue
            msg = f"{test_name}: Key {key} has different length values"
            self.assertListEqual(test_values, ref_values, msg)
