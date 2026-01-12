from abc import ABC

class TrieNode(ABC):
    def __init__(self, content):
        self.content = content

    def get(self):
        return self.content

    def is_activity(self):
        pass

    def __str__(self):
        return self.content

    def __hash__(self):
        return hash(self.content)

    def __eq__(self, other):
        return self.content == other.content


class Activity(TrieNode):
    def __init__(self, content):
        super().__init__(content)

    def is_activity(self):
        return True


class Node(TrieNode):
    def __init__(self, content):
        super().__init__(content)

    def is_activity(self):
        return False