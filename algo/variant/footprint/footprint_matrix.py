from typing import Dict

class FootprintMatrix:
    def __init__(self):
        self.data: Dict[Relation, int] = {}

    def add_relation(self, relation):
        if relation not in self.data:
            self.data[relation] = 1
        else:
            self.data[relation] += 1

    def get_predecessor(self, successor):
        result = []
        for data in self.data:
            if data.is_successor(successor):
                result.append(data)
        return result

class Relation:
    def __init__(self):
        self.data = []

    def is_successor(self, successor):
        for data in self.data:
            if data[0] == successor:
                return True
        return False
