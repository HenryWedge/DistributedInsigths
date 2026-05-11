from datetime import timedelta, datetime
from typing import Dict, List

from algo.datastructure.event import Event
from algo.network import Network


class Relation:
    def __init__(self, predecessor: str, successor: str):
        self.pre = predecessor
        self.suc = successor

    def __hash__(self):
        return hash((self.pre, self.suc))

    def __eq__(self, other):
        return self.pre == other.pre and self.suc == other.suc

    def is_successor(self, activity_name: str):
        return self.suc == activity_name


class DistributedFootprint(Network):

    def __init__(self, network: Network, node_id: str):
        super().__init__()
        self.network = network
        self.node_id = node_id
        self.footprint_matrix: FootprintMatrix = FootprintMatrix()
        self.network.add_node(self.node_id, self)
        self.events: List[Event] = []

    def check_conformance(self, event: Event):
        # 1. Speichere das aktuelle Event lokal
        self.events.append(event)

        # 2. Finde ALLE potenziellen Vorgänger-Knoten aus der Matrix
        possible_relations = self.footprint_matrix.get_predecessor(self.node_id)

        if not possible_relations:
            print(f"Info: Kein bekannter Vorgänger für {self.node_id} (Initial-Event?).")
            return

        candidate_events = []

        # 3. Alle potenziellen Knoten abfragen
        for rel in possible_relations:
            pred_node_id = rel.pre
            pred_node = self.network.get_node(pred_node_id)

            if pred_node:
                last_event = pred_node.get_last_event_for_case(event.case_id)
                if last_event:
                    candidate_events.append((pred_node_id, last_event))

        # 4. Den zeitlich nächsten Vorgänger bestimmen
        if candidate_events:
            valid_predecessors = [
                (node_id, e) for node_id, e in candidate_events
                if e.time < event.time
            ]

            if valid_predecessors:
                true_pred_id, true_event = max(valid_predecessors, key=lambda x: x[1].time)

                print(f"Conformance OK: '{true_pred_id}' ist der direkte Vorgänger für Case {event.case_id} "
                      f"(Zeitdifferenz: {event.time - true_event.time})")
            else:
                print(f"Violation: In Case {event.case_id} wurden Events bei Vorgängern gefunden, "
                      f"aber alle liegen zeitlich nach {self.node_id}!")
        else:
            print(f"Violation: Case {event.case_id} ist bei keinem der erwarteten Vorgänger bekannt.")


    def get_last_event_for_case(self, case_id: str) -> Event:
        case_events = [e for e in self.events if e.case_id == case_id]
        if not case_events:
            return None
        return max(case_events, key=lambda e: e.time)

    def is_predecessor(self, case_id):
        return any(e.case_id == case_id for e in self.events)

class FootprintMatrix:
    def __init__(self):
        self.data: Dict[Relation, int] = {}

    def add_relation(self, predecessor: str, successor: str):
        rel = Relation(predecessor, successor)
        self.data[rel] = self.data.get(rel, 0) + 1

    def get_predecessor(self, successor_node_id: str) -> List[Relation]:
        return [rel for rel in self.data.keys() if rel.is_successor(successor_node_id)]


def run_test():
    print("=== Starte Distributed Conformance Test ===\n")

    net = Network()
    node_a = DistributedFootprint(net, "A")
    node_b = DistributedFootprint(net, "B")

    node_b.footprint_matrix.add_relation("A", "B")

    time_1 = datetime.now()
    event_1 = Event(case_id="Case_123", activity="A", time=time_1, location="A")
    node_a.events.append(event_1)
    node_a.events.append(event_1)
    print(f"Schritt 1: Event bei Knoten A registriert ({time_1})")

    time_2 = time_1 + timedelta(minutes=5)
    event_2 = Event(case_id="Case_123", activity="B", time=time_2, location="B")

    node_b.check_conformance(event_2)

    time_3 = time_1 - timedelta(minutes=10)
    event_3 = Event(case_id="Case_999", activity="B", time=time_3, location="B")

    node_a.events.append(Event(case_id="Case_999", activity="A", time=time_1, location="A"))
    node_b.check_conformance(event_3)


if __name__ == "__main__":
    run_test()