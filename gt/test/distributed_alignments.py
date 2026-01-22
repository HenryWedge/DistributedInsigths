import unittest

from gt.distributed_alignments import DistributedAlignments
from gt.event_log_splitter import EventLogSplitter
from utility.converter import Converter


class GroundTruthAlignmentsTest(unittest.TestCase):

    def test_ground_truth_alignments(self):
        testee = DistributedAlignments()
        event_log_splitter = EventLogSplitter("datasets/Sepsis.xes")
        testee.mine_process_model(event_log_splitter.get_training_data())
        testee.calculate_alignments(event_log_splitter.get_test_data())
        print("Done")

if __name__ == '__main__':
    unittest.main()
