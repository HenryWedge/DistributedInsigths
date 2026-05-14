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

Alignment = List[Tuple[Optional[str], Optional[str]]]


def compute_hash(prev_hash: str, activity: str) -> str:
    return hashlib.sha256((prev_hash + activity).encode()).hexdigest()


def alignment_entries_for_start(log_idx: int, events: List[str]) -> Alignment:
    return [(None, log) for log in events[:log_idx + 1]]


class Participant:
    def __init__(self, participant_id: str):
        self.id = participant_id
        self.transitions: List[Tuple[str, str, str]] = []
        self._memo: Dict[Tuple[str, int], Tuple[int, Alignment]] = {}

    def add_transition(self, prev_hash: str, activity: str) -> str:
        curr_hash = compute_hash(prev_hash, activity)
        self.transitions.append((prev_hash, activity, curr_hash))
        return curr_hash

    def clear_memo(self):
        self._memo.clear()

    def get_transitions_by_curr_hash(self, curr_hash: str) -> List[Tuple[str, str]]:
        return [(p, a) for p, a, c in self.transitions if c == curr_hash]

    def _min_cost(self, target_hash: str, log_idx: int,
                  events: List[str], network: 'Network') -> Tuple[int, Alignment]:
        if target_hash == START_HASH:
            return log_idx + 1, alignment_entries_for_start(log_idx, events)

        key = (target_hash, log_idx)
        if key in self._memo:
            return self._memo[key]

        local_transitions = self.get_transitions_by_curr_hash(target_hash)

        best_cost = float('inf')
        best_align: Alignment = []

        for prev_hash, activity in local_transitions:
            cost, align = network.route_min_cost(prev_hash, log_idx, events)
            cost += MODEL_COST
            if cost < best_cost:
                best_cost = cost
                best_align = align + [(activity, None)]

            if log_idx >= 0 and events[log_idx] == activity:
                cost, align = network.route_min_cost(prev_hash, log_idx - 1, events)
                if cost < best_cost:
                    best_cost = cost
                    best_align = align + [(activity, activity)]

        if log_idx >= 0:
            cost, align = network.route_min_cost(target_hash, log_idx - 1, events)
            cost += LOG_COST
            if cost < best_cost:
                best_cost = cost
                best_align = align + [(None, events[log_idx])]

        if best_cost == float('inf'):
            best_cost = log_idx + 1
            best_align = alignment_entries_for_start(log_idx, events)

        result = (int(best_cost), best_align)
        self._memo[key] = result
        return result

    def compute_prefix_alignment(self, events: List[str],
                                 network: 'Network') -> Tuple[int, Alignment]:
        all_nodes = {START_HASH}
        for p in network.participants.values():
            for _, _, c in p.transitions:
                all_nodes.add(c)

        log_idx = len(events) - 1

        best_cost = float('inf')
        best_align: Alignment = []

        for node in all_nodes:
            cost, align = network.route_min_cost(node, log_idx, events)
            if cost < best_cost:
                best_cost = cost
                best_align = align

        return int(best_cost), best_align


class Network:
    def __init__(self):
        self.event_stream: Dict[str, List[str]] = {}
        self.participants: Dict[str, Participant] = {}
        self.hash_owner: Dict[str, str] = {}

    def register_participant(self, participant: Participant):
        self.participants[participant.id] = participant
        for _, _, curr_hash in participant.transitions:
            self.hash_owner[curr_hash] = participant.id

    def store_event(self, case_id: str, activity: str):
        if case_id not in self.event_stream:
            self.event_stream[case_id] = []
        self.event_stream[case_id].append(activity)

    def get_events(self, case_id: str) -> List[str]:
        return self.event_stream.get(case_id, [])

    def route_min_cost(self, target_hash: str, log_idx: int,
                        events: List[str]) -> Tuple[int, Alignment]:
        if target_hash == START_HASH:
            return log_idx + 1, alignment_entries_for_start(log_idx, events)

        owner = self.hash_owner.get(target_hash)
        if owner is None:
            return log_idx + 1, alignment_entries_for_start(log_idx, events)

        return self.participants[owner]._min_cost(target_hash, log_idx, events, self)

    def record_event(self, case_id: str, activity: str, participant_id: str) -> Tuple[int, Alignment]:
        self.store_event(case_id, activity)
        events = self.get_events(case_id)

        for p in self.participants.values():
            p.clear_memo()

        participant = self.participants.get(participant_id)
        if participant is None:
            cost, align = self._compute_prefix_fallback(events)
        else:
            cost, align = participant.compute_prefix_alignment(events, self)

        print(f"[{participant_id}] Event: {activity} | Running cost: {cost}")
        return cost, align

    def _compute_prefix_fallback(self, events: List[str]) -> Tuple[int, Alignment]:
        all_nodes = {START_HASH}
        for p in self.participants.values():
            for _, _, c in p.transitions:
                all_nodes.add(c)
        log_idx = len(events) - 1

        best_cost = float('inf')
        best_align: Alignment = []
        for node in all_nodes:
            cost, align = self._route_min_cost(node, log_idx, events)
            if cost < best_cost:
                best_cost = cost
                best_align = align
        return int(best_cost), best_align


def compute_centralized_prefix_alignment(sequences: List[List[str]],
                                         trace: List[str]) -> Tuple[int, Alignment]:
    transitions: Dict[str, Tuple[str, str]] = {}
    all_nodes: Set[str] = {START_HASH}

    for seq in sequences:
        prev = START_HASH
        for activity in seq:
            curr = compute_hash(prev, activity)
            if curr not in transitions:
                transitions[curr] = (prev, activity)
            all_nodes.add(curr)
            prev = curr

    memo: Dict[Tuple[str, int], Tuple[int, Alignment]] = {}

    def min_cost(target_hash: str, log_idx: int) -> Tuple[int, Alignment]:
        if target_hash == START_HASH:
            return log_idx + 1, alignment_entries_for_start(log_idx, trace)

        key = (target_hash, log_idx)
        if key in memo:
            return memo[key]

        if target_hash not in transitions:
            return log_idx + 1, alignment_entries_for_start(log_idx, trace)

        prev_hash, activity = transitions[target_hash]

        best_cost = float('inf')
        best_align: Alignment = []

        cost, align = min_cost(prev_hash, log_idx)
        cost += MODEL_COST
        if cost < best_cost:
            best_cost = cost
            best_align = align + [(activity, None)]

        if log_idx >= 0 and trace[log_idx] == activity:
            cost, align = min_cost(prev_hash, log_idx - 1)
            if cost < best_cost:
                best_cost = cost
                best_align = align + [(activity, activity)]

        if log_idx >= 0:
            cost, align = min_cost(target_hash, log_idx - 1)
            cost += LOG_COST
            if cost < best_cost:
                best_cost = cost
                best_align = align + [(None, trace[log_idx])]

        if best_cost == float('inf'):
            best_cost = log_idx + 1
            best_align = alignment_entries_for_start(log_idx, trace)

        result = (int(best_cost), best_align)
        memo[key] = result
        return result

    log_idx = len(trace) - 1

    best_cost = float('inf')
    best_align: Alignment = []

    for node in all_nodes:
        cost, align = min_cost(node, log_idx)
        if cost < best_cost:
            best_cost = cost
            best_align = align

    return int(best_cost), best_align


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


if __name__ == "__main__":
    splitter = EventLogSplitter("../gt/test/datasets/Sepsis.xes", location_key="org:group")
    total_cases = len(splitter.case_ids)

    training_sequences, mapping = load_training_data(splitter, 10, c=False)
    network = build_network(training_sequences, mapping)

    print(f"Training traces: {len(training_sequences)}")
    print(f"Network participants: {len(network.participants)}")
    print()

    first_fail = None

    for idx in range(total_cases):
        trace = load_validation_trace(splitter, idx, c=False)
        if len(trace) < 2:
            continue

        dec_cost = 0
        for ei, event in enumerate(trace[:]):
            case_id = f"case_{idx}"
            pid = mapping.get(event, list(network.participants.keys())[0])
            dec_cost, dec_align = network.record_event(case_id, event, pid)

        cen_cost, cen_align = compute_centralized_prefix_alignment(training_sequences, trace)

        status = "OK" if dec_cost == cen_cost else "FAIL"
        sys.stdout.write(f"\r  [{idx:4d}/{total_cases}] cost={dec_cost:3d}/{cen_cost:3d}  events={len(trace):3d}  {status}")
        sys.stdout.flush()

        if dec_cost != cen_cost:
            first_fail = (idx, trace, dec_cost, cen_cost)
            print("\n\nMISMATCH FOUND!")
            break

    print()

    if first_fail:
        idx, trace, dec_cost, cen_cost = first_fail
        print(f"\nIndex: {idx}  Trace ({len(trace)} events)")
        for i, a in enumerate(trace):
            print(f"  {i}: {a}")
        print(f"Decentralized: {dec_cost}  Centralized: {cen_cost}")
    else:
        print(f"\nAll {total_cases} traces matched!")
