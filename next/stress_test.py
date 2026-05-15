#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import hashlib
from typing import Dict, List, Tuple, Optional

from algo.utility.event_log_splitter import EventLogSplitter

START = "START"
LOG_COST = 1
MODEL_COST = 1



class Event:
    def __init__(self, activity: str, case_id: str, location: str, timestamp):
        self.activity = activity
        self.case_id = case_id
        self.location = location
        self.timestamp = timestamp

    def __str__(self) -> str:
        return self.activity

class Entrypoint:
    def __init__(self, previous_entrypoint_hash: str, activity: str, participant_id: str):
        self.hash = self.compute_hash(previous_entrypoint_hash, activity)
        self.participant_id = participant_id

    def compute_hash(self, previous_entrypoint: 'Entrypoint', activity: str) -> str:
        if type(previous_entrypoint) == str:
            return hashlib.sha256(activity.encode()).hexdigest()
        return hashlib.sha256((previous_entrypoint.hash + activity).encode()).hexdigest()

class Transition:
    def __init__(self, prev_hash: str, activity: str, participant_id: str):
        self.prev_hash = prev_hash
        self.activity = activity
        self.entrypoint = Entrypoint(prev_hash, activity, participant_id)

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

    def __str__(self) -> str:
        lines = []
        for m, l in self._moves:
            left = m if m is not None else ">>"
            right = l if l is not None else ">>"
            lines.append(f"({left:20s}, {right})")
        return f"Alignment(cost={self.cost}, len={len(self._moves)})\n" + "\n".join(lines)

    def add_sync_move(self, activity: str) -> 'Alignment':
        return Alignment(self._moves + [(activity, activity)])

    def add_log_move(self, activity: str) -> 'Alignment':
        return Alignment(self._moves + [(None, activity)])

    def add_model_move(self, activity: str) -> 'Alignment':
        return Alignment(self._moves + [(activity, None)])


class Participant:
    def __init__(self, participant_id: str, network: 'Network'):
        self.id = participant_id
        self.transitions: List[Transition] = []
        self.cache: Dict[Tuple[str, int], Alignment] = {}
        self.decision_cache: Dict[Tuple[str, int], Tuple[int, int, str, int]] = {}
        self.network: 'Network' = network
        self.event_stream: Dict[str, List[str]] = {}
        self._case_log_activities: Dict[str, Dict[int, str]] = {}

    def _store_activity_at(self, case_id: str, log_index: int, activity: str):
        if case_id not in self._case_log_activities:
            self._case_log_activities[case_id] = {}
        self._case_log_activities[case_id][log_index] = activity

    def _get_activity_at(self, case_id: str, log_index: int) -> Optional[str]:
        return self._case_log_activities.get(case_id, {}).get(log_index)

    def receive_event(self, case_id: str, log_index: int, activity: str):
        if case_id not in self.event_stream:
            self.event_stream[case_id] = []
        self.event_stream[case_id].append(activity)
        self._store_activity_at(case_id, log_index, activity)

    def add_transition(self, entrypoint: str, activity: str, participant_id: str) -> str:
        transition = Transition(entrypoint, activity, participant_id)
        self.transitions.append(transition)
        return transition.entrypoint

    def get_transitions_by_entrypoint(self, entrypoint: str) -> List[Transition]:
        return [t for t in self.transitions if t.entrypoint == entrypoint]

    def request_predecessor_cost(
        self,
        entrypoint: str,
        log_index: int,
        case_id: str
    ) -> int:
        self.network.route_calls += 1
        if entrypoint == START:
            return LOG_COST * (log_index + 1)

        owner = self.network.entrypoint_participant_map.get(entrypoint)
        if owner is None:
            return LOG_COST * (log_index + 1)

        if owner != self.id:
            self.network.remote_calls += 1

        return self.network.get_participant(owner).calculate_cost(
            entrypoint, log_index, case_id
        )

    def calculate_cost(
        self,
        entrypoint: str,
        log_index: int,
        case_id: str
    ) -> int:
        if entrypoint == START:
            return LOG_COST * (log_index + 1)

        activity = self._get_activity_at(case_id, log_index)
        key = (entrypoint, log_index)
        if key in self.decision_cache:
            return self.decision_cache[key][0]

        local_transitions = self.get_transitions_by_entrypoint(entrypoint)
        local_events = self.event_stream.get(case_id, [])
        best_cost = 10**9
        best_decision = (best_cost, -1, "", log_index)

        for i, t in enumerate(local_transitions):
            pred_cost = self.request_predecessor_cost(t.prev_hash, log_index, case_id)
            cost = pred_cost + MODEL_COST
            if cost < best_cost:
                best_cost = cost
                best_decision = (cost, i, t.prev_hash, log_index)

            if activity is not None and activity in local_events and activity == t.activity:
                pred_cost = self.request_predecessor_cost(t.prev_hash, log_index - 1, case_id)
                cost = pred_cost
                if cost < best_cost:
                    best_cost = cost
                    best_decision = (cost, i, t.prev_hash, log_index - 1)

        if log_index >= 0:
            pred_cost = self.request_predecessor_cost(entrypoint, log_index - 1, case_id)
            cost = pred_cost + LOG_COST
            if cost < best_cost:
                best_cost = cost
                best_decision = (cost, -1, entrypoint, log_index - 1)

        self.decision_cache[key] = best_decision
        return best_cost

    def request_predecessor_alignment(
        self,
        entrypoint: str,
        log_index: int,
        case_id: str
    ) -> Alignment:
        self.network.route_calls += 1
        if entrypoint == START:
            return Alignment([(None, "?") for _ in range(log_index + 1)])

        owner = self.network.entrypoint_participant_map.get(entrypoint)
        if owner is None:
            return Alignment([(None, "?") for _ in range(log_index + 1)])

        if owner != self.id:
            self.network.remote_calls += 1

        return self.network.get_participant(owner).reconstruct_alignment(
            entrypoint, log_index, case_id
        )

    def reconstruct_alignment(
        self,
        entrypoint: str,
        log_index: int,
        case_id: str
    ) -> Alignment:
        if entrypoint == START:
            return Alignment([(None, "?") for _ in range(log_index + 1)])

        key = (entrypoint, log_index)
        if key in self.cache:
            return self.cache[key]

        if key not in self.decision_cache:
            self.calculate_cost(entrypoint, log_index, case_id)

        _, trans_idx, pred_hash, pred_log_index = self.decision_cache[key]

        if trans_idx == -1:
            activity = self._get_activity_at(case_id, log_index)
            log_activity = activity if activity is not None else "?"
            pred_align = self.request_predecessor_alignment(pred_hash, pred_log_index, case_id)
            align = pred_align.add_log_move(log_activity)
        else:
            t = self.get_transitions_by_entrypoint(entrypoint)[trans_idx]
            pred_align = self.request_predecessor_alignment(pred_hash, pred_log_index, case_id)
            if pred_log_index == log_index:
                align = pred_align.add_model_move(t.activity)
            else:
                align = pred_align.add_sync_move(t.activity)

        self.cache[key] = align
        return align

    def compute_best_cost(self, log_index: int, case_id: str) -> Tuple[int, Optional[str]]:
        best_cost = 10**9
        best_entrypoint = None
        for transition in self.transitions:
            cost = self.calculate_cost(transition.entrypoint, log_index, case_id)
            if cost < best_cost:
                best_cost = cost
                best_entrypoint = transition.entrypoint
        return best_cost, best_entrypoint

    def compute_best_alignment(self, log_index: int, case_id: str, entrypoint: Optional[str] = None) -> Alignment:
        if entrypoint is None:
            return Alignment([(None, "?") for _ in range(log_index + 1)])
        return self.reconstruct_alignment(entrypoint, log_index, case_id)

    def process_event(self, event: Event, log_index: int) -> Alignment:
        self.receive_event(event.case_id, log_index, event.activity)

        best_cost = 10**9
        best_pid = None
        best_entrypoint = None
        for participant in self.network.participants.values():
            cost, entrypoint = participant.compute_best_cost(log_index, event.case_id)
            if cost < best_cost:
                best_cost = cost
                best_pid = participant.id
                best_entrypoint = entrypoint

        if best_pid and best_entrypoint is not None:
            return self.network.participants[best_pid].compute_best_alignment(
                log_index, event.case_id, best_entrypoint
            )
        return Alignment([(None, "?") for _ in range(log_index + 1)])


class Network:
    def __init__(self):
        self.participants: Dict[str, Participant] = {}
        self.entrypoint_participant_map: Dict[str, str] = {}
        self.route_calls = 0
        self.remote_calls = 0

    def reset_stats(self):
        self.route_calls = 0
        self.remote_calls = 0

    def get_participant(self, participant_id: str) -> Participant | None:
        return self.participants.get(participant_id, None)

    def get_total_states(self) -> int:
        return sum(len(p.decision_cache) for p in self.participants.values())

    def register_participant(self, participant: Participant):
        self.participants[participant.id] = participant
        participant.network = self
        for transition in participant.transitions:
            self.entrypoint_participant_map[transition.entrypoint] = participant.id


class Executor:
    def __init__(self, network: Network, participant_mapping: Dict[str, str]):
        self.network = network
        self.participant_mapping = participant_mapping
        self.case_event_count: Dict[str, int] = {}

    def record_event(self, event: Event) -> Alignment:
        count = self.case_event_count.get(event.case_id, 0) + 1
        self.case_event_count[event.case_id] = count
        log_index = count - 1

        pid = self.participant_mapping.get(event.activity)
        participant = self.network.get_participant(pid)
        if participant is None:
            return Alignment([(None, "?") for _ in range(log_index + 1)])
        return participant.process_event(event, log_index)


def build_network(
    sequences: List[List[Event]],
    participant_mapping: Dict[str, str]
):
    network = Network()

    for seq in sequences:
        prev = Entrypoint("", START, None)
        for event in seq:
            participant_id = participant_mapping[event.activity]
            if participant_id not in network.participants:
                network.register_participant(Participant(participant_id, network))
            curr = network.participants[participant_id].add_transition(prev, event.activity, participant_id)
            if curr not in network.entrypoint_participant_map:
                network.entrypoint_participant_map[curr] = participant_id
            prev = curr

    executor = Executor(network, participant_mapping)
    return executor


def load_training_data(splitter: EventLogSplitter, n: int, c: bool):
    training = splitter.get_training_data(n)

    sequences: List[List[Event]] = []
    mapping: Dict[str, str] = {}

    for case_id in training.traces:
        trace: List[Event] = []
        occurrences: Dict[str, int] = {}
        for event in training.traces[case_id]:
            if event.activity not in occurrences:
                occurrences[event.activity] = 1
            else:
                occurrences[event.activity] += 1
            activity_str = f"{event.activity}-{event.location}{occurrences[event.activity]}"
            loc = "c" if c else event.location
            trace.append(Event(activity_str, case_id, loc, event.time))
            mapping[activity_str] = loc
        sequences.append(trace)

    return sequences, mapping


def load_validation_trace(splitter: EventLogSplitter, record_index: int, c: bool):
    test_data = splitter.get_test_data(record_index)

    for case_id in test_data.traces:
        trace: List[Event] = []
        occurrences: Dict[str, int] = {}
        for event in test_data.traces[case_id]:
            if event.activity not in occurrences:
                occurrences[event.activity] = 1
            else:
                occurrences[event.activity] += 1
            activity_str = f"{event.activity}-{event.location}{occurrences[event.activity]}"
            loc = "c" if c else event.location
            trace.append(Event(activity_str, case_id, loc, event.time))
        return trace

    return []


if __name__ == "__main__":
    splitter = EventLogSplitter("../gt/test/datasets/Sepsis.xes", location_key="org:group")
    total_cases = 100

    training_sequences, mapping = load_training_data(splitter, 10, c=False)
    training_sequences_c, mapping_c = load_training_data(splitter, 10, c=True)
    executor = build_network(training_sequences, mapping)
    executor_c = build_network(training_sequences_c, mapping_c)

    print(f"Training traces: {len(training_sequences)}")
    print(f"Decentral participants: {len(executor.network.participants)}")
    print(f"Central participants: {len(executor_c.network.participants)}")
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
        trace_events = load_validation_trace(splitter, idx, c=False)
        trace_events_c = load_validation_trace(splitter, idx, c=True)
        if len(trace_events) < 2:
            continue

        n_processed += 1
        case_id = f"case_{idx}"
        network = executor.network
        network_c = executor_c.network

        network.reset_stats()
        network_c.reset_stats()

        case_fail = None
        for ei in range(len(trace_events)):
            trace_events[ei].case_id = case_id
            trace_events_c[ei].case_id = case_id
            dec_align = executor.record_event(trace_events[ei])
            cen_align = executor_c.record_event(trace_events_c[ei])
            print("-" * 40)
            print(dec_align)
            print("-"*40)
            print(cen_align)
            print("-" * 40)
            if dec_align.cost != cen_align.cost:
                case_fail = (ei, dec_align, cen_align)
                break

        total_route += network.route_calls
        total_remote += network.remote_calls
        total_states += network.get_total_states()
        total_route_c += network_c.route_calls
        total_states_c += network_c.get_total_states()

        final_cost = dec_align.cost
        status = "OK" if case_fail is None else "FAIL"
        sys.stdout.write(f"\r  [{idx:4d}/{total_cases}] cost={final_cost:3d}  events={len(trace_events):3d}  {status}")
        sys.stdout.flush()

        if case_fail is not None:
            ei, dec_align, cen_align = case_fail
            first_fail = (idx, trace_events[:ei + 1], trace_events_c[:ei + 1], dec_align, cen_align)
            print("\n\nMISMATCH FOUND!")
            break

    print()

    if first_fail:
        idx, trace, trace_c, dec_align, cen_align = first_fail
        print(f"\nIndex: {idx}")
        print(f"Trace prefix ({len(trace)} events, up to failing event):")
        for i, a in enumerate(trace):
            print(f"  {i}: {a}")
        print(f"\nCentralized trace prefix ({len(trace_c)} events):")
        for i, a in enumerate(trace_c):
            print(f"  {i}: {a}")
        print(f"\nDecentralized cost: {dec_align.cost}")
        print(f"Centralized cost: {cen_align.cost}")
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
