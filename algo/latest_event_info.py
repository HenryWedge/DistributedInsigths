from datetime import datetime

from algo.trie_node import Node


class LatestEventInfo:

    def __init__(self, timestamp: datetime, node: Node):
        self.timestamp: datetime = timestamp
        self.node: Node = node

    def __lt__(self, other):
        return self.timestamp < other.timestamp