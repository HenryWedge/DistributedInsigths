from typing import List


class NewTrie:
    def __init__(self, label="#"):
        self.label = label
        self.children: List['NewTrie'] = []

    def add_child(self, trie: 'NewTrie'):
        self.children.append(trie)

    def has_child(self, label) -> bool:
        return label in [child.label for child in self.children]

    def is_leaf(self):
        return len(self.children) == 0

    def get_child(self, label) -> 'NewTrie':
        return [child for child in self.children if child.label == label][0]

    def get_children(self):
        return self.children

    def has_child_with_label(self, label) -> bool:
        return bool([child for child in self.children if child.label == label])

    def min(self):
        if not self.children:
            return 0
        return 1 + min([child.min() for child in self.children])

    def traverse(self, label) -> 'NewTrie':
        return [child for child in self.children if child.label == label][0]

    def mean(self):
        if not self.children:
            return 0
        return 1 + sum([child.mean() for child in self.children]) / len(self.children)

    def __eq__(self, other):
        if self.is_leaf() and other.is_leaf():
            return self.label == other.label
        if len(self.children) == len(other.children):
            for child in self.children:
                if not child in other.children:
                    return False
            return True
        return False


class TrieBuilder:
    def __init__(self, trie: NewTrie):
        self.root_trie = trie
        self.active_trie: NewTrie = trie

    def insert(self, label: str):
        if self.active_trie.has_child(label):
            new_trie = self.active_trie.get_child(label)
        else:
            new_trie = NewTrie(label)
            self.active_trie.add_child(new_trie)
        self.active_trie = new_trie

    def reset(self):
        self.active_trie = self.root_trie


if __name__ == '__main__':
    testee = TrieBuilder(NewTrie("#"))
    testee.insert("A")
    testee.insert("B")
    testee.insert("C")
    testee.reset()
    testee.insert("A")
    testee.insert("B")
    testee.insert("C")

    testee2 = TrieBuilder(NewTrie("#"))
    testee2.insert("A")
    testee2.insert("B")
    testee2.insert("D")
    testee2.reset()
    testee2.insert("A")
    testee2.insert("B")
    testee2.insert("C")
    print(testee.root_trie == testee2.root_trie)
    print(testee.root_trie.min())
