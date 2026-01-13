import heapq
from typing import List

from algo.state_item import StateItem

class StateExplorer:
    def __init__(self, initial_state: StateItem):
        self.heap: List[StateItem] = [initial_state]
        self.max_heap_size = 10

    def  get_next_state(self) -> StateItem:
        return self.heap.pop()

    def is_empty(self) -> bool:
        return bool(self.heap)

    def top(self) -> StateItem:
        return self.heap[0]

    def insert_state(self, state):
        heapq.heappush(self.heap, state)

    def get_all_states(self) -> List[StateItem]:
        return self.heap
