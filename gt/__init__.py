from collections import defaultdict
from typing import List

import pm4py
from pm4py import PetriNet, Marking
from pm4py.objects.log.obj import EventLog
from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments

class GroundTruthAlignments:

    def __init__(self):
        self.model: tuple[PetriNet, Marking, Marking] | None = None

    def mine_process_model(self, event_log: EventLog):
        self.model = pm4py.discover_petri_net_inductive(event_log)

    def calculate_alignments(self, event_log: EventLog):
        model_costs = {t: (0 if t.label is None else 1) for t in self.model[0].transitions}
        costs = {t: (0 if t == ">>" else 1) for t in range(200)}

        parameters = {
            alignments.Variants.VERSION_DISCOUNTED_A_STAR: True,
            #alignments.Variants.VERSION_DISCOUNTED_A_STAR.value.PARAM_TRACE_COST_FUNCTION: lambda e: 2,
            alignments.Parameters.PARAM_TRACE_COST_FUNCTION: costs,
            alignments.Parameters.PARAM_MODEL_COST_FUNCTION: model_costs
        }
        aligned_traces = alignments.apply_log(
            event_log,
            self.model[0],
            self.model[1],
            self.model[2],
            parameters=parameters
        )

        for index, result in enumerate(aligned_traces):
            print(f"Trace {index}: {event_log[index].attributes['case:concept:name']}")
            print(f"Alignment Fitness: {result['fitness']}")
            # The alignment sequence shows the synchronous, move-on-log, and move-on-model steps
            print(f"Cost: {self.get_alignment_cost(result['alignment'])}")
            print(f"Alignment: {result['alignment']}\n")

    def get_alignment_cost(self, alignment: List[tuple[str, str]]) -> int:
        alignment_cost = 0
        for move in alignment:
            if not (move[0] == ">>" and move[1] is None) and not (move[0] == move[1]):
                alignment_cost = alignment_cost + 1
        return alignment_cost