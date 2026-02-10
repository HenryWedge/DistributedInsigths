import string
from time import time
from typing import Dict, List, Callable

from algo.discovery_node import DiscoveryNode
from algo.event import Event
from algo.event_distribution_function import EventDistributionFunction
from algo.insight_node import InsightNode
from algo.network import Network
from algo.strategy.collect_previous_alignments_strategy import CollectPreviousAlignmentsStrategy
from algo.strategy.heap_pruning_strategy import HeapPruningStrategy


class NetworkTopology:
    def __init__(
        self,
        event_distribution_function: EventDistributionFunction,
        pruning_strategy: HeapPruningStrategy,
        collect_alignments_strategy: Callable[[Network, string], CollectPreviousAlignmentsStrategy]
    ):
        self.network_discovery: Network = Network()
        self.network_insights: Network = Network()
        self.insight_nodes: Dict[str, InsightNode] = {}
        self.discovery_nodes: Dict[str, DiscoveryNode] = {}
        self.event_distribution_function: EventDistributionFunction = event_distribution_function
        self.pruning_strategy: HeapPruningStrategy = pruning_strategy
        self.monitor: List[float] = []
        self.heap_size_monitor: List[float] = []
        self.collect_alignments_strategy = collect_alignments_strategy

    def init_insight_nodes(self):
        for location in self.discovery_nodes:
            node = InsightNode(
                self.discovery_nodes[location].local_trie,
                location,
                self.network_insights,
                self.pruning_strategy,
                self.collect_alignments_strategy
            )
            self.insight_nodes[location] = node
            self.network_insights.add_node(location, node)

    def process_insights(self, event: Event):
        location = self.event_distribution_function.distribute(event)
        if not location in self.discovery_nodes:
            print("WARNING: Resource not seen yet")
            return
        insight_node: InsightNode = self.insight_nodes[location]
        start = time()
        insight_node.process_event(event)
        self.heap_size_monitor.append(len(insight_node.state_explorer[event.case_id].heap))
        end = time()
        self.monitor.append(round(1000 * (end - start), 2))

    def process_discovery_event(self, event: Event):
        location = self.event_distribution_function.distribute(event)
        if location not in self.discovery_nodes:
            node = DiscoveryNode(location, self.network_discovery)
            self.discovery_nodes[location] = node
            self.network_discovery.add_node(location, node)
        discovery_node: DiscoveryNode = self.discovery_nodes[location]
        discovery_node.process_event(event)

    def get_cumulated_alignment_cost(self):
        alignments_per_case = {}
        for node in self.insight_nodes:
            for case_id in self.insight_nodes[node].state_explorer:
                new_cost = self.insight_nodes[node].state_explorer[case_id].top().cost
                if not case_id in alignments_per_case or alignments_per_case[case_id] < new_cost:
                    alignments_per_case[case_id] = new_cost
        return alignments_per_case

    def get_network_requests(self):
        network_requests = []
        for node in self.insight_nodes:
            network_requests.append(sum(self.insight_nodes[node].collect_alignments_strategy.get_number_of_network_requests()))
        return network_requests

    def get_heap_size(self):
        heap_sizes = []
        for node in self.insight_nodes:
            heap_sizes.append(sum(self.insight_nodes[node].heap_pruning_strategy.get_heap_sizes()))
        return heap_sizes