from typing import Dict, List

from algo.context import Context
from algo.event import Event
from algo.latest_event_info import LatestEventInfo
from algo.network import Network
from algo.new_trie import NewTrie, TrieBuilder
from algo.trie_node import Node, TrieNode, Activity


class DiscoveryNode:

    def __init__(self, node_id: str, network: Network):
        self.node_id: str = node_id
        self.network: Network = network
        self.local_network: Network = network
        self.local_trie: NewTrie = NewTrie()
        self.latest_event: Dict[str, Context[Event]] = {}
        self.trie_builder: TrieBuilder = TrieBuilder(self.local_trie)
        self.running_trace: Dict[str, List[TrieNode]] = {}

    def get_latest_timestamp(self, case_id) -> LatestEventInfo | None:
        if case_id not in self.latest_event:
            return None
        return LatestEventInfo(self.latest_event[case_id].get_last().time, Node(self.node_id, [event.activity for event in self.latest_event[case_id].get()]))

    def process_event(self, event: Event):
        case_id = event.case_id
        timestamps = []
        for node in self.network.get_all_nodes(self.node_id):
            timestamp = node.get_latest_timestamp(case_id)
            if timestamp:
                timestamps.append(timestamp)

        events_to_add: List[TrieNode] = [Activity(event.activity)]
        if timestamps:
            latest_event_info: LatestEventInfo = max(timestamps)
            if case_id not in self.latest_event or latest_event_info.timestamp > self.latest_event[case_id].get_last().time:
                events_to_add.append(latest_event_info.node)

        events_to_add.reverse()
        self.add_events_to_trace(case_id, events_to_add)
        #TODO hrei that can be implemented more efficiently
        for e in self.running_trace[case_id]:
            self.trie_builder.insert(e)
        self.trie_builder.reset()
        if not case_id in self.latest_event:
            self.latest_event[case_id] = Context(1)
        self.latest_event[case_id].push(event)

    def add_events_to_trace(self, case_id: str, events: List[TrieNode]):
        if not case_id in self.running_trace:
            self.running_trace[case_id] = []
        self.running_trace[case_id].extend(events)
