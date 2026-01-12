from collections import deque
from typing import List

from algo.trie import Trie
from algo.trie_node import TrieNode


class TrieTraverser:

    def __init__(self, trie: Trie):
        self.trie: Trie = trie

    def find_activity_in_trie(self, activity: TrieNode) -> tuple[Trie | None, int]:
        if activity in self.trie.next_items():
            return self.trie, 0

        initial_queue: List[tuple[Trie, int]] = []
        for children in self.trie.next_children():
            initial_queue.append((children, 1))

        queue = deque(initial_queue)
        while queue:
            current_trie = queue.popleft()

            if current_trie[0].is_empty():
                continue

            if activity in current_trie[0].next_items():
                return current_trie

            for children in current_trie[0].next_children():
                queue.append((children, current_trie[1] + 1))

        return None, -1
