from copy import deepcopy
from typing import Dict, List

from algo.network import Network
from algo.alignment_node import LocatedActivity


class Context:
    def __init__(self, elements):
        self.elements = elements

    def body(self):
        return Context(self.elements[0:-1])

    def location(self):
        return self.elements[-1].location

    def activity(self):
        return self.elements[-1].activity

    def head(self):
        return self.elements[-1]

    def activities(self):
        return [element.activity for element in self.elements]

    def is_start(self):
        return len(self.elements) == 1

    def __eq__(self, other):
        return self.elements == other.elements

    def __hash__(self):
        return hash(self.elements)


class ContextProtocolNode:
    def __init__(self, node_id, network):
        self.node_id = node_id
        self.network: Network = network
        self.network.add_node(self.node_id, self)
        self.observed_events = []
        self.entry_points: Dict[str, List[Context]] = {}

    def add_entry_point(self, activity: str, context: Context):
        self.entry_points[activity].append(context)

    def get_insight(self, context):
        score = self.insight(context.head().activity)
        if not context.is_start():
            score += self.network.get_node(context.body().location()).get_insight(context.body())
        return score

    def insight(self, activity: str):
        print(activity)
        return 0 if activity in self.observed_events else 1

    def process_activity(self, activity):
        score = 0
        self.observed_events.append(activity)
        score += self.insight(activity)
        external_scores = []
        if activity in self.entry_points:
            for ep in self.entry_points[activity]:
                external_scores.append(self.network.get_node(ep.location()).get_insight(ep))
            score += min(external_scores)
        return score


class ModelTrainer:
    def learn(self, traces: List[List[LocatedActivity]]) -> Network:
        network = Network()
        for trace in traces:
            history: List[LocatedActivity] = []
            for current_event in trace:
                loc = current_event.location
                if not loc in network.nodes:
                    ContextProtocolNode(loc, network)
                node = network.get_node(loc)
                if not history:
                    if not "<start>" in node.entry_points:
                        node.entry_points["<start>"] = []
                    new_context = Context([current_event])
                    if new_context not in node.entry_points["<start>"]:
                        node.add_entry_point("<start>", new_context)
                else:
                    new_context = Context(deepcopy(history))
                    if current_event.activity not in node.entry_points:
                        node.entry_points[current_event.activity] = []
                    if new_context not in node.entry_points[current_event.activity]:
                        node.add_entry_point(current_event.activity, new_context)
                history.append(current_event)
        return network


if __name__ == '__main__':
    network: Network = ModelTrainer().learn([
        [
            LocatedActivity("X", "n1"),
            LocatedActivity("A", "n1"),
            LocatedActivity("C", "n2"),
            LocatedActivity("E", "n3")
        ],
        [
            LocatedActivity("X", "n1"),
            LocatedActivity("B", "n1"),
            LocatedActivity("C", "n2"),
            LocatedActivity("D", "n3"),
        ]
    ])

    print(network.get_node("n1").process_activity("X"))
    print("---")
    print(network.get_node("n1").process_activity("B"))
    print("---")
    print(network.get_node("n2").process_activity("C"))
    print("---")
    print(network.get_node("n3").process_activity("D"))
