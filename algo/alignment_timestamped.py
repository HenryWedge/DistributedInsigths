from algo.alignment import Alignment
from algo.trie_node import Node

class AlignmentTimestamped:
    def __init__(self, alignment: Alignment, timestamp: int, node: Node):
        self.alignment: Alignment = alignment
        self.timestamp: int = timestamp
        self.node: Node = node

    def __lt__(self, other):
        return self.timestamp < other.timestamp