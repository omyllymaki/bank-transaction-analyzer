import os
import random
import unittest

from src.config_manager import ConfigManager
from src.data_processing.data_preprocessing import DataPreprocessor

random.seed(42)


class BaseTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        root_path = os.path.abspath(os.path.dirname(__file__))
        data_path = os.path.join(root_path, "../test_data")
        config_path = os.path.join(root_path, "../test_configuration/config.json")
        files = [os.path.join(data_path, f) for f in os.listdir(data_path) if f.endswith(".txt")]
        data_processor = DataPreprocessor()
        config_manager = ConfigManager(config_path)
        config = config_manager.get_config()
        data = data_processor.get_data(files)
        cls.config = config
        cls.data = data
