from abc import ABC

END_MARKER = "<end>"

class TrieNode(ABC):
    def __init__(self, content):
        self.content = content

    def get(self):
        return self.content

    def is_activity(self):
        pass

    def is_end(self):
        pass

    def get_activity(self):
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

    def is_end(self):
        return False

    def get_activity(self):
        return self.content

class EndActivity(TrieNode):
    def __init__(self):
        super().__init__(END_MARKER)

    def is_activity(self):
        return True

    def is_end(self):
        return True

class Node(TrieNode):
    def __init__(self, content, activity):
        super().__init__(content)
        self.activity = activity

    def is_activity(self):
        return False

    def is_end(self):
        return False

    def get_activity(self):
        return self.activity