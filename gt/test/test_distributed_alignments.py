import unittest
from typing import Dict

from gt.distributed_alignments import DistributedAlignments
from gt.event_log_splitter import EventLogSplitter
from gt.network_topology_event_log_adapter import NetworkTopologyEventLogAdapter
from test_event_log import TestEventLog


class TestGroundTruthAlignments(unittest.TestCase):

    def test_ground_truth_alignments(self):
        testee = DistributedAlignments()
        event_log_splitter = EventLogSplitter("./datasets/Sepsis.xes")
        #event_log_splitter = TestEventLog()

        test_traces_count = 10

        testee.mine_process_model(event_log_splitter.get_training_data())
        testee.calculate_alignments(event_log_splitter.get_test_data(test_traces_count))

        adapter = NetworkTopologyEventLogAdapter()
        adapter.distribute_event_log_discovery(event_log_splitter.get_training_data())
        adapter.distribute_event_log_insights(event_log_splitter.get_test_data(test_traces_count))

        central_alignments: Dict[str, int] = {}
        decentral_alignments: Dict[str, int] = {}

        for case_id in testee.insight_node.state_explorer:
            central_alignments[case_id] = testee.insight_node.state_explorer[case_id].top()[0].cost

        for node in adapter.network_topology.insight_nodes:
            for case_id in adapter.network_topology.insight_nodes[node].state_explorer:
                new_cost = adapter.network_topology.insight_nodes[node].state_explorer[case_id].top()[0].cost
                if not case_id in decentral_alignments or decentral_alignments[case_id] < new_cost:
                    decentral_alignments[case_id] = new_cost

        print("Finished")


if __name__ == '__main__':
    unittest.main()
