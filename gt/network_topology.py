from typing import Dict

from algo.discovery_node import DiscoveryNode
from algo.event import Event
from algo.insight_node import InsightNode
from algo.network import Network


class NetworkTopology:

    def __init__(self):
        self.network: Network = Network()
        self.insight_nodes: Dict[str, InsightNode] = {}
        self.discovery_nodes: Dict[str, DiscoveryNode] = {}

    def process_insights(self, event: Event):
        if event.location not in self.insight_nodes:
            self.insight_nodes[event.location] = InsightNode(
                self.discovery_nodes[event.location].local_trie, event.location, self.network
            )
        insight_node: InsightNode = self.insight_nodes[event.location]
        insight_node.process_event(event)

    def process_discovery_event(self, event: Event):
        if event.location not in self.discovery_nodes:
            self.discovery_nodes[event.location] = DiscoveryNode(event.location, self.network)
        discovery_node: DiscoveryNode = self.discovery_nodes[event.location]
        discovery_node.process_event(event)