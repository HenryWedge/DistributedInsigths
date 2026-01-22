import unittest

from gt.event_log_splitter import EventLogSplitter
from gt.network_topology_event_log_adapter import NetworkTopologyEventLogAdapter


class NetworkTopologyEventLogAdapterTest(unittest.TestCase):

    def test_ground_truth_alignments(self):
        event_log_splitter = EventLogSplitter("datasets/Sepsis.xes", location_key="org:group")
        adapter = NetworkTopologyEventLogAdapter()
        adapter.distribute_event_log_discovery(event_log_splitter.get_training_data())
        adapter.distribute_event_log_insights(event_log_splitter.get_test_data())
        print("Done")

if __name__ == '__main__':
    unittest.main()
