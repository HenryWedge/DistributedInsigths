from typing import Dict, List

from algo.event import Event
from algo.latest_event_info import LatestEventInfo
from algo.network import Network
from algo.trie import Trie
from algo.trie_node import Node, TrieNode, Activity


class DiscoveryNode:

    def __init__(self, node_id: str, network: Network):
        self.node_id: str = node_id
        self.network: Network = network
        self.local_network: Network = network
        self.local_trie: Trie = Trie()
        self.latest_ts: Dict[str, int] = {}
        self.completeness: Dict[str, int] = {}
        self.running_trace: Dict[str, List[TrieNode]] = {}

    def get_latest_timestamp(self, case_id) -> LatestEventInfo | None:
        if case_id not in self.latest_ts:
            return None
        return LatestEventInfo(self.latest_ts[case_id], Node(self.node_id), self.completeness[case_id])

    def process_event(self, event: Event):
        case_id = event.case_id
        timestamps = []
        for node in self.network.get_all_nodes():
            timestamp = node.get_latest_timestamp(case_id)
            if timestamp:
                timestamps.append(timestamp)

        events_to_add: List[TrieNode] = [Activity(event.activity)]
        if timestamps:
            latest_event_info: LatestEventInfo = max(timestamps)
            self.completeness[case_id] = latest_event_info.completeness
            if case_id not in self.latest_ts or latest_event_info.timestamp > self.latest_ts[case_id]:
                events_to_add.append(latest_event_info.node)
                self.completeness[case_id] = latest_event_info.completeness + 1
        else:
            self.completeness[case_id] = 0

        events_to_add.reverse()
        self.add_events_to_trace(case_id, events_to_add)
        self.local_trie.insert_trace(self.running_trace[case_id])
        self.latest_ts[case_id] = event.time

    def add_events_to_trace(self, case_id: str, events: List[TrieNode]):
        if not case_id in self.running_trace:
            self.running_trace[case_id] = []
        self.running_trace[case_id].extend(events)
