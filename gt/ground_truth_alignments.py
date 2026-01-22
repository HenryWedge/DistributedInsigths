import pm4py
from pm4py import PetriNet, Marking
from pm4py.objects.log.obj import EventLog
from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments

class GroundTruthAlignments:

    def __init__(self):
        self.model: tuple[PetriNet, Marking, Marking] | None = None

    def mine_process_model(self, event_log: EventLog):
        self.model = pm4py.discover_petri_net_heuristics(event_log)

    def calculate_alignments(self, event_log: EventLog):
        parameters = {
            alignments.Variants.VERSION_DISCOUNTED_A_STAR: True,
        }
        aligned_traces = alignments.apply_log(
            event_log,
            self.model[0],
            self.model[1],
            self.model[2],
            parameters=parameters
        )

        for index, result in enumerate(aligned_traces):
            print(f"Trace {index}: {event_log[index].attributes['concept:name']}")
            print(f"  Alignment Fitness: {result['fitness']}")
            print(f"  Cost: {result['cost']}")
            print(f"  Alignment: {result['alignment']}\n")