from algo.trie_node import Node


class LatestEventInfo:

    def __init__(self, timestamp: int, node: Node):
        self.timestamp: int = timestamp
        self.node: Node = node

    def __lt__(self, other):
        return self.timestamp < other.timestamp