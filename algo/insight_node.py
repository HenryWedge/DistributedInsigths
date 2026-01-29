from datetime import datetime
from typing import Dict, List, Any

from algo.alignment import Alignment
from algo.alignment_builder import AlignmentBuilder
from algo.alignment_timestamped import AlignmentTimestamped
from algo.event import Event
from algo.network import Network
from algo.new_trie import NewTrie
from algo.state_explorer import StateExplorer
from algo.state_item import StateItem
from algo.state_with_time import StateWithTime
from algo.trie_node import Node, Activity, TrieNode
from algo.trie_traverser import TrieTraverser


class InsightNode:
    def __init__(self, trie: NewTrie, node_id: str, network: Network):
        self.node_id = node_id
        self.network: Network = network
        self.local_trie = trie
        self.alignment_builder: AlignmentBuilder = AlignmentBuilder()
        self.state_explorer: Dict[str, StateExplorer] = {}
        self.latest_event: Dict[str, Event] = {}

    def get_current_state(self, event) -> StateWithTime | None:
        if event.case_id not in self.state_explorer:
            return None

        return StateWithTime(
            self.latest_event[event.case_id].time,
            self.state_explorer[event.case_id].get_all_states(),
            Node(self.node_id, self.latest_event[event.case_id].activity)
        )

    def _collect_alignment_states(self, event: Event):
        alignment_states: List[StateWithTime] = []
        for node in self.network.get_all_nodes(self.node_id):
            alignment_state = node.get_current_state(event)
            if alignment_state is not None:
                alignment_states.append(alignment_state)
        return alignment_states

    def _insert_new_states(self, case_id, new_alignment_states: List[StateItem]):
        for state in new_alignment_states:
            self.state_explorer[case_id].insert_state(state)

    def is_new_alignment(self, case_id: str, latest_alignment_state: StateWithTime):
        return not case_id in self.latest_event or latest_alignment_state.time > self.latest_event[case_id].time

    def find_entrypoint_in_model(self, node: TrieNode):
        # TODO hrei consider cost
        return [
            TrieTraverser(self.local_trie).find_activity_in_trie(node)[0]
        ]

    def process_event(self, event):
        case_id = event.case_id
        alignment_states: List[StateWithTime] = self._collect_alignment_states(event)
        has_trace_started_on_other_node = case_id not in self.state_explorer and bool(alignment_states)

        if case_id not in self.state_explorer:
            self._init_state_for_case(event, has_trace_started_on_other_node)

        self.integrate_previous_state(alignment_states, case_id, has_trace_started_on_other_node)

        new_alignment_states = self.alignment_builder.build_alignment(
            Activity(event.activity), event.time, self.state_explorer[case_id]
        )

        self.latest_event[case_id] = event
        self._insert_new_states(case_id, new_alignment_states)
        self.state_explorer[case_id].prune()

        # print(event.activity)
        print([str(item.alignment) for item in self.state_explorer[case_id].top()])
        # print([str(item.trie) for item in self.state_explorer[case_id].top()])
        # print(self.state_explorer[case_id].top(2).trie)
        # print(f"size: {len(self.state_explorer[case_id].heap)}")

    def integrate_previous_state(
        self,
        alignment_states: list[StateWithTime],
        case_id,
        has_trace_started_on_other_node: bool
    ):
        if not alignment_states:
            return

        latest_alignment_state: StateWithTime = max(alignment_states)
        if not self.is_new_alignment(case_id, latest_alignment_state):
            return

        latest_tries = self.get_distinct_tries(self.state_explorer[case_id].get_all_states())
        if has_trace_started_on_other_node:
            latest_tries = self.find_entrypoint_in_model(latest_alignment_state.node)

        self.state_explorer[case_id].clear()
        self.accept_external_states(case_id, latest_alignment_state, latest_tries)
        new_alignment_states = self.alignment_builder.build_alignment(
            latest_alignment_state.node, latest_alignment_state.time, self.state_explorer[case_id]
        )
        self._insert_new_states(case_id, new_alignment_states)

    def accept_external_states(
            self,
            case_id,
            latest_alignment_state: StateWithTime,
            latest_tries: List[NewTrie]):
        for state in latest_alignment_state.states:
            for latest_trie in latest_tries:
                self.state_explorer[case_id].insert_state(
                    StateItem(state.cost, latest_trie, state.alignment, state.last_activity)
                )

    def _init_state_for_case(self, event: Event, has_trace_started_on_other_node=True):
        trie = None
        if not has_trace_started_on_other_node:
            trie = self.local_trie

        self.state_explorer[event.case_id] = StateExplorer(
            StateItem(
                0,
                trie,
                AlignmentTimestamped(
                    alignment=Alignment(),
                    timestamp=datetime(1, 1, 1),
                    node=Node(self.node_id, event.activity)
                ),
                last_activity=None
            )
        )

    def get_distinct_tries(self, states: List[StateItem]):
        tries = []
        for state in states:
            if not state.trie in tries:
                tries.append(state.trie)
        return tries
