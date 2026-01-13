from algo.event import Event
from algo.latest_event_info import LatestEventInfo
from algo.network import Network
from algo.trie import Trie
from algo.trie_node import Node


class DiscoveryNode:

    def __init__(self, node_id: str, network: Network):
        self.node_id = node_id
        self.network: Network = network
        self.local_network: Network = network
        self.local_trie: Trie = Trie()
        self.latest_ts = None
        self.running_trace = []

    def get_latest_timestamp(self) -> LatestEventInfo | None:
        if self.latest_ts is None:
            return None
        return LatestEventInfo(self.latest_ts, Node(self.node_id))

    def process_event(self, event: Event):
        timestamps = []
        for node in self.network.get_all_nodes():
            timestamp = node.get_latest_timestamp()
            if timestamp:
                timestamps.append(timestamp)
        if timestamps:
            latest_timestamp: LatestEventInfo = max(timestamps)
            if not self.latest_ts or latest_timestamp.timestamp > self.latest_ts:
                self.running_trace.extend([latest_timestamp.node, event.activity])
            else:
                self.running_trace.append(event.activity)
        else:
            self.running_trace.append(event.activity)
        self.local_trie.insert_trace(self.running_trace)
        self.latest_ts = event.time
