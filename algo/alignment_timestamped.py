from datetime import datetime

from algo.alignment import Alignment
from algo.trie_node import Node

class AlignmentTimestamped:
    def __init__(self, alignment: Alignment, timestamp: datetime, node: Node):
        self.alignment: Alignment = alignment
        self.timestamp: datetime = timestamp
        self.node: Node = node

    def __lt__(self, other):
        return self.timestamp < other.timestamp

    def __str__(self):
        return f"(node:{self.node},ts:{self.timestamp},alignment:{str(self.alignment)})"