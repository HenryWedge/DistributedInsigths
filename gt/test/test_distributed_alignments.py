import unittest

from gt.distributed_alignments import DistributedAlignments
from gt.event_log_splitter import EventLogSplitter
from gt.network_topology_event_log_adapter import NetworkTopologyEventLogAdapter
from test_event_log import TestEventLog


class TestGroundTruthAlignments(unittest.TestCase):

    def test_ground_truth_alignments(self):
        testee = DistributedAlignments()
        event_log_splitter = EventLogSplitter("./datasets/Sepsis.xes")
        #event_log_splitter = TestEventLog()
        central = False
        if central:
            testee.mine_process_model(event_log_splitter.get_training_data())
            testee.calculate_alignments(event_log_splitter.get_test_data())
        else:
            adapter = NetworkTopologyEventLogAdapter()
            adapter.distribute_event_log_discovery(event_log_splitter.get_training_data())
            adapter.distribute_event_log_insights(event_log_splitter.get_test_data())

        #for case in testee.insight_node.state_explorer:
            #print(testee.insight_node.state_explorer[case].top()[0])
            #self.assertEqual(13, testee.insight_node.state_explorer[case].top()[0].cost)

        #for node in adapter.network_topology.insight_nodes:
        #    print(adapter.network_topology.insight_nodes[node].state_explorer[case].top()[0].cost)


if __name__ == '__main__':
    unittest.main()
