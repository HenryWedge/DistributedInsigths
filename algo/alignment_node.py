import sys
from typing import List, Any

from algo.datastructure.alignment import Alignment
from algo.alignments.alignment_calculator import calculate_alignment
from algo.datastructure.alignment_repsonse import AlignmentResponse
from algo.datastructure.located_activity import LocatedActivity
from algo.network import Network
from algo.datastructure.trie import Trie

class NetworkNode:
    def __init__(self, model, network, node_id):
        self.node_id = node_id
        self.network: Network = network
        self.network.add_node(self.node_id, self)
        self.i = -1
        self.model: Trie = model
        self.observed_events = {}
        self.cache = {}

    def _get_entry_points_containing_label(self, label):
        return [child for child in self.model.get_children() if
                child.label.location != self.node_id and child.contains(label)]

    def _get_trace(self, min_i=-1, max_i=sys.maxsize):
        filtered = {k: v for k, v in self.observed_events.items() if min_i < k < max_i}
        return [value for key, value in sorted(filtered.items())]

    def get_all_moves(self, i):
        result = []
        for key in self.observed_events:
            if key < i:
                result.append(self.observed_events[key])
        return result

    def get_alignment(self, rec_depth, target: LocatedActivity, i) -> AlignmentResponse:
        response: AlignmentResponse = self.find_best_alignment(rec_depth + 1, target, i)
        if not response:
            return None

        return AlignmentResponse(
            max(self.i, response.timestamp),
            response.alignment,
            target,
            response.last_node
        )

    def process_event(self, located_activity: LocatedActivity, i: int) -> Alignment:
        self.i = i
        self.observed_events[i] = located_activity
        response = self.find_best_alignment(0, located_activity, i, is_start=True)
        return response.alignment

    def find_best_alignment(self, rec_depth, target: LocatedActivity = None, i=sys.maxsize, is_start=False) -> Any:
        all_candidate_alignments: List[AlignmentResponse] = []
        #print(rec_depth)
        for entry_point in self.model.get_children_containing_label(target):
            response, model = self._request_external_alignment(rec_depth, entry_point, i)
            last_node = response.last_node
            trace = self._get_relevant_local_trace(i, is_start, last_node, response.timestamp)
            local_alignment = calculate_alignment(trace, model, target)

            if local_alignment.contains_log_moves():
                last_node = self.node_id

            candidate_alignment = response.alignment + local_alignment
            all_candidate_alignments.append(
                AlignmentResponse(response.timestamp, candidate_alignment, target, last_node))

        if not all_candidate_alignments:
            return calculate_alignment(self._get_trace(), self.model, target)
        all_candidate_alignments = self._add_external_log_moves(all_candidate_alignments, i)
        best_alignment_response = min(all_candidate_alignments, key=lambda x: x.alignment)

        return AlignmentResponse(
            best_alignment_response.timestamp,
            best_alignment_response.alignment,
            target, best_alignment_response.last_node
        )

    def get_alignment_global(self, i):
        max_response = None
        max_target = None
        for target in self.model.get_leaves():
            response: AlignmentResponse = self.find_best_alignment(target, i)
            if not max_response or response.timestamp > max_response.timestamp:
                max_response = response
                max_target = target

        return AlignmentResponse(
            max(self.i, max_response.timestamp),
            max_response.alignment,
            max_target,
            max_response.last_node
        )

    def _add_external_log_moves(self, responses: List[AlignmentResponse], i):
        all_log_moves = []
        response_with_external_log_moves = []
        for node in self.network.get_all_nodes(self.node_id):
            all_log_moves.extend(node.get_all_moves(i))
        for response in responses:
            alignment_with_log_moves = response.alignment.append_missing_log_moves(all_log_moves)
            response.alignment = alignment_with_log_moves
            response_with_external_log_moves.append(response)
        return response_with_external_log_moves

    def _request_external_alignment(self, rec_depth, entry_point: Trie, i: int) -> tuple[AlignmentResponse, Trie]:
        model = self.model
        if self.node_id == entry_point.location:
            alignment_response = AlignmentResponse(-1, Alignment(), entry_point, None)
        else:
            if entry_point in self.cache:
                alignment_response = self.cache[entry_point]
            else:
                alignment_response = (
                    self.network.get_node(entry_point.location).get_alignment(rec_depth, entry_point, i))
            model = self.model.get_child(entry_point)

        self.cache[entry_point] = alignment_response
        return alignment_response, model

    def _get_relevant_local_trace(self, i: int, is_start: bool, last_node, timestamp: int) -> list[Any]:
        max_time = i if not is_start and i == self.i else sys.maxsize
        min_time = timestamp - 1 if last_node == self.node_id else timestamp
        return self._get_trace(min_time, max_time)
