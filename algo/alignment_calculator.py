import heapq

from algo.alignment import Alignment
from algo.trie import Trie


def calculate_alignment(trace, trie_node: Trie, target=None):
    start_node = trie_node
    queue = [(Alignment(), id(start_node), start_node, 0)]
    visited = set()

    while queue:
        path, _, current_node, trace_idx = heapq.heappop(queue)

        # Zielzustand: Ende der Trace UND Ende eines Pfades im Trie
        if target:
            # If we have a target we force to reach it
            if not current_node.is_root() and current_node.label.activity == target.activity:
                if target and trace_idx == len(trace):
                    return path
        else:
            if trace_idx == len(trace):
                return path

        state_id = (id(current_node), trace_idx)
        if state_id in visited:
            continue
        visited.add(state_id)

        # Sync Move
        if trace_idx < len(trace) and current_node.has_child(trace[trace_idx]):
            next_node = current_node.get_child(trace[trace_idx])
            heapq.heappush(queue, (
                path.sync_move(trace[trace_idx]),
                id(next_node),
                next_node,
                trace_idx + 1,
            ))

        # Model move
        for next_node in current_node.get_children():
            heapq.heappush(queue, (
                path.move_on_model_skip_log(next_node.label),
                id(next_node),
                next_node,
                trace_idx
            ))

        # Log move
        if trace_idx < len(trace):
            # In the central case we want to enforce that the alignment goes to the end of the trace
            if (
                    target
                    or trace_idx != len(trace) - 1
                    or not queue
            ):
                heapq.heappush(queue, (
                    path.move_on_log_skip_model(trace[trace_idx]),
                    id(current_node),
                    current_node,
                    trace_idx + 1
                ))

    return None