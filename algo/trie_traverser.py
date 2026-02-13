from collections import deque
from typing import List, Any

from algo.new_trie import NewTrie
from algo.trie_node import TrieNode


class TrieTraverser:

    def __init__(self, trie: NewTrie):
        self.trie: NewTrie = trie

    def find_activity_in_trie(self, activity: TrieNode) -> tuple[NewTrie | None, int, list[Any]]:
        if self.trie.has_child_with_label(activity):
            return self.trie.traverse(activity), 0, [activity]

        initial_queue: List[tuple[NewTrie, int, List[any]]] = []
        for child in self.trie.get_children():
            initial_queue.append((child, 0, [child.label]))

        queue = deque(initial_queue)
        while queue:
            trie, cost, path = queue.popleft()

            if not trie:
                continue

            if trie.label == activity:
                return trie, cost, path

            for child in trie.get_children():
                path.append(child.label)
                queue.append((child, cost + 1, path))

        return None, -1
