import unittest

from gt import GroundTruthAlignments
from gt.event_log_splitter import EventLogSplitter
from utility.converter import Converter


class GroundTruthAlignmentsTest(unittest.TestCase):

    def test_ground_truth_alignments(self):
        testee = GroundTruthAlignments()
        event_log_splitter = EventLogSplitter("datasets/Sepsis.xes")
        event_log_train = Converter().from_event_log(event_log_splitter.get_training_data())
        event_log_test = Converter().from_event_log(event_log_splitter.get_test_data())
        testee.mine_process_model(event_log_train)
        testee.calculate_alignments(event_log_test)
        print("Done")

if __name__ == '__main__':
    unittest.main()
