import heapq
from typing import List

from algo.state_item import StateItem

class StateExplorer:
    def __init__(self, initial_state: StateItem | None = None):
        self.heap: List[StateItem] = []
        if initial_state:
            self.heap.append(initial_state)
        self.max_heap_size = 10

    def get_next_state(self) -> StateItem:
        return self.heap.pop()

    def is_empty(self) -> bool:
        return not bool(self.heap)

    def top(self, n=1) -> List[StateItem] | StateItem:
        if n == -1:
            return sorted(self.heap)
        if n == 1:
            return heapq.nsmallest(n=n, iterable=self.heap)[0]
        return heapq.nsmallest(n=n ,iterable=self.heap)

    def clear(self):
        self.heap = []

    def insert_state(self, state):
        heapq.heappush(self.heap, state)

    def get_all_states(self) -> List[StateItem]:
        return self.heap

    def prune(self):
        pass
        #self.heap = self.heap[:5]