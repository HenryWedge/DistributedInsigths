from collections import deque
from typing import List

from algo.new_trie import NewTrie
from algo.trie_node import TrieNode


class TrieTraverser:

    def __init__(self, trie: NewTrie):
        self.trie: NewTrie = trie

    def find_activity_in_trie(self, activity: TrieNode) -> tuple[NewTrie | None, int]:
        if self.trie.has_child_with_label(activity):
            return self.trie, 0

        initial_queue: List[tuple[NewTrie, int]] = []
        for children in self.trie.get_children():
            initial_queue.append((children, 1))

        queue = deque(initial_queue)
        while queue:
            current_trie = queue.popleft()

            if not current_trie[0] or current_trie[0].is_empty():
                continue

            if self.trie.has_child_with_label(activity):
                return current_trie

            for children in current_trie[0].get_children():
                queue.append((children, current_trie[1] + 1))

        return None, -1
