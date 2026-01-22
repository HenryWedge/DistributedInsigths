from algo.discovery_node import DiscoveryNode
from algo.event_log import EventLog
from algo.insight_node import InsightNode
from algo.network import Network
from algo.trie import Trie


class DistributedAlignments:

    def __init__(self):
        self.network = Network()
        self.node_id = "n1"
        self.discovery_node = DiscoveryNode(self.node_id, network=self.network)
        self.trie = None

    def mine_process_model(self, event_log: EventLog) -> Trie:
        for trace in event_log.traces:
            for event in event_log.traces[trace]:
                self.discovery_node.process_event(event)
        self.trie = self.discovery_node.local_trie

    def calculate_alignments(self, event_log: EventLog):
        insight_node = InsightNode(trie=self.trie, node_id=self.node_id, network=self.network)
        for trace in event_log.traces:
            for event in event_log.traces[trace]:
                insight_node.process_event(event)
