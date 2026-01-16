import heapq
from typing import List

from algo.state_item import StateItem

class StateExplorer:
    def __init__(self, initial_states: List[StateItem]):
        heapq.heapify(initial_states)
        self.heap: List[StateItem] = initial_states
        self.max_heap_size = 10

    def get_next_state(self) -> StateItem:
        return self.heap.pop()

    def is_empty(self) -> bool:
        return not bool(self.heap)

    def top(self, n=0) -> List[StateItem] | StateItem:
        if n == 0:
            return self.heap[0]
        if n == -1:
            return sorted(self.heap)
        return heapq.nlargest(n=n ,iterable=self.heap)

    def items_after_timestamp(self, timestamp: int) -> List[StateItem]:
        return [state_item for state_item in self.heap if timestamp <= state_item.get_timestamp()]

    def insert_state(self, state):
        if state not in self.heap:
            heapq.heappush(self.heap, state)

    def get_all_states(self) -> List[StateItem]:
        return self.heap
