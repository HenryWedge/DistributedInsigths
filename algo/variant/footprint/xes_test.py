import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer
from datetime import datetime

from algo.variant.footprint.withcontext import DistributedFootprint, Event


def run_xes_test(file_path: str, context_size: int = 2):
    # 1. XES Log laden
    log = xes_importer.apply(file_path)

    # Netzwerk initialisieren
    net = Network()
    nodes = {}

    def get_or_create_node(node_id):
        if node_id not in nodes:
            nodes[node_id] = DistributedFootprint(net, node_id)
        return nodes[node_id]

    # 2. Training-Phase (80% des Logs)
    # Wir bauen die Footprint-Matrizen aller beteiligten Knoten auf
    split_index = int(len(log) * 0.8)
    train_log = log[:split_index]
    test_log = log[split_index:]

    print(f"Lerne Footprint aus {len(train_log)} Traces...")

    for trace in train_log:
        history = []  # Speichert (node, activity)
        for event in trace:
            activity = event["concept:name"]
            # Wir nutzen die Resource als Node, falls nicht vorhanden, ein Default
            node_id = event.get("org:group", "Default_Node")

            # Wenn wir genug Historie für den Kontext haben
            if len(history) >= context_size:
                current_context = tuple(history[-context_size:])
                target_node = get_or_create_node(node_id)
                target_node.footprint_matrix.add_relation(current_context, node_id, activity)

            history.append((node_id, activity))

    print("Training abgeschlossen. Starte Conformance Checking...")
    print("-" * 50)

    # 3. Conformance Phase (20% des Logs)
    for trace in test_log:
        case_id = trace.attributes.get("concept:name", "unknown")
        print(f"\nPrüfe Case: {case_id}")

        for event in trace:
            activity = event["concept:name"]
            node_id = event.get("org:group", "Default_Node")
            timestamp = event["time:timestamp"]

            # In diesem verteilten Szenario müssen wir sicherstellen,
            # dass das Event-Objekt die richtigen Attribute hat
            dist_event = Event(case_id, activity, node_id, timestamp)

            current_node = get_or_create_node(node_id)
            current_node.check_conformance(dist_event)


# --- Hilfsklasse Network (falls nicht importiert) ---
class Network:
    def __init__(self):
        self.nodes = {}

    def add_node(self, node_id, node_instance):
        self.nodes[node_id] = node_instance

    def get_node(self, node_id):
        return self.nodes.get(node_id)


if __name__ == "__main__":
    try:
        run_xes_test("../../Sepsis.xes")
    except Exception as e:
        print(f"Fehler: {e}")
        print("Hinweis: Lade dir eine .xes Datei herunter (z.B. von BPI Challenges) oder nutze ein pm4py Sample.")