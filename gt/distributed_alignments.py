from typing import List

from algo.discovery_node import DiscoveryNode
from algo.event_log import EventLog
from algo.insight_node import InsightNode
from algo.network import Network
from algo.new_trie import NewTrie
from time import time

from algo.strategy.collect_previous_alignments_strategy import CollectPreviousAlignmentsStrategy, \
    CollectPreviousAlignmentsStrategyAskAll


class DistributedAlignments:

    def __init__(self, max_heap_size: int):
        self.network = Network()
        self.node_id = "n1"
        self.discovery_node = DiscoveryNode(self.node_id, network=self.network)
        self.trie: NewTrie | None = None
        self.insight_node: InsightNode = None
        self.max_heap_size = max_heap_size
        self.monitor: List[float] = []

    def mine_process_model(self, event_log: EventLog):
        for trace in event_log.traces:
            for event in event_log.traces[trace]:
                self.discovery_node.process_event(event)
        self.trie = self.discovery_node.local_trie

    def calculate_alignments(self, event_log: EventLog):
        self.insight_node = InsightNode(
            trie=self.trie,
            node_id=self.node_id,
            network=self.network,
            max_heap_size=self.max_heap_size,
            collect_alignments_strategy=lambda network, node_id: CollectPreviousAlignmentsStrategyAskAll(network, node_id)
        )
        for trace in event_log.traces:
            for event in event_log.traces[trace]:
                start = time()
                self.insight_node.process_event(event)
                end = time()
                self.monitor.append(round((end - start)*1000, 2))