import heapq
from abc import ABC
from typing import List
from algo.event import Event
from algo.network import Network
from algo.state_with_time import StateWithTime

class CollectPreviousAlignmentsStrategy(ABC):
    def __init__(self, network: Network, node_id: str):
        self.network = network
        self.node_id = node_id

    def collect_alignment_states(self, event: Event) -> List[StateWithTime]:
        pass

class CollectPreviousAlignmentsStrategyAskAll(CollectPreviousAlignmentsStrategy):
    def __init__(self, network: Network, node_id: str):
        super().__init__(network, node_id)
        self.network_requests = 0

    def collect_alignment_states(self, event: Event) -> List[StateWithTime]:
        alignment_states: List[StateWithTime] = []
        for node in self.network.get_all_nodes(self.node_id):
            alignment_state = node.get_current_state(event)
            self.network_requests += 1
            if alignment_state is not None:
                alignment_states.append(alignment_state)
        return alignment_states

class NodeOccurrence:
    def __init__(self, occurrence_count: int, node):
        self.occurrence_count = occurrence_count
        self.node = node

    def increment(self):
        self.occurrence_count += 1

    def __lt__(self, other):
        return self.occurrence_count < other.occurrence_count

class CollectPreviousAlignmentsStrategyAskOptimistically(CollectPreviousAlignmentsStrategy):
    def __init__(self, network: Network, node_id: str):
        super().__init__(network, node_id)
        self.predecessor_occurrences = {}
        self.network_requests = 0

    def collect_alignment_states(self, event: Event) -> List[StateWithTime]:
        possible_nodes = self.network.get_all_nodes(self.node_id)
        nodes = []
        if not self.predecessor_occurrences:
            for node in possible_nodes:
                self.predecessor_occurrences[node] = 0
                heapq.heappush(nodes, NodeOccurrence(0, node))
        else:
            for predecessor in self.predecessor_occurrences:
                heapq.heappush(nodes, NodeOccurrence(self.predecessor_occurrences[predecessor], predecessor))
        for node_occurrence in nodes:
            node = node_occurrence.node
            alignment_state = node.get_current_state(event)
            self.network_requests += 1
            if alignment_state:
                self.predecessor_occurrences[node] = self.predecessor_occurrences[node] + 1
                return [alignment_state]
        return []