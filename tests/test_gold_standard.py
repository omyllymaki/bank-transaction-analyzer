import os
import random

from src.config_manager import ConfigManager, DROP_DATA_KEY
from src.data_processing.data_filtering import filter_data
from src.data_processing.data_preprocessing import DataPreprocessor
from src.utils import save_pickle, load_pickle
from tests.base_test import BaseTest

random.seed(42)

GENERATE_REFERENCE = False


class TestFiltering(BaseTest):

    def _generate_target_inputs(self):
        inputs = []
        for k in range(50):
            n_targets = random.randint(3, 10)
            targets = self.data["target"].sample(n=n_targets, random_state=k)
            targets_search = "|".join(targets.values.tolist())
            inputs.append({"target": targets_search})
        return inputs

    def _generate_id_inputs(self):
        inputs = []
        for k in range(50):
            n_ids = random.randint(2, 5)
            ids = self.data["id"].sample(n=n_ids, random_state=k)
            ids_search = "|".join(ids.values.tolist())
            inputs.append({"id": ids_search})
        return inputs

    def _generate_value_inputs(self):
        n_rows = self.data.shape[0]
        inputs = []
        for k in range(50):
            i = random.randrange(n_rows)
            min_value = self.data["value"].iloc[i]
            i = random.randrange(n_rows)
            max_value = self.data["value"].iloc[i]
            inputs.append({"min_value": min_value, "max_value": max_value})
        return inputs

    def _generate_date_inputs(self):
        n_rows = self.data.shape[0]
        inputs = []
        for k in range(50):
            i = random.randrange(n_rows)
            min_date = self.data["time"].iloc[i]
            i = random.randrange(n_rows)
            max_date = self.data["time"].iloc[i]
            inputs.append({"min_date": min_date, "max_date": max_date})
        return inputs

    def _generate_labels_inputs(self):
        inputs = []
        unique_labels = self.data["labels"].unique()
        for label in unique_labels:
            inputs.append({"labels": label})
        return inputs

    def _general_filtering_test(self, test_name, f, catch_error=False):

        if GENERATE_REFERENCE:
            inputs = f()

            outputs = []
            for input in inputs:
                output = filter_data(self.data,
                                     **input)
                output = output.to_dict()
                outputs.append(output)

            save_pickle(test_name, {"inputs": inputs, "outputs": outputs})

        data = load_pickle(test_name)
        inputs = data["inputs"]
        expected_outputs = data["outputs"]

        for input, expected_output in zip(inputs, expected_outputs):
            output = filter_data(self.data,
                                 **input)

            output = output.to_dict()
            print(f"Input {input}; output size  {len(output['time'])}")
            if catch_error:
                try:
                    self._compare_dicts(output, expected_output, test_name)
                except Exception as e:
                    print(e)

    def test_target_filtering(self):
        self._general_filtering_test(f"{self._testMethodName}.p", self._generate_target_inputs)

    def test_value_filtering(self):
        self._general_filtering_test(f"{self._testMethodName}.p", self._generate_value_inputs)

    def test_date_filtering(self):
        self._general_filtering_test(f"{self._testMethodName}.p", self._generate_date_inputs)

    def test_id_filtering(self):
        self._general_filtering_test(f"{self._testMethodName}.p", self._generate_id_inputs)

    def test_labels_filtering(self):
        self._general_filtering_test(f"{self._testMethodName}.p", self._generate_labels_inputs)
