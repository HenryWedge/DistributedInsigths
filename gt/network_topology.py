import string
from time import time
from typing import Dict, List, Callable

from algo.discovery_node import DiscoveryNode
from algo.event import Event
from algo.insight_node import InsightNode
from algo.network import Network
from algo.strategy.collect_previous_alignments_strategy import CollectPreviousAlignmentsStrategy
from algo.strategy.heap_pruning_strategy import HeapPruningStrategy


class NetworkTopology:
    def __init__(
            self,
            pruning_strategy: HeapPruningStrategy,
            collect_alignments_strategy: Callable[[Network, string], CollectPreviousAlignmentsStrategy]
    ):
        self.network_discovery: Network = Network()
        self.network_insights: Network = Network()
        self.insight_nodes: Dict[str, InsightNode] = {}
        self.discovery_nodes: Dict[str, DiscoveryNode] = {}
        self.pruning_strategy: HeapPruningStrategy = pruning_strategy
        self.monitor: List[float] = []
        self.collect_alignments_strategy = collect_alignments_strategy

    def process_insights(self, event: Event):
        if event.location not in self.insight_nodes:
            node = InsightNode(
                self.discovery_nodes[event.location].local_trie,
                event.location,
                self.network_insights,
                self.pruning_strategy,
                self.collect_alignments_strategy
            )
            self.insight_nodes[event.location] = node
            self.network_insights.add_node(event.location, node)
        insight_node: InsightNode = self.insight_nodes[event.location]
        start = time()
        insight_node.process_event(event)
        end = time()
        self.monitor.append(round(1000 * (end - start), 2))

    def process_discovery_event(self, event: Event):
        if event.location not in self.discovery_nodes:
            node = DiscoveryNode(event.location, self.network_discovery)
            self.discovery_nodes[event.location] = node
            self.network_discovery.add_node(event.location, node)
        discovery_node: DiscoveryNode = self.discovery_nodes[event.location]
        discovery_node.process_event(event)
