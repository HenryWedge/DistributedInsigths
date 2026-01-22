import unittest

from gt import GroundTruthAlignments
from gt.event_log_splitter import EventLogSplitter
from utility.converter import Converter
from pm4py.visualization.petri_net import visualizer as pn_visualizer

class GroundTruthAlignmentsTest(unittest.TestCase):

    def test_ground_truth_alignments(self):
        testee = GroundTruthAlignments()
        event_log_splitter = EventLogSplitter("datasets/Sepsis.xes")
        event_log_train = Converter().from_event_log(event_log_splitter.get_training_data())
        event_log_test = Converter().from_event_log(event_log_splitter.get_test_data())
        testee.mine_process_model(event_log_train)
        testee.calculate_alignments(event_log_test)

        gviz = pn_visualizer.apply(testee.model[0], testee.model[1], testee.model[2])

        pn_visualizer.view(gviz)
        print("Done")

if __name__ == '__main__':
    unittest.main()
