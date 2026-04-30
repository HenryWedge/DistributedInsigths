from copy import deepcopy
from typing import List

from algo.datastructure.alignment_constants import SKIP, MODEL_COST, LOG_COST
from algo.datastructure.alignment_element import AlignmentElement
from algo.datastructure.located_activity import LocatedActivity


class Alignment:
    def __init__(self):
        self.elements: List[AlignmentElement] = []
        self.processed_events = 0

    def get_elements(self):
        [AlignmentElement(element.log.activity, element.model.activity) for element in self.elements]

    def increment_processed_events(self):
        self.processed_events += 1

    def sync_move(self, sync_move: LocatedActivity):
        this_alignment = deepcopy(self)
        this_alignment.elements.append(AlignmentElement(sync_move, sync_move))
        return this_alignment

    def move_on_model_skip_log(self, model_move: LocatedActivity):
        this_alignment = deepcopy(self)
        this_alignment.elements.append(AlignmentElement(model_move, SKIP))
        return this_alignment

    def move_on_log_skip_model(self, log_move: LocatedActivity):
        this_alignment = deepcopy(self)
        this_alignment.elements.append(AlignmentElement(SKIP, log_move))
        return this_alignment

    def get_cost(self):
        cost = 0
        for element in self.elements:
            if element.log == SKIP:
                cost += MODEL_COST
            elif element.model == SKIP:
                cost += LOG_COST
        return cost

    def is_empty(self):
        return not bool(self.elements)

    def __add__(self, other):
        this_self = deepcopy(self)
        if not other:
            return this_self
        resulting_alignment = Alignment()
        resulting_alignment.elements.extend(this_self.elements)
        resulting_alignment.elements.extend(other.elements)
        return resulting_alignment

    def __lt__(self, other):
        if self.get_cost() == other.get_cost():
            if len(self.elements) == len(other.elements):
                return hash(self) < hash(other)
            return len(self.elements) < len(other.elements)
        return self.get_cost() < other.get_cost()

    def __eq__(self, other):
        if len(self.elements) != len(other.elements):
            return False

        for i in range(len(self.elements)):
            if self.elements[i] != other.elements[i]:
                return False
        return True

    def __str__(self):
        final_string = ""
        for element in self.elements:
            final_string += str(element) + "\n"
        return f"[Cost:{self.get_cost()}]\n{final_string}"

    def get_all_log_moves(self):
        all_log_moves = []
        for element in self.elements:
            if element.log != SKIP:
                all_log_moves.append(element.log)
        return all_log_moves

    def contains_log_moves(self):
        return len(self.get_all_log_moves()) > 0

    def append_missing_log_moves(self, log_moves):
        missing_log_moves = []
        for log_move in log_moves:
            if log_move not in self.get_all_log_moves():
                missing_log_moves.append(log_move)
        if not missing_log_moves:
            return deepcopy(self)
        alignment = deepcopy(self)
        for log_move in missing_log_moves:
            alignment = alignment.move_on_log_skip_model(log_move)
        return alignment

    def __hash__(self):
        return hash(frozenset(self.elements))
