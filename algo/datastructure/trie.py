from typing import List, Any


class Trie:
    def __init__(self, label=None):
        if label:
            self.label = label
        else:
            self.label = "#"
        self.children: List[Trie] = []

    def __str__(self):
        return str(self.label)

    def is_root(self):
        return isinstance(self.label, str)

    def has_child(self, label) -> bool:
        return label in [child.label for child in self.children]

    def is_leaf(self):
        return len(self.children) == 0

    def get_child(self, label) -> 'Trie':
        return [child for child in self.children if child.label == label][0]

    def traverse(self, label):
        return self.get_child(label).children[0]

    def get_children(self):
        return self.children

    def add_child(self, trie: 'Trie'):
        self.children.append(trie)

    def get_children_containing_label(self, label):
        return [
            self.get_child(child.label).label
            for child in self.get_children()
            if self.get_child(child.label).contains(label)
        ]

    def contains(self, label, rec_depth=0) -> bool:
        if self.label == label:
            return True
        for child in self.children:
            if rec_depth> 19:
                print("Stop")
            if child.contains(label, rec_depth + 1):
                return True
        return False

    def get_leaves(self) -> List[Any]:
        if self.is_leaf():
            return [self.label]

        leaves = []
        for child in self.children:
            leaves.extend(child.get_leaves())

        return leaves