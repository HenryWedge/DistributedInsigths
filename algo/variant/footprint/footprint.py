from typing import List

from algo.datastructure.event import Event
from algo.network import Network
from algo.variant.footprint.footprint_matrix import FootprintMatrix


class DistributedFootprint(Network):

    def __init__(self, network: Network, node_id: str):
        self.network = network
        self.node_id = node_id
        self.footprint_matrix: FootprintMatrix = FootprintMatrix()
        self.network.add_node(self.node_id, self)
        self.events: List[Event] = []

    def check_conformance(self, event: Event):
        self.events.append(event)
        for node in self.network.get_all_nodes(self.node_id):
            node.is_predecessor(event.case_id)

    def is_predecessor(self, case_id):
        pass
