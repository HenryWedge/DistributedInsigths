from pm4py.objects.log.importer.xes import importer as xes_importer

from typing import List, Dict, Optional

from algo.datastructure.event import Event


class Relation:
    def __init__(self, context: tuple, successor_node: str, successor_activity: str):
        self.context = context  # Tuple von (node_id, activity)
        self.suc_node = successor_node
        self.suc_act = successor_activity

    def __hash__(self):
        return hash((self.context, self.suc_node, self.suc_act))

    def __eq__(self, other):
        return (isinstance(other, Relation) and
                self.context == other.context and
                self.suc_node == other.suc_node and
                self.suc_act == other.suc_act)

    def is_successor(self, node_id: str, activity: str):
        return self.suc_node == node_id and self.suc_act == activity

class FootprintMatrix:
    def __init__(self):
        self.data: Dict[Relation, int] = {}

    def add_relation(self, context: tuple, suc_node: str, suc_act: str):
        rel = Relation(context, suc_node, suc_act)
        self.data[rel] = self.data.get(rel, 0) + 1

    def get_predecessors(self, node_id: str, activity: str) -> List[Relation]:
        return [rel for rel in self.data.keys() if rel.is_successor(node_id, activity)]


class Network:
    def __init__(self):
        self.nodes: Dict[str, 'DistributedFootprint'] = {}

    def add_node(self, node_id: str, node_instance: 'DistributedFootprint'):
        self.nodes[node_id] = node_instance

    def get_node(self, node_id: str) -> Optional['DistributedFootprint']:
        return self.nodes.get(node_id)


class DistributedFootprint:
    def __init__(self, network: Network, node_id: str, context_size: int = 2):
        self.network = network
        self.node_id = node_id
        self.context_size = context_size
        self.footprint_matrix = FootprintMatrix()
        self.network.add_node(self.node_id, self)
        self.events: List[Event] = []

    def check_conformance(self, event: Event):
        self.events.append(event)
        possible_relations = self.footprint_matrix.get_predecessors(self.node_id, event.activity)

        if not possible_relations:
            return False

        valid_contexts_found = []

        for rel in possible_relations:
            if len(rel.context) == 0:
                valid_contexts_found.append(rel.context)
                continue

            current_context_events = []
            context_is_valid = True

            for (p_node_id, p_act) in reversed(rel.context):
                p_node = self.network.get_node(p_node_id)
                if not p_node:
                    context_is_valid = False
                    break

                last_event = p_node.get_last_event_for_case(event.case_id, p_act)
                if last_event and (not current_context_events or last_event.time < current_context_events[-1].time):
                    if last_event.time < event.time:
                        current_context_events.append(last_event)
                    else:
                        context_is_valid = False
                        break
                else:
                    context_is_valid = False
                    break

            if context_is_valid and len(current_context_events) == len(rel.context):
                valid_contexts_found.append(rel.context)

        if valid_contexts_found:
            best_ctx = max(valid_contexts_found, key=len)
            return True
        else:
            return False

    def get_last_event_for_case(self, case_id: str, activity: str) -> Optional[Event]:
        relevant = [e for e in self.events if e.case_id == case_id and e.activity == activity]
        return max(relevant, key=lambda e: e.time) if relevant else None

def run_distributed_conformance(xes_path: str, n_size: int = 1000):
    print(f"Log file: {xes_path}...")
    log = xes_importer.apply(xes_path)[0:100]
    net = Network()

    def get_node(node_id: str) -> DistributedFootprint:
        if node_id not in net.nodes:
            return DistributedFootprint(net, node_id, context_size=n_size)
        return net.nodes[node_id]

    split = int(len(log) * 0.8)
    train_log = log[:split]
    test_log = log[split:]

    for trace in train_log:
        history = []
        for event in trace:
            act = event["concept:name"]
            node = event.get("org:group", "Default_Node")
            curr_ctx = tuple(history[-(min(len(history), n_size)):])

            get_node(node).footprint_matrix.add_relation(curr_ctx, node, act)
            history.append((node, act))

    for trace in test_log:
        case_id = trace.attributes.get("concept:name", "unknown")
        print(f"\nTrace {case_id}:")
        for pm4pyEvent in trace:
            event = Event(
                case_id=case_id,
                activity=pm4pyEvent["concept:name"],
                location=pm4pyEvent.get("org:group", "Default_Node"),
                time=pm4pyEvent["time:timestamp"]
            )
            print(event)
            print(get_node(event.location).check_conformance(event))


if __name__ == "__main__":
    run_distributed_conformance("../../Sepsis.xes")