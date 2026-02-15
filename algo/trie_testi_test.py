from algo.network import Network
from algo.trie_testi import LocatedActivity, NetworkNode, Trie, TrieBuilder


def get_training_traces():
    return [
        [
            LocatedActivity("A", "n1"),
            LocatedActivity("B", "n1"),
            LocatedActivity("E", "n2"),
            LocatedActivity("F", "n2"),
            LocatedActivity("H", "n2"),
            LocatedActivity("G", "n4")
        ],
        [
            LocatedActivity("A", "n1"),
            LocatedActivity("C", "n1"),
            LocatedActivity("D", "n3"),
            LocatedActivity("G", "n4")
        ]
    ]


def get_validation_trace():
    return [
        LocatedActivity("A", "n1"),
        LocatedActivity("B", "n1"),
        LocatedActivity("D", "n3"),
        LocatedActivity("F", "n2"),
        LocatedActivity("G", "n4")
    ]

def run(central=False):
    trie_builders = {}
    last_event = None
    for trace in get_training_traces():
        for located_activity in trace:
            if located_activity.location not in trie_builders:
                trie_builders[located_activity.location] = TrieBuilder(Trie())
            if central:
                located_activity.location = "n1"
                trie_builders["n1"].insert(located_activity)
            else:
                if last_event and last_event.location != located_activity.location:
                   trie_builders[located_activity.location].insert(last_event)
                trie_builders[located_activity.location].insert(located_activity)
            last_event = located_activity
        for trie_id in trie_builders:
            trie_builders[trie_id].reset()
        last_event = None

    network = Network()
    for key in trie_builders:
        NetworkNode(trie_builders[key].root_trie, network, key)

    for i, located_activity in enumerate(get_validation_trace()):
        if central:
            alignment = network.get_node("n1").process_event(located_activity, i)
        else:
            alignment = network.get_node(located_activity.location).process_event(located_activity, i)
        print(alignment)

if __name__ == '__main__':
    run(False)
    print("---")
    run(True)