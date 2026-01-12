from typing import Dict, List


class Network[T]:

    def __init__(self):
        self.nodes: Dict[str, T] = {}

    def add_node(self, node_id, node):
        self.nodes[node_id] = node

    def get_node(self, node_id) -> T:
        return self.nodes[node_id]

    def get_all_nodes(self)-> List[T]:
        return list(self.nodes.values())