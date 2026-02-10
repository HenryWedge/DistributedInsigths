import heapq
from abc import ABC
from typing import List

from algo.state_item import StateItem

class HeapPruningStrategy(ABC):
    def prune(self, current_items: List[StateItem]) -> List[StateItem]:
        pass

    def get_heap_sizes(self):
        pass

class DoNotPruneStrategy(HeapPruningStrategy):
    def __init__(self):
        self.heap_sizes = []

    def prune(self, current_items: List[StateItem]) -> List[StateItem]:
        self.heap_sizes.append(len(current_items))
        return current_items

    def get_heap_sizes(self):
        return self.heap_sizes

class PruneHighestCostStrategy(HeapPruningStrategy):
    def __init__(self, max_size: int):
        self.max_size = max_size
        self.heap_sizes = []

    def prune(self, current_items: List[StateItem]) -> List[StateItem]:
        heapq.heapify(current_items)
        self.heap_sizes.append(len(current_items))
        return current_items[:self.max_size]

    def get_heap_sizes(self):
        return self.heap_sizes
