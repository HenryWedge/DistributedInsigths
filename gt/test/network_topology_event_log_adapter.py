import unittest

from gt.event_log_splitter import EventLogSplitter
from gt.network_topology_event_log_adapter import NetworkTopologyEventLogAdapter

class NetworkTopologyEventLogAdapterTest(unittest.TestCase):

    def test_ground_truth_alignments(self):
        event_log = EventLogSplitter("datasets/Sepsis.xes", location_key="org:group")
        #event_log = TestEventLog()
        adapter = NetworkTopologyEventLogAdapter()
        adapter.distribute_event_log_discovery(event_log.get_training_data())
        adapter.distribute_event_log_insights(event_log.get_test_data())
        print("Done")

if __name__ == '__main__':
    unittest.main()
