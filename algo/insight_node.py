from datetime import datetime
from typing import Dict, List

from algo.alignment import Alignment
from algo.alignment_builder import AlignmentBuilder
from algo.alignment_timestamped import AlignmentTimestamped
from algo.network import Network
from algo.state_explorer import StateExplorer
from algo.state_item import StateItem
from algo.state_with_time import StateWithTime
from algo.trie import Trie
from algo.trie_node import Node, Activity

class InsightNode:
    def __init__(self, trie: Trie, node_id: str, network: Network):
        self.node_id = node_id
        self.network: Network = network
        self.local_trie = trie
        self.alignment_builder: AlignmentBuilder = AlignmentBuilder()
        self.state_explorer: Dict[str, StateExplorer] = {}
        self.latest_ts: Dict[str, datetime] = {}

    def get_current_state(self, case_id) -> StateWithTime | None:
        if case_id not in self.state_explorer:
            return None
        return StateWithTime(self.latest_ts[case_id], self.state_explorer[case_id].get_all_states(), Node(self.node_id))

    def process_event(self, event):
        if event.activity == "Release B":
            print("Stop")

        case_id = event.case_id
        if case_id not in self.state_explorer:
            self._init_state_for_case(case_id)

        alignment_states: List[StateWithTime] = []
        for node in self.network.get_all_nodes(self.node_id):
            alignment_state = node.get_current_state(case_id)
            if alignment_state is not None:
                alignment_states.append(alignment_state)

        if alignment_states:
            latest_alignment_state: StateWithTime = max(alignment_states)
            if not case_id in self.latest_ts or latest_alignment_state.time > self.latest_ts[case_id]:
                #TODO hrei: Not only take the last entry somehow
                latest_trie = self.state_explorer[case_id].top()[0].trie

                self.state_explorer[case_id].clear()
                for state in latest_alignment_state.states:
                    self.state_explorer[case_id].insert_state(
                        StateItem(state.cost, latest_trie, state.alignment)
                    )
                new_alignment_states = self.alignment_builder.build_alignment(
                    latest_alignment_state.node, latest_alignment_state.time, self.state_explorer[case_id]
                )
                for state in new_alignment_states:
                    self.state_explorer[case_id].insert_state(state)
            #TODO hrei here we have to quantify the Real Skip_node_cost


        new_alignment_states = self.alignment_builder.build_alignment(Activity(event.activity), event.time, self.state_explorer[case_id])
        self.latest_ts[case_id] = event.time
        for state in new_alignment_states:
            self.state_explorer[case_id].insert_state(state)
        self.state_explorer[case_id].prune()
        print(event.activity)
        print([str(item.alignment) for item in self.state_explorer[case_id].top()])
        #print([str(item.trie) for item in self.state_explorer[case_id].top()])
        #print(self.state_explorer[case_id].top(2).trie)
        #print(f"size: {len(self.state_explorer[case_id].heap)}")

    def _init_state_for_case(self, case_id):
        self.state_explorer[case_id] = StateExplorer(
            StateItem(
                0, self.local_trie, AlignmentTimestamped(
                    alignment=Alignment(), timestamp=datetime(1, 1, 1), node=Node(self.node_id)
                )
            )
        )
