from datetime import datetime
from typing import Dict, List

from algo.alignment import Alignment
from algo.alignment_builder import AlignmentBuilder
from algo.alignment_timestamped import AlignmentTimestamped
from algo.event import Event
from algo.network import Network
from algo.new_trie import NewTrie
from algo.state_explorer import StateExplorer
from algo.state_item import StateItem
from algo.state_with_time import StateWithTime
from algo.trie_node import Node, Activity
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

    def process_event(self, event):
        case_id = event.case_id
        is_init = False

        alignment_states: List[StateWithTime] = []
        for node in self.network.get_all_nodes(self.node_id):
            alignment_state = node.get_current_state(event)
            if alignment_state is not None:
                alignment_states.append(alignment_state)
        if case_id not in self.state_explorer:
            if alignment_states:
                self._init_state_for_case(event, False)
                is_init = True
            else:
                self._init_state_for_case(event, True)

        if alignment_states:
            latest_alignment_state: StateWithTime = max(alignment_states)

            if not case_id in self.latest_event or latest_alignment_state.time > self.latest_event[case_id].time:
                # TODO hrei Instead of this logic take the "ingress node" and perform the alignments from there
                latest_tries = self.get_distinct_tries(self.state_explorer[case_id].get_all_states())
                if is_init:
                    latest_tries = [TrieTraverser(self.local_trie).find_activity_in_trie(latest_alignment_state.node)[
                        0]]  # [state.trie for state in latest_alignment_state.states]
                self.state_explorer[case_id].clear()

                for state in latest_alignment_state.states:
                    for latest_trie in latest_tries:
                        self.state_explorer[case_id].insert_state(
                            StateItem(state.cost, latest_trie, state.alignment, state.last_activity)
                        )
                new_alignment_states = self.alignment_builder.build_alignment(
                    latest_alignment_state.node, latest_alignment_state.time, self.state_explorer[case_id]
                )
                for state in new_alignment_states:
                    self.state_explorer[case_id].insert_state(state)
                # TODO hrei here we have to quantify the Real Skip_node_cost

        new_alignment_states = self.alignment_builder.build_alignment(
            Activity(event.activity), event.time, self.state_explorer[case_id]
        )
        self.latest_event[case_id] = event
        for state in new_alignment_states:
            self.state_explorer[case_id].insert_state(state)
        self.state_explorer[case_id].prune()
        print(event.activity)
        print([str(item.alignment) for item in self.state_explorer[case_id].top()])
        # print([str(item.trie) for item in self.state_explorer[case_id].top()])
        # print(self.state_explorer[case_id].top(2).trie)
        # print(f"size: {len(self.state_explorer[case_id].heap)}")

    def _init_state_for_case(self, event: Event, initialize=True):
        if not initialize:
            self.state_explorer[event.case_id] = StateExplorer(
                StateItem(
                    0, None, AlignmentTimestamped(
                        alignment=Alignment(), timestamp=datetime(1, 1, 1), node=Node(self.node_id, event.activity)),
                    last_activity=None
                )
            )
        else:
            self.state_explorer[event.case_id] = StateExplorer(
                StateItem(
                    0, self.local_trie, AlignmentTimestamped(
                        alignment=Alignment(), timestamp=datetime(1, 1, 1), node=Node(self.node_id, event.activity)),
                    last_activity=None
                )
            )

    def get_distinct_tries(self, states: List[StateItem]):
        tries = []
        for state in states:
            if not state.trie in tries:
                tries.append(state.trie)
        return tries
