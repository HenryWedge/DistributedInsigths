from typing import Dict

from algo.discovery_node import DiscoveryNode
from algo.event import Event
from algo.insight_node import InsightNode
from algo.network import Network


class NetworkTopology:

    def __init__(self):
        self.network_discovery: Network = Network()
        self.network_insights: Network = Network()
        self.insight_nodes: Dict[str, InsightNode] = {}
        self.discovery_nodes: Dict[str, DiscoveryNode] = {}

    def process_insights(self, event: Event):
        if event.location not in self.insight_nodes:
            node = InsightNode(
                self.discovery_nodes[event.location].local_trie, event.location, self.network_insights
            )
            self.insight_nodes[event.location] = node
            self.network_insights.add_node(event.location, node)
        insight_node: InsightNode = self.insight_nodes[event.location]
        insight_node.process_event(event)

    def process_discovery_event(self, event: Event):
        if event.location not in self.discovery_nodes:
            node = DiscoveryNode(event.location, self.network_discovery)
            self.discovery_nodes[event.location] = node
            self.network_discovery.add_node(event.location, node)
        discovery_node: DiscoveryNode = self.discovery_nodes[event.location]
        discovery_node.process_event(event)