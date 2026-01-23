from datetime import datetime
from typing import List

from algo.state_item import StateItem
from algo.trie_node import Node


class StateWithTime:

    def __init__(self, time: datetime, states: List[StateItem], node: Node):
        self.time: datetime = time
        self.states: List[StateItem] = states
        self.node: Node = node

    def __lt__(self, other):
        return self.time < other.time