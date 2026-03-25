from algo.alignment import Alignment


class AlignmentResponse:
    def __init__(self, timestamp, alignment, entry_point, last_node):
        self.timestamp: int = timestamp
        self.alignment: Alignment = alignment
        self.entry_point = entry_point
        self.last_node = last_node

    def __lt__(self, other):
        return self.alignment > other.alignment

    def is_empty(self):
        return not self.alignment or self.alignment.is_empty()
