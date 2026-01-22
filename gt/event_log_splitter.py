import random
import pm4py
from utility.converter import Converter

class EventLogSplitter:

    def __init__(self, file_path: str, training_split: int = 0.8):
        self.converter = Converter()
        self.training_split = training_split
        self.log = self._read_xes_log(file_path)
        self.case_ids = self._get_case_ids()
        self.split_index = self._calculate_split_index()

    def _read_xes_log(self, file_path):
        return self.converter.to_event_log(pm4py.read_xes(file_path, return_legacy_log_object=True))

    def _get_case_ids(self):
        return list(self.log.traces.keys())

    def _calculate_split_index(self):
        random.seed(1)
        random.shuffle(self.case_ids)

        split_index = int(len(self.case_ids) * 0.8)
        return split_index

    def get_training_data(self):
        return self.log.filter_case_ids(self.case_ids[:100])

    def get_test_data(self):
        return self.log.filter_case_ids(self.case_ids[-100:])