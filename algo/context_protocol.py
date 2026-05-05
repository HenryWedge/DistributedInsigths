import sys
from copy import deepcopy
from typing import Dict, List

from algo.datastructure.alignment import Alignment
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
        return len(self.elements) == 1 and self.elements[0] == "<start>"

    def __eq__(self, other):
        return self.elements == other.elements

    def __hash__(self):
        return hash(self.elements)


class ContextProtocolNode:
    def __init__(self, node_id, network):
        self.node_id = node_id
        self.network: Network = network
        self.network.add_node(self.node_id, self)
        self.observed_events = {}
        self.latest_alignment = Alignment()
        self.entry_points: Dict[str, List[Context]] = {}

    def add_entry_point(self, activity: str, context: Context):
        self.entry_points[activity].append(context)

    def get_insight(self, context, i):
        score = self.insight(context.head().activity, i)
        if not context.is_start() and context.body().elements:
            score += self.network.get_node(context.body().location()).get_insight(context.body(), i - 1)
        return score

    def _get_events(self, min_i=-1, max_i=sys.maxsize):
        filtered = {k: v for k, v in self.observed_events.items() if min_i < k < max_i}
        return [value for key, value in sorted(filtered.items())]

    def get_all_activities(self):
        return self._get_events()

    def insight(self, activity: str, i):
        alignment = Alignment()
        if activity in self._get_events() and activity in self.entry_points:
            alignment = alignment.sync_move(LocatedActivity(activity, ""))
        elif activity in self.entry_points:
            alignment = alignment.move_on_model_skip_log(LocatedActivity(activity, ""))
        for event in self._get_events(min_i=i - 1):
            if event not in self.entry_points:
                alignment = alignment.move_on_log_skip_model(LocatedActivity(event, ""))
        return alignment

    def process_activity(self, activity, i):
        alignment = Alignment()
        self.observed_events[i] = activity
        alignment += self.insight(activity, i)
        external_alignments = []
        if activity in self.entry_points:
            for ep in self.entry_points[activity]:
                if ep.is_start():
                    break
                else:
                    external_alignments.append(self.network.get_node(ep.location()).get_insight(ep, i))
            all_log_moves = set()
            for node in self.network.get_all_nodes(""):
                for lg_mv in node.get_all_activities():
                    all_log_moves.add(lg_mv)
            min_alignment = None

            if external_alignments:
                for align in external_alignments:
                    align += alignment
                    align = align.append_missing_log_moves(all_log_moves)
                    if not min_alignment or min_alignment > align:
                        min_alignment = align
            else:
                min_alignment = alignment
        else:
            latest_alignments = []
            for node in self.network.get_all_nodes(""):
                latest_alignments.append(node.latest_alignment)
            alignment += max(latest_alignments)
            min_alignment = alignment
        self.latest_alignment = min_alignment
        return self.latest_alignment


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
                    if not current_event.activity in node.entry_points:
                        node.entry_points[current_event.activity] = [Context(["<start>"])]
                    # if current_event not in node.entry_points:
                    #    node.add_entry_point(current_event.activity, new_context)
                else:
                    new_context = Context(deepcopy(history))
                    if current_event.activity not in node.entry_points:
                        node.entry_points[current_event.activity] = []
                    if new_context not in node.entry_points[current_event.activity]:
                        node.add_entry_point(current_event.activity, new_context)
                history.append(current_event)
        return network


if __name__ == '__main__':
    network: Network = ModelTrainer().learn(
        [[
            LocatedActivity("A", "n1"),
            LocatedActivity("B", "n1"),
            LocatedActivity("E", "n2"),
            LocatedActivity("F", "n2"),
            LocatedActivity("H", "n2"),
            LocatedActivity("G", "n4")
        ],
            [
                LocatedActivity("A", "n1"),
                LocatedActivity("C", "n1"),
                LocatedActivity("D", "n3"),
                LocatedActivity("G", "n4")
            ]]
        # [
        #    [
        #        LocatedActivity("X", "n1"),
        #        LocatedActivity("A", "n1"),
        #        LocatedActivity("C", "n2"),
        #        LocatedActivity("E", "n3")
        #    ],
        #    [
        #        LocatedActivity("X", "n1"),
        #        LocatedActivity("B", "n1"),
        #        LocatedActivity("C", "n2"),
        #        LocatedActivity("D", "n3"),
        #    ]
        # ]
    )

    # print(network.get_node("n1").process_activity("X", 0))
    # print("---")
    # print(network.get_node("n1").process_activity("B", 1))
    # print("---")
    # print(network.get_node("n1").process_activity("F", 2))
    ##print("---")
    ##print(network.get_node("n2").process_activity("C", 3))
    # print("---")
    # print(network.get_node("n3").process_activity("D", 4))

    print(network.get_node("n1").process_activity("A", 0))
    print(network.get_node("n1").process_activity("B", 1))
    print(network.get_node("n3").process_activity("D", 2))
    print(network.get_node("n2").process_activity("F", 3))
    print(network.get_node("n4").process_activity("G", 4))
