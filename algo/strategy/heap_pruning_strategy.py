import heapq
from abc import ABC
from typing import List

from algo.state_item import StateItem

class HeapPruningStrategy(ABC):
    def prune(self, current_items: List[StateItem]) -> List[StateItem]:
        pass

class DoNotPruneStrategy(HeapPruningStrategy):
    def prune(self, current_items: List[StateItem]) -> List[StateItem]:
        return current_items

class PruneHighestCostStrategy(HeapPruningStrategy):
    def __init__(self, max_size: int):
        self.max_size = max_size

    def prune(self, current_items: List[StateItem]) -> List[StateItem]:
        heapq.heapify(current_items)
        return current_items[:self.max_size]