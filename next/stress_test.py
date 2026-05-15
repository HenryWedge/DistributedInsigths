#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import hashlib
from typing import Dict, List, Tuple, Set, Optional

from algo.utility.event_log_splitter import EventLogSplitter


START_HASH = "START"
LOG_COST = 1
MODEL_COST = 1


def compute_hash(prev_hash: str, activity: str) -> str:
    return hashlib.sha256((prev_hash + activity).encode()).hexdigest()


class Transition:
    def __init__(self, prev_hash: str, activity: str):
        self.prev_hash = prev_hash
        self.activity = activity
        self.curr_hash = compute_hash(prev_hash, activity)


class Alignment:

    def __init__(self, moves: Optional[List[Tuple[Optional[str], Optional[str]]]] = None):
        self._moves: List[Tuple[Optional[str], Optional[str]]] = moves if moves is not None else []

    @property
    def moves(self) -> List[Tuple[Optional[str], Optional[str]]]:
        return self._moves

    @property
    def cost(self) -> int:
        c = 0
        for m, l in self._moves:
            if m is None:
                c += LOG_COST
            elif l is None:
                c += MODEL_COST
        return c

    def add_sync_move(self, activity: str) -> 'Alignment':
        return Alignment(self._moves + [(activity, activity)])

    def add_log_move(self, activity: str) -> 'Alignment':
        return Alignment(self._moves + [(None, activity)])

    def add_model_move(self, activity: str) -> 'Alignment':
        return Alignment(self._moves + [(activity, None)])

    @staticmethod
    def from_log_moves(events: List[str], log_idx: int) -> 'Alignment':
        return Alignment([(None, e) for e in events[:log_idx + 1]])


class Participant:
    def __init__(self, participant_id: str):
        self.id = participant_id
        self.transitions: List[Transition] = []
        self._memo: Dict[Tuple[str, int], Alignment] = {}

    def add_transition(self, prev_hash: str, activity: str) -> str:
        t = Transition(prev_hash, activity)
        self.transitions.append(t)
        return t.curr_hash

    def clear_memo(self):
        self._memo.clear()

    def get_transitions_by_curr_hash(self, curr_hash: str) -> List[Transition]:
        return [t for t in self.transitions if t.curr_hash == curr_hash]

    def min_cost_with_alignment(self, target_hash: str, log_idx: int,
                                events: List[str], network: 'Network') -> Alignment:
        if target_hash == START_HASH:
            return Alignment.from_log_moves(events, log_idx)

        key = (target_hash, log_idx)
        if key in self._memo:
            return self._memo[key]

        local_transitions = self.get_transitions_by_curr_hash(target_hash)

        best_align: Optional[Alignment] = None
        best_cost = float('inf')

        for t in local_transitions:
            align = network.compute_min_cost_with_alignment(t.prev_hash, log_idx, events, caller_id=self.id)
            candidate = align.add_model_move(t.activity)
            if candidate.cost < best_cost:
                best_cost = candidate.cost
                best_align = candidate

            if log_idx >= 0 and events[log_idx] == t.activity:
                align = network.compute_min_cost_with_alignment(t.prev_hash, log_idx - 1, events, caller_id=self.id)
                candidate = align.add_sync_move(t.activity)
                if candidate.cost < best_cost:
                    best_cost = candidate.cost
                    best_align = candidate

        if log_idx >= 0:
            align = network.compute_min_cost_with_alignment(target_hash, log_idx - 1, events, caller_id=self.id)
            candidate = align.add_log_move(events[log_idx])
            if candidate.cost < best_cost:
                best_cost = candidate.cost
                best_align = candidate

        if best_cost == float('inf'):
            best_align = Alignment.from_log_moves(events, log_idx)

        self._memo[key] = best_align
        return best_align


class Network:
    def __init__(self):
        self.event_stream: Dict[str, List[str]] = {}
        self.participants: Dict[str, Participant] = {}
        self.hash_owner: Dict[str, str] = {}
        self.route_calls = 0
        self.remote_calls = 0

    def reset_stats(self):
        self.route_calls = 0
        self.remote_calls = 0

    def get_total_states(self) -> int:
        return sum(len(p._memo) for p in self.participants.values())

    def register_participant(self, participant: Participant):
        self.participants[participant.id] = participant
        for t in participant.transitions:
            self.hash_owner[t.curr_hash] = participant.id

    def record_event(self, case_id: str, activity: str):
        if case_id not in self.event_stream:
            self.event_stream[case_id] = []
        self.event_stream[case_id].append(activity)

    def get_events(self, case_id: str) -> List[str]:
        return self.event_stream.get(case_id, [])

    def get_all_curr_hashes(self) -> Set[str]:
        hashes = set()
        for p in self.participants.values():
            for t in p.transitions:
                hashes.add(t.curr_hash)
        return hashes

    def get_all_prev_hashes(self) -> Set[str]:
        hashes = set()
        for p in self.participants.values():
            for t in p.transitions:
                hashes.add(t.prev_hash)
        return hashes

    def get_sink_nodes(self) -> Set[str]:
        all_curr = self.get_all_curr_hashes()
        all_prev = self.get_all_prev_hashes()
        return all_curr - all_prev

    def get_all_nodes(self) -> Set[str]:
        nodes = {START_HASH}
        nodes.update(self.get_all_curr_hashes())
        return nodes

    def compute_min_cost_with_alignment(self, target_hash: str, log_idx: int,
                                        events: List[str],
                                        caller_id: Optional[str] = None) -> Alignment:
        self.route_calls += 1
        if target_hash == START_HASH:
            return Alignment.from_log_moves(events, log_idx)

        owner = self.hash_owner.get(target_hash)
        if owner is None:
            return Alignment.from_log_moves(events, log_idx)

        if caller_id is not None and owner != caller_id:
            self.remote_calls += 1

        return self.participants[owner].min_cost_with_alignment(
            target_hash, log_idx, events, self)

    def compute_prefix_alignment(self, case_id: str) -> Alignment:
        events = self.get_events(case_id)

        for p in self.participants.values():
            p.clear_memo()

        log_idx = len(events) - 1
        all_nodes = self.get_all_nodes()

        best_align: Optional[Alignment] = None
        best_cost = float('inf')

        for node in all_nodes:
            align = self.compute_min_cost_with_alignment(node, log_idx, events)
            if align.cost < best_cost:
                best_cost = align.cost
                best_align = align

        return best_align


def build_network(sequences: List[List[str]],
                  participant_mapping: Dict[str, str]) -> Network:
    network = Network()

    for seq in sequences:
        prev = START_HASH
        for activity in seq:
            pid = participant_mapping[activity]
            if pid not in network.participants:
                network.register_participant(Participant(pid))
            curr = network.participants[pid].add_transition(prev, activity)
            if curr not in network.hash_owner:
                network.hash_owner[curr] = pid
            prev = curr

    return network


def load_training_data(splitter: EventLogSplitter, n: int, c: bool):
    training = splitter.get_training_data(n)

    sequences: List[List[str]] = []
    mapping: Dict[str, str] = {}

    for case_id in training.traces:
        trace = []
        occurrences: Dict[str, int] = {}
        for event in training.traces[case_id]:
            if event.activity not in occurrences:
                occurrences[event.activity] = 1
            else:
                occurrences[event.activity] += 1
            activity_str = f"{event.activity}-{event.location}{occurrences[event.activity]}"
            loc = "c" if c else event.location
            trace.append(activity_str)
            mapping[activity_str] = loc
        sequences.append(trace)

    return sequences, mapping


def load_validation_trace(splitter: EventLogSplitter, record_index: int, c: bool):
    test_data = splitter.get_test_data(record_index)

    for case_id in test_data.traces:
        trace = []
        occurrences: Dict[str, int] = {}
        for event in test_data.traces[case_id]:
            if event.activity not in occurrences:
                occurrences[event.activity] = 1
            else:
                occurrences[event.activity] += 1
            activity_str = f"{event.activity}-{event.location}{occurrences[event.activity]}"
            trace.append(activity_str)
        return trace

    return []


if __name__ == "__main__":
    splitter = EventLogSplitter("../gt/test/datasets/Sepsis.xes", location_key="org:group")
    total_cases = len(splitter.case_ids)

    training_sequences, mapping = load_training_data(splitter, 10, c=False)
    training_sequences_c, mapping_c = load_training_data(splitter, 10, c=True)
    network = build_network(training_sequences, mapping)
    network_c = build_network(training_sequences_c, mapping_c)

    print(f"Training traces: {len(training_sequences)}")
    print(f"Decentral participants: {len(network.participants)}")
    print(f"Central participants: {len(network_c.participants)}")
    print(f"Total cases: {total_cases}")
    print()

    first_fail = None

    total_route = 0
    total_remote = 0
    total_states = 0
    total_route_c = 0
    total_states_c = 0
    n_processed = 0

    for idx in range(total_cases):
        trace = load_validation_trace(splitter, idx, c=False)
        trace_c = load_validation_trace(splitter, idx, c=True)
        if len(trace) < 2:
            continue

        n_processed += 1
        case_id = f"case_{idx}"
        for event in trace:
            network.record_event(case_id, event)
        for event in trace_c:
            network_c.record_event(case_id, event)

        network.reset_stats()
        network_c.reset_stats()

        dec_align = network.compute_prefix_alignment(case_id)
        cen_align = network_c.compute_prefix_alignment(case_id)
        dec_cost = dec_align.cost
        cen_cost = cen_align.cost

        total_route += network.route_calls
        total_remote += network.remote_calls
        total_states += network.get_total_states()
        total_route_c += network_c.route_calls
        total_states_c += network_c.get_total_states()

        status = "OK" if dec_cost == cen_cost else "FAIL"
        sys.stdout.write(f"\r  [{idx:4d}/{total_cases}] cost={dec_cost:3d}/{cen_cost:3d}  events={len(trace):3d}  {status}")
        sys.stdout.flush()

        if dec_cost != cen_cost:
            first_fail = (idx, trace, trace_c, dec_cost, cen_cost, dec_align, cen_align)
            print("\n\nMISMATCH FOUND!")
            break

    print()

    if first_fail:
        idx, trace, trace_c, dec_cost, cen_cost, dec_align, cen_align = first_fail
        print(f"\nIndex: {idx}")
        print(f"Trace ({len(trace)} events):")
        for i, a in enumerate(trace):
            print(f"  {i}: {a}")
        print(f"\nCentralized trace ({len(trace_c)} events):")
        for i, a in enumerate(trace_c):
            print(f"  {i}: {a}")
        print(f"\nDecentralized cost: {dec_cost}")
        print(f"Centralized cost: {cen_cost}")
        print(f"\nDecentralized alignment:")
        for i, (m, l) in enumerate(dec_align.moves):
            print(f"  {i}: {m or '>>':40s} | {l or '>>'}")
        print(f"\nCentralized alignment:")
        for i, (m, l) in enumerate(cen_align.moves):
            print(f"  {i}: {m or '>>':40s} | {l or '>>'}")
    else:
        avg_route = total_route / n_processed
        avg_remote = total_remote / n_processed
        avg_states = total_states / n_processed
        avg_route_c = total_route_c / n_processed
        avg_states_c = total_states_c / n_processed
        sep = "=" * 70
        dash = "-" * 40
        dash2 = "-" * 12
        print(f"\n{sep}")
        print(f"  Results: {n_processed} traces, all matched!")
        print(f"{sep}")
        print(f"  {'Metric':<40s} {'Decentral':>12s} {'Central':>12s}")
        print(f"  {dash} {dash2} {dash2}")
        print(f"  {'Avg network lookups (route_calls)':<40s} {avg_route:>12.1f} {avg_route_c:>12.1f}")
        print(f"  {'Avg cross-participant calls (remote)':<40s} {avg_remote:>12.1f} {'N/A':>12s}")
        print(f"  {'Avg states explored (memo entries)':<40s} {avg_states:>12.1f} {avg_states_c:>12.1f}")
        print(f"  {'Total network lookups':<40s} {total_route:>12d} {total_route_c:>12d}")
        print(f"  {'Total cross-participant calls':<40s} {total_remote:>12d} {'N/A':>12s}")
        print(f"  {'Total states explored':<40s} {total_states:>12d} {total_states_c:>12d}")
        print(f"{sep}")
