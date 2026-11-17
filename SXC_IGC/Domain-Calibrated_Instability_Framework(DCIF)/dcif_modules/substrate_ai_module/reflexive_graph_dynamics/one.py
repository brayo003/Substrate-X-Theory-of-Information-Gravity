#!/usr/bin/env python3
"""
one.py — GI Task 9.2, revision 9: test-fixture and verdict-logic corrections.

Revision 8 is preserved unchanged except for two corrections:

  F8 (T02).  The first fixture in test_02_candidate_generation used
  `R = {(0,1)}`, `P = {{0,1}, {2,3}}` and expected the empty candidate
  set.  That expectation is wrong: the only edge is intra-block, so
  `S_g = ∅`, `B_out = ∅`, and both cross-block states 2 and 3 that are
  not in `S_R` are eligible.  The correct expectation is
  `{(0, 2), (0, 3)}`.  The rule `generate_candidates` is unchanged and
  correct; the fixture expectation was a test-code defect.

  F9 (verdict).  In `write_report`, the negative-behavioural-result
  branch required `D_final_graph_differs_from_CR == 0`.  Two different
  creation rules with the same count necessarily produce different
  graphs; that quantity is a tautology, not a behavioural observable.
  The branch now requires
  `D_final_partition_differs_from_CR == 0 and
   D_gate_reach_differs_from_CR == 0 and
   D_stored_reach_differs_from_CR == 0`,
  which are the three observables that actually decide whether the
  specific partition-conditioned placement rule contributes anything
  beyond rate-matched random placement.

No models, metrics, mechanisms, gates, or other tests are changed.

Status: this file has not been executed in the authoring environment.
Run `python3 one.py --test` first.
"""


from __future__ import annotations


import argparse
import csv
import hashlib
import json
import math
import os
import random
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, FrozenSet, Iterable, List, Optional, Sequence, Set, Tuple




# ===========================================================================
# 1.  Core data structures
# ===========================================================================


class Partition:
    """A partition of a fixed finite state set.  Block ids are internal
    bookkeeping; every reported observable is relabelling-invariant."""


    def __init__(self, states: Iterable[Any], blocks: Iterable[Iterable[Any]]):
        self._states: FrozenSet[Any] = frozenset(states)
        self._block_of: Dict[Any, int] = {}
        self._blocks: Dict[int, FrozenSet[Any]] = {}
        self._next_id: int = 0
        for raw in blocks:
            b = frozenset(raw)
            if not b:
                raise ValueError("empty block in partition")
            for s in b:
                if s not in self._states:
                    raise ValueError(f"state {s!r} in partition not in declared state set")
                if s in self._block_of:
                    raise ValueError(f"state {s!r} appears in two blocks")
                self._block_of[s] = self._next_id
            self._blocks[self._next_id] = b
            self._next_id += 1
        missing = self._states - set(self._block_of)
        if missing:
            raise ValueError(f"partition missing states {sorted(missing)}")


    def block_of(self, s: Any) -> int:
        return self._block_of[s]


    def block(self, bid: int) -> FrozenSet[Any]:
        return self._blocks[bid]


    def blocks(self) -> List[FrozenSet[Any]]:
        return [self._blocks[i] for i in sorted(self._blocks)]


    def num_blocks(self) -> int:
        return len(self._blocks)


    def states(self) -> FrozenSet[Any]:
        return self._states


    def equivalent(self, a: Any, b: Any) -> bool:
        return self._block_of[a] == self._block_of[b]


    def signature(self) -> Tuple[Tuple[Any, ...], ...]:
        return tuple(sorted(tuple(sorted(b)) for b in self._blocks.values()))


    def copy(self) -> "Partition":
        return Partition(self._states, self._blocks.values())




class TransitionGraph:
    def __init__(self, states: Iterable[Any]):
        self._states: FrozenSet[Any] = frozenset(states)
        self._succ: Dict[Any, Set[Any]] = {s: set() for s in self._states}
        self._pred: Dict[Any, Set[Any]] = {s: set() for s in self._states}


    def add_edge(self, a: Any, b: Any) -> None:
        if a not in self._states or b not in self._states:
            raise ValueError(f"edge ({a!r},{b!r}) references unknown state")
        self._succ[a].add(b)
        self._pred[b].add(a)


    def remove_edge(self, a: Any, b: Any) -> None:
        self._succ[a].discard(b)
        self._pred[b].discard(a)


    def successors(self, s: Any) -> FrozenSet[Any]:
        return frozenset(self._succ[s])


    def predecessors(self, s: Any) -> FrozenSet[Any]:
        return frozenset(self._pred[s])


    def has_edge(self, a: Any, b: Any) -> bool:
        return b in self._succ[a]


    def edges(self) -> Iterable[Tuple[Any, Any]]:
        for a in self._states:
            for b in self._succ[a]:
                yield (a, b)


    def edge_set(self) -> FrozenSet[Tuple[Any, Any]]:
        return frozenset(self.edges())


    def signature(self) -> Tuple[Tuple[Any, Any], ...]:
        return tuple(sorted(self.edges()))


    def states(self) -> FrozenSet[Any]:
        return self._states


    def out_degree(self, s: Any) -> int:
        return len(self._succ[s])


    def copy(self) -> "TransitionGraph":
        g = TransitionGraph(self._states)
        for a, b in self.edges():
            g.add_edge(a, b)
        return g


    def __len__(self) -> int:
        return sum(len(v) for v in self._succ.values())




# ===========================================================================
# 2.  Refinement, gate, consistency
# ===========================================================================


def successor_class_signature(a: Any, R: TransitionGraph, P: Partition) -> FrozenSet[int]:
    return frozenset(P.block_of(b) for b in R.successors(a))




def refine_once(R: TransitionGraph, P: Partition) -> Tuple[Partition, int]:
    new_blocks: List[List[Any]] = []
    num_splits = 0
    P_snap = P.copy()
    for bid in sorted(P_snap._blocks):
        members = list(P_snap._blocks[bid])
        groups: Dict[FrozenSet[int], List[Any]] = {}
        for s in members:
            sig = successor_class_signature(s, R, P_snap)
            groups.setdefault(sig, []).append(s)
        if len(groups) == 1:
            new_blocks.append(members)
        else:
            num_splits += len(groups) - 1
            new_blocks.extend(groups.values())
    return Partition(R.states(), new_blocks), num_splits




def gate_partition(R: TransitionGraph, P: Partition) -> TransitionGraph:
    g = TransitionGraph(R.states())
    for a, b in R.edges():
        if not P.equivalent(a, b):
            g.add_edge(a, b)
    return g




def gate_successors(z: Any, R: TransitionGraph, P: Partition) -> Set[Any]:
    return {b for b in R.successors(z) if not P.equivalent(z, b)}




def consistency_violations(R: TransitionGraph, P: Partition):
    sigs = {s: successor_class_signature(s, R, P) for s in R.states()}
    by_block: Dict[int, List[Any]] = defaultdict(list)
    for s in R.states():
        by_block[P.block_of(s)].append(s)
    out = []
    for members in by_block.values():
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                a, b = members[i], members[j]
                if sigs[a] != sigs[b]:
                    out.append((a, b, sigs[a], sigs[b]))
    return out




# ===========================================================================
# 3.  Instance generation
# ===========================================================================


def generate_instance(seed: int, n_states: int, edge_prob: float,
                      n_initial_blocks: int) -> Tuple[TransitionGraph, Partition]:
    rng = random.Random(init_stream_seed(seed))
    states = list(range(n_states))
    R = TransitionGraph(states)
    for a in states:
        for b in states:
            if rng.random() < edge_prob:
                R.add_edge(a, b)
    for a in states:
        if R.out_degree(a) == 0:
            R.add_edge(a, (a + 1) % n_states)
    shuffled = states[:]
    rng.shuffle(shuffled)
    blocks: List[List[int]] = [[] for _ in range(n_initial_blocks)]
    for i, s in enumerate(shuffled):
        blocks[i % n_initial_blocks].append(s)
    return R, Partition(states, blocks)




# ===========================================================================
# 4.  Candidate generation (primary model: uncapped)
# ===========================================================================


def generate_candidates(z: Any, R: TransitionGraph, P: Partition,
                        cap_per_source: Optional[int] = None) -> Set[Tuple[Any, Any]]:
    beta = P.block(P.block_of(z))
    S_R = R.successors(z)
    S_g = gate_successors(z, R, P)
    B_out = {P.block_of(b) for b in S_g}
    cands: Set[Tuple[Any, Any]] = set()
    for b in P.states():
        if b == z or b in beta or b in S_R or P.block_of(b) in B_out:
            continue
        cands.add((z, b))
    if cap_per_source is not None and len(cands) > cap_per_source:
        cands = set(sorted(cands, key=lambda e: e[1])[:cap_per_source])
    return cands




def creation_pool(R: TransitionGraph, P: Partition) -> List[Tuple[Any, Any]]:
    pool: List[Tuple[Any, Any]] = []
    for a in sorted(R.states()):
        for b in sorted(R.states()):
            if a == b or P.equivalent(a, b) or R.has_edge(a, b):
                continue
            pool.append((a, b))
    return pool




# ===========================================================================
# 5.  Common random numbers
# ===========================================================================


STREAM_DOMAIN_OFFSETS = {"init": 1, "move": 2, "ctrl": 3}




def stream_seed(seed: int, domain: str) -> int:
    if domain not in STREAM_DOMAIN_OFFSETS:
        raise ValueError(f"unknown stream domain: {domain}")
    return seed * 1_000_000 + STREAM_DOMAIN_OFFSETS[domain]




def init_stream_seed(seed: int) -> int:
    return stream_seed(seed, "init")




def move_stream_seed(seed: int) -> int:
    return stream_seed(seed, "move")




def cr_stream_seed(seed: int) -> int:
    return stream_seed(seed, "ctrl")




def pre_draw_uniforms(seed: int, steps: int) -> List[float]:
    rng = random.Random(move_stream_seed(seed))
    return [rng.random() for _ in range(steps)]




def select_successor(u: float, succ_sorted: Sequence[Any]) -> Optional[Any]:
    if not succ_sorted:
        return None
    n = len(succ_sorted)
    idx = min(int(u * n), n - 1)
    return succ_sorted[idx]




def apply_movement(u: float, succ_set: Set[Any], z: Any) -> Tuple[Any, bool]:
    succ = sorted(succ_set)
    selected = select_successor(u, succ)
    if selected is None:
        return z, False
    return selected, True




# ===========================================================================
# 6.  Step record and run result
# ===========================================================================


@dataclass
class StepRecord:
    t: int
    z_before: Any
    z_after: Any
    block_count: int
    partition_blocks: Tuple[Tuple[Any, ...], ...]
    graph_signature: Tuple[Tuple[Any, Any], ...]
    gate_edge_count: int
    admissible_edge_count: int
    created_edges_raw: int
    removed_edges_raw: int
    net_change: int
    consistency_violations: int
    splits_this_step: int
    traversed: bool
    stalled: bool
    created_set: Tuple[Tuple[Any, Any], ...] = ()
    removed_set: Tuple[Tuple[Any, Any], ...] = ()
    requested_create: int = 0
    creation_pool_size: int = 0
    ages_signature: Tuple[Tuple[Tuple[Any, Any], int], ...] = ()
    augmented_key: Tuple = ()
    candidates_pre_cap: int = 0
    candidates_post_cap: int = 0
    cap_saturated: bool = False
    unique_target_blocks: int = 0




@dataclass
class RunResult:
    model: str
    seed: int
    initial_partition: Optional[Partition] = None
    initial_graph: Optional[TransitionGraph] = None
    initial_blocks: Optional[int] = None
    initial_edges: Optional[int] = None
    initial_z: Any = None


    records: List[StepRecord] = field(default_factory=list)
    final_partition: Optional[Partition] = None
    final_graph: Optional[TransitionGraph] = None
    final_gate: Optional[TransitionGraph] = None


    partition_signatures: List[Tuple] = field(default_factory=list)
    graph_signatures: List[Tuple] = field(default_factory=list)


    partition_stable_at: Optional[int] = None
    graph_stable_at: Optional[int] = None
    combined_stable_at: Optional[int] = None


    trajectory_state_recurrence: bool = False
    configuration_recurrence: bool = False
    full_augmented_recurrence: bool = False


    created_ever_effective: int = 0
    created_affecting_refinement: int = 0
    created_total: int = 0




# ===========================================================================
# 7.  Shared measurement helpers
# ===========================================================================


def _serialize_partition(P: Partition) -> Tuple[Tuple[Any, ...], ...]:
    return tuple(tuple(sorted(b)) for b in P.blocks())




def _canonical_blocks(blocks: Iterable[Iterable[Any]]) -> Tuple[Tuple[Any, ...], ...]:
    """Canonicalise any sequence of blocks (list of lists, tuple of tuples,
    frozensets, ...) to a sorted tuple of sorted tuples, matching
    `Partition.signature()`."""
    return tuple(sorted(tuple(sorted(b)) for b in blocks))




def _stabilization_index_including_t0(signatures_with_t0: List[Any]) -> Optional[int]:
    if not signatures_with_t0:
        return None
    last_change = 0
    for i in range(1, len(signatures_with_t0)):
        if signatures_with_t0[i] != signatures_with_t0[i - 1]:
            last_change = i
    return last_change




def _trajectory_recurrence(z_list: List[Any]) -> bool:
    return len(set(z_list)) < len(z_list)




def _config_recurrence(sig_list: List[Tuple]) -> bool:
    return len(set(sig_list)) < len(sig_list)




def _full_recurrence(keys: List[Any]) -> bool:
    return len(set(keys)) < len(keys)




def _augmented_key(z: Any, P: Partition, R: TransitionGraph,
                   active_ages: Dict[Tuple[Any, Any], int], now: int,
                   removal_age: int) -> Tuple:
    ages = tuple(sorted((e, min(now - ts, removal_age))
                        for e, ts in active_ages.items()))
    return (z, P.signature(), R.signature(), ages)




def edge_affects_refinement(e: Tuple[Any, Any], R: TransitionGraph,
                            P: Partition) -> bool:
    a, b = e
    if P.equivalent(a, b):
        return False
    members = sorted(P.block(P.block_of(a)))
    if len(members) == 1:
        return False
    sig_with = {s: successor_class_signature(s, R, P) for s in members}
    succ_wo = R.successors(a) - {b}
    sig_wo_a = frozenset(P.block_of(x) for x in succ_wo)


    def grouping(sig_map: Dict[Any, FrozenSet[int]]):
        g: Dict[FrozenSet[int], List[Any]] = defaultdict(list)
        for s in members:
            g[sig_map[s]].append(s)
        return sorted(sorted(v) for v in g.values())


    sig_map_wo = dict(sig_with)
    sig_map_wo[a] = sig_wo_a
    return grouping(sig_with) != grouping(sig_map_wo)




def _finalize_run(rec: RunResult, z0: Any, P: Partition, R: TransitionGraph,
                  gate: TransitionGraph, created_all: Set[Tuple[Any, Any]],
                  ever_traversed: Set[Tuple[Any, Any]],
                  affecting: Set[Tuple[Any, Any]]) -> RunResult:
    rec.final_partition = P
    rec.final_graph = R
    rec.final_gate = gate
    rec.partition_stable_at = _stabilization_index_including_t0(rec.partition_signatures)
    rec.graph_stable_at = _stabilization_index_including_t0(rec.graph_signatures)
    combined = list(zip(rec.partition_signatures, rec.graph_signatures))
    rec.combined_stable_at = _stabilization_index_including_t0(combined)
    z_traj = [z0] + [r.z_after for r in rec.records]
    rec.trajectory_state_recurrence = _trajectory_recurrence(z_traj)
    configs = list(zip(z_traj, rec.partition_signatures, rec.graph_signatures))
    rec.configuration_recurrence = _config_recurrence(configs)
    rec.created_total = len(created_all)
    rec.created_ever_effective = len(created_all & ever_traversed)
    rec.created_affecting_refinement = len(affecting)
    return rec




# ===========================================================================
# 8.  Model runners
# ===========================================================================


def run_model_a(R_full, P0, z0, steps, uniforms, movement_seed_for_label=None):
    P = P0.copy()
    z = z0
    rec = RunResult("A", movement_seed_for_label or 0,
                    initial_partition=P0.copy(), initial_graph=R_full.copy(),
                    initial_blocks=P0.num_blocks(), initial_edges=len(R_full),
                    initial_z=z0)
    rec.partition_signatures = [P.signature()]
    rec.graph_signatures = [R_full.signature()]
    for t in range(steps):
        z_before = z
        z_after, traversed = apply_movement(uniforms[t], R_full.successors(z_before), z_before)
        gate = gate_partition(R_full, P)
        viol = len(consistency_violations(gate, P))
        rec.records.append(StepRecord(
            t=t, z_before=z_before, z_after=z_after,
            block_count=P.num_blocks(), partition_blocks=_serialize_partition(P),
            graph_signature=R_full.signature(), gate_edge_count=len(gate),
            admissible_edge_count=len(R_full),
            created_edges_raw=0, removed_edges_raw=0, net_change=0,
            consistency_violations=viol, splits_this_step=0,
            traversed=traversed, stalled=not traversed))
        rec.partition_signatures.append(P.signature())
        rec.graph_signatures.append(R_full.signature())
        z = z_after
    return _finalize_run(rec, z0, P, R_full.copy(), gate_partition(R_full, P),
                         set(), set(), set())




def run_model_b(R_full, P0, z0, steps, uniforms, movement_seed_for_label=None):
    P = P0.copy()
    z = z0
    rec = RunResult("B", movement_seed_for_label or 0,
                    initial_partition=P0.copy(), initial_graph=R_full.copy(),
                    initial_blocks=P0.num_blocks(), initial_edges=len(R_full),
                    initial_z=z0)
    rec.partition_signatures = [P.signature()]
    rec.graph_signatures = [R_full.signature()]
    for t in range(steps):
        z_before = z
        z_after, traversed = apply_movement(uniforms[t], R_full.successors(z_before), z_before)
        new_P, n_splits = refine_once(R_full, P)
        gate = gate_partition(R_full, new_P)
        viol = len(consistency_violations(gate, new_P))
        rec.records.append(StepRecord(
            t=t, z_before=z_before, z_after=z_after,
            block_count=new_P.num_blocks(), partition_blocks=_serialize_partition(new_P),
            graph_signature=R_full.signature(), gate_edge_count=len(gate),
            admissible_edge_count=len(R_full),
            created_edges_raw=0, removed_edges_raw=0, net_change=0,
            consistency_violations=viol, splits_this_step=n_splits,
            traversed=traversed, stalled=not traversed))
        P = new_P
        z = z_after
        rec.partition_signatures.append(P.signature())
        rec.graph_signatures.append(R_full.signature())
    return _finalize_run(rec, z0, P, R_full.copy(), gate_partition(R_full, P),
                         set(), set(), set())




def run_model_c(R_full, P0, z0, steps, uniforms, movement_seed_for_label=None):
    P = P0.copy()
    R = R_full
    z = z0
    rec = RunResult("C", movement_seed_for_label or 0,
                    initial_partition=P0.copy(), initial_graph=R_full.copy(),
                    initial_blocks=P0.num_blocks(), initial_edges=len(R_full),
                    initial_z=z0)
    rec.partition_signatures = [P.signature()]
    rec.graph_signatures = [R.signature()]
    for t in range(steps):
        z_before = z
        z_after, traversed = apply_movement(uniforms[t], gate_successors(z_before, R, P), z_before)
        gate = gate_partition(R, P)
        new_P, n_splits = refine_once(gate, P)
        new_gate = gate_partition(R, new_P)
        viol = len(consistency_violations(new_gate, new_P))
        rec.records.append(StepRecord(
            t=t, z_before=z_before, z_after=z_after,
            block_count=new_P.num_blocks(), partition_blocks=_serialize_partition(new_P),
            graph_signature=R.signature(), gate_edge_count=len(new_gate),
            admissible_edge_count=len(R),
            created_edges_raw=0, removed_edges_raw=0, net_change=0,
            consistency_violations=viol, splits_this_step=n_splits,
            traversed=traversed, stalled=not traversed))
        P = new_P
        z = z_after
        rec.partition_signatures.append(P.signature())
        rec.graph_signatures.append(R.signature())
    return _finalize_run(rec, z0, P, R.copy(), gate_partition(R, P),
                         set(), set(), set())




def run_model_d(R_full, P0, z0, steps, uniforms, movement_seed_for_label=None,
                cap_per_source: Optional[int] = None, removal_age: int = 5,
                index_hook: Optional[Callable[[int, List[Any]], int]] = None):
    if removal_age < 1:
        raise ValueError("removal_age must be >= 1")
    P = P0.copy()
    R = R_full.copy()
    R0_edges = R_full.edge_set()
    z = z0
    rec = RunResult("D", movement_seed_for_label or 0,
                    initial_partition=P0.copy(), initial_graph=R_full.copy(),
                    initial_blocks=P0.num_blocks(), initial_edges=len(R_full),
                    initial_z=z0)
    rec.partition_signatures = [P.signature()]
    rec.graph_signatures = [R.signature()]
    active_ages: Dict[Tuple[Any, Any], int] = {}
    created_all: Set[Tuple[Any, Any]] = set()
    ever_traversed: Set[Tuple[Any, Any]] = set()
    affecting: Set[Tuple[Any, Any]] = set()
    augmented_keys: List[Any] = [_augmented_key(z, P, R, active_ages, 0, removal_age)]


    for t in range(steps):
        s_g = gate_successors(z, R, P)
        if index_hook is not None:
            succ_sorted = sorted(s_g)
            if succ_sorted:
                z_after = succ_sorted[index_hook(t, succ_sorted)]
                traversed = True
            else:
                z_after = z
                traversed = False
        else:
            z_after, traversed = apply_movement(uniforms[t], s_g, z)
        if traversed:
            e_trav = (z, z_after)
            ever_traversed.add(e_trav)
            if e_trav not in R0_edges:
                active_ages[e_trav] = t
        gate = gate_partition(R, P)
        new_P, n_splits = refine_once(gate, P)
        pre_cap_set = generate_candidates(z, R, new_P, cap_per_source=None)
        pre_cap = len(pre_cap_set)
        if cap_per_source is None:
            cands = pre_cap_set
            post_cap = pre_cap
            cap_saturated = False
        else:
            cands = generate_candidates(z, R, new_P, cap_per_source=cap_per_source)
            post_cap = len(cands)
            cap_saturated = pre_cap > cap_per_source and post_cap == cap_per_source
        target_blocks = {new_P.block_of(b) for (_, b) in cands}
        created = {(a, b) for (a, b) in cands if not R.has_edge(a, b)}
        diag_pool_size = len(creation_pool(R, new_P))
        removed: Set[Tuple[Any, Any]] = set()
        for e in R.edge_set():
            if e in R0_edges:
                continue
            if e == (z, z_after):
                continue
            if e not in active_ages:
                raise RuntimeError(f"active dynamic edge {e} missing metadata (invariant violation)")
            if t - active_ages[e] >= removal_age:
                removed.add(e)
        new_R = R.copy()
        for e in created:
            new_R.add_edge(*e)
        for e in removed:
            new_R.remove_edge(*e)
        assert new_R.edge_set() == (R.edge_set() | created) - removed
        for e in removed:
            active_ages.pop(e, None)
        for e in created:
            active_ages[e] = t
        if traversed and (z, z_after) not in R0_edges:
            active_ages[(z, z_after)] = t
        created_all |= created
        for e in created:
            if e not in affecting and e in new_R.edge_set() and \
                    edge_affects_refinement(e, gate_partition(new_R, new_P), new_P):
                affecting.add(e)
        new_gate = gate_partition(new_R, new_P)
        viol = len(consistency_violations(new_gate, new_P))
        ages_sig = tuple(sorted((e, min((t + 1) - ts, removal_age))
                                for e, ts in active_ages.items()))
        akey = _augmented_key(z_after, new_P, new_R, active_ages, t + 1, removal_age)
        rec.records.append(StepRecord(
            t=t, z_before=z, z_after=z_after,
            block_count=new_P.num_blocks(), partition_blocks=_serialize_partition(new_P),
            graph_signature=new_R.signature(), gate_edge_count=len(new_gate),
            admissible_edge_count=len(new_R),
            created_edges_raw=len(created), removed_edges_raw=len(removed),
            net_change=len(new_R) - len(R),
            consistency_violations=viol, splits_this_step=n_splits,
            traversed=traversed, stalled=not traversed,
            created_set=tuple(sorted(created)), removed_set=tuple(sorted(removed)),
            requested_create=len(created), creation_pool_size=diag_pool_size,
            ages_signature=ages_sig, augmented_key=akey,
            candidates_pre_cap=pre_cap, candidates_post_cap=post_cap,
            cap_saturated=cap_saturated, unique_target_blocks=len(target_blocks)))
        P = new_P
        R = new_R
        z = z_after
        rec.partition_signatures.append(P.signature())
        rec.graph_signatures.append(R.signature())
        augmented_keys.append(akey)


    rec.full_augmented_recurrence = _full_recurrence(augmented_keys)
    return _finalize_run(rec, z0, P, R, gate, created_all, ever_traversed, affecting)




class ControlMatchingFailure(RuntimeError):
    pass




def run_control_random_matched(R_full, P0, z0, steps, uniforms,
                               movement_seed_for_label=None,
                               d_created_per_step: Optional[List[int]] = None,
                               removal_age: int = 5):
    if d_created_per_step is None:
        raise ValueError("CR control requires per-step creation counts from D")
    if removal_age < 1:
        raise ValueError("removal_age must be >= 1")
    cr_rng = random.Random(cr_stream_seed(movement_seed_for_label or 0))
    P = P0.copy()
    R = R_full.copy()
    R0_edges = R_full.edge_set()
    z = z0
    rec = RunResult("CR", movement_seed_for_label or 0,
                    initial_partition=P0.copy(), initial_graph=R_full.copy(),
                    initial_blocks=P0.num_blocks(), initial_edges=len(R_full),
                    initial_z=z0)
    rec.partition_signatures = [P.signature()]
    rec.graph_signatures = [R.signature()]
    active_ages: Dict[Tuple[Any, Any], int] = {}
    created_all: Set[Tuple[Any, Any]] = set()
    ever_traversed: Set[Tuple[Any, Any]] = set()
    affecting: Set[Tuple[Any, Any]] = set()
    augmented_keys: List[Any] = [_augmented_key(z, P, R, active_ages, 0, removal_age)]


    for t in range(steps):
        s_g = gate_successors(z, R, P)
        z_after, traversed = apply_movement(uniforms[t], s_g, z)
        if traversed:
            e_trav = (z, z_after)
            ever_traversed.add(e_trav)
            if e_trav not in R0_edges:
                active_ages[e_trav] = t
        gate = gate_partition(R, P)
        new_P, n_splits = refine_once(gate, P)


        n_create = int(d_created_per_step[t])
        pool = creation_pool(R, new_P)
        cr_own_cands = generate_candidates(z, R, new_P, cap_per_source=None)
        if len(pool) < len(cr_own_cands):
            raise RuntimeError("invariant violation: Pool_t smaller than "
                               "C^D on CR's own state (implementation bug)")
        if len(pool) < n_create:
            raise ControlMatchingFailure(
                f"seed={movement_seed_for_label} t={t}: creation pool too "
                f"small (requested {n_create}, available {len(pool)}); "
                f"seed excluded from matched statistics")
        created = set(cr_rng.sample(sorted(pool), n_create)) if n_create else set()


        removed: Set[Tuple[Any, Any]] = set()
        for e in R.edge_set():
            if e in R0_edges:
                continue
            if e == (z, z_after):
                continue
            if e not in active_ages:
                raise RuntimeError(f"active dynamic edge {e} missing metadata (invariant violation)")
            if t - active_ages[e] >= removal_age:
                removed.add(e)
        new_R = R.copy()
        for e in created:
            new_R.add_edge(*e)
        for e in removed:
            new_R.remove_edge(*e)
        assert new_R.edge_set() == (R.edge_set() | created) - removed


        for e in removed:
            active_ages.pop(e, None)
        for e in created:
            active_ages[e] = t
        if traversed and (z, z_after) not in R0_edges:
            active_ages[(z, z_after)] = t
        created_all |= created
        for e in created:
            if e not in affecting and e in new_R.edge_set() and \
                    edge_affects_refinement(e, gate_partition(new_R, new_P), new_P):
                affecting.add(e)
        new_gate = gate_partition(new_R, new_P)
        viol = len(consistency_violations(new_gate, new_P))
        ages_sig = tuple(sorted((e, min((t + 1) - ts, removal_age))
                                for e, ts in active_ages.items()))
        akey = _augmented_key(z_after, new_P, new_R, active_ages, t + 1, removal_age)
        rec.records.append(StepRecord(
            t=t, z_before=z, z_after=z_after,
            block_count=new_P.num_blocks(), partition_blocks=_serialize_partition(new_P),
            graph_signature=new_R.signature(), gate_edge_count=len(new_gate),
            admissible_edge_count=len(new_R),
            created_edges_raw=len(created), removed_edges_raw=len(removed),
            net_change=len(new_R) - len(R),
            consistency_violations=viol, splits_this_step=n_splits,
            traversed=traversed, stalled=not traversed,
            created_set=tuple(sorted(created)), removed_set=tuple(sorted(removed)),
            requested_create=n_create, creation_pool_size=len(pool),
            ages_signature=ages_sig, augmented_key=akey))
        P = new_P
        R = new_R
        z = z_after
        rec.partition_signatures.append(P.signature())
        rec.graph_signatures.append(R.signature())
        augmented_keys.append(akey)


    rec.full_augmented_recurrence = _full_recurrence(augmented_keys)
    return _finalize_run(rec, z0, P, R, gate_partition(R, P),
                         created_all, ever_traversed, affecting)




# ===========================================================================
# 9.  Reachability
# ===========================================================================


def reachable_from(g: TransitionGraph, s0: Any) -> Set[Any]:
    seen = {s0}
    stack = [s0]
    while stack:
        u = stack.pop()
        for v in g.successors(u):
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return seen




def replay_removals(R_full: TransitionGraph,
                    records: Sequence[StepRecord],
                    removal_age: int) -> List[Set[Tuple[Any, Any]]]:
    R0_edges = R_full.edge_set()
    Rcur = R_full.copy()
    ages: Dict[Tuple[Any, Any], int] = {}
    expected: List[Set[Tuple[Any, Any]]] = []
    for r in records:
        trav_edge = (r.z_before, r.z_after) if r.traversed else None
        if trav_edge is not None and trav_edge not in R0_edges:
            ages[trav_edge] = r.t
        exp: Set[Tuple[Any, Any]] = set()
        for e in Rcur.edge_set():
            if e in R0_edges or e == trav_edge:
                continue
            if e not in ages:
                raise TestFailure(
                    f"t={r.t}: replay lost age metadata for {e}")
            if r.t - ages[e] >= removal_age:
                exp.add(e)
        expected.append(exp)
        for e in r.created_set:
            Rcur.add_edge(*e)
        for e in r.removed_set:
            Rcur.remove_edge(*e)
        if Rcur.edge_set() != set(r.graph_signature):
            raise TestFailure(
                f"t={r.t}: replay graph diverges from recorded signature")
        for e in r.created_set:
            ages[e] = r.t
        for e in r.removed_set:
            ages.pop(e, None)
    return expected




# ===========================================================================
# 10.  Test inventory
# ===========================================================================


class TestFailure(AssertionError):
    pass




def _check(cond, msg):
    if not cond:
        raise TestFailure(msg)




def test_00_history_redundancy():
    """F1: canonical comparison on both sides."""
    for seed in (0, 1, 2):
        R, P0 = generate_instance(seed, 8, 0.3, 2)
        u = pre_draw_uniforms(seed + 100, 25)
        rec = run_model_d(R, P0, 0, 25, u, movement_seed_for_label=seed)
        R0 = R.edge_set()
        P = P0.copy()
        Rcur = R.copy()
        for r in rec.records:
            dyn = Rcur.edge_set() - R0
            for (a, b) in dyn:
                _check(not P.equivalent(a, b),
                       f"t={r.t}: dynamic edge ({a},{b}) not cross-block")
            for (a, b) in r.removed_set:
                _check((a, b) not in R0, f"t={r.t}: original edge removed")
            gate = gate_partition(Rcur, P)
            new_P, _ = refine_once(gate, P)
            new_R = Rcur.copy()
            for e in r.created_set:
                new_R.add_edge(*e)
            for e in r.removed_set:
                new_R.remove_edge(*e)
            _check(new_R.edge_set() == set(r.graph_signature),
                   f"t={r.t}: replay graph diverges from recorded signature")
            _check(_canonical_blocks(new_P.blocks()) ==
                   _canonical_blocks(r.partition_blocks),
                   f"t={r.t}: replay partition diverges from recorded blocks")
            P, Rcur = new_P, new_R




def test_01_partition_invariants():
    for seed in (0, 1, 2, 3):
        R, P0 = generate_instance(seed, 10, 0.3, 3)
        u = pre_draw_uniforms(seed + 200, 20)
        for runner in (run_model_b, run_model_c,
                       lambda *a, **k: run_model_d(*a, **k)):
            rec = runner(R, P0, 0, 20, u, movement_seed_for_label=seed)
            for r in rec.records:
                blocks = [set(b) for b in r.partition_blocks]
                flat = [s for b in blocks for s in b]
                _check(len(flat) == len(set(flat)), "overlapping blocks")
                _check(sorted(flat) == list(range(10)), "incomplete cover")
                _check(all(b for b in blocks), "empty block")
                _check(r.block_count == len(blocks), "block count mismatch")




def test_02_candidate_generation():
    """F8 (rev 9): the first fixture had the wrong expected value.
    With R = {(0,1)} and P = {{0,1}, {2,3}}, the only edge is intra-
    block, so S_g = empty, B_out = empty, and both cross-block states
    2 and 3 that are not in S_R = {1} are eligible.  The correct
    expectation is {(0, 2), (0, 3)}.  The rule is unchanged."""
    states = [0, 1, 2, 3]
    R = TransitionGraph(states)
    R.add_edge(0, 1)
    P = Partition(states, [[0, 1], [2, 3]])
    c = generate_candidates(0, R, P, cap_per_source=None)
    _check(c == {(0, 2), (0, 3)},
           f"expected {{(0,2),(0,3)}}, got {c}")
    # Fixture 2: 0 -> 2 is cross-block, so 2 is in S_g and 2's block
    # {2,3} is in B_out; only states in blocks not in B_out qualify,
    # but 0 and 1 are already in beta -> empty candidate set.
    R2 = TransitionGraph(states)
    R2.add_edge(0, 2)
    c2 = generate_candidates(0, R2, P, cap_per_source=None)
    _check(c2 == set(), f"expected empty, got {c2}")
    # Fixture 3: symmetric to fixture 2 with 3 in place of 2.
    R3 = TransitionGraph(states)
    R3.add_edge(0, 3)
    c3 = generate_candidates(0, R3, P, cap_per_source=None)
    _check(c3 == set(), f"expected empty, got {c3}")
    # Fixture 4: empty graph, both cross-block states eligible.
    R4 = TransitionGraph(states)
    c4 = generate_candidates(0, R4, P, cap_per_source=None)
    _check(c4 == {(0, 2), (0, 3)},
           f"expected {{(0,2),(0,3)}}, got {c4}")
    for (a, b) in c4:
        _check(not P.equivalent(a, b), "candidate not cross-block")
        _check(not R4.has_edge(a, b), "candidate already in R")
    c5 = generate_candidates(0, R4, P, cap_per_source=1)
    _check(len(c5) == 1 and c5 <= c4, "cap must keep a subset of size cap")




def test_03_removal_preserves_R0():
    for seed in (0, 1):
        R, P0 = generate_instance(seed, 10, 0.3, 2)
        R0 = R.edge_set()
        u = pre_draw_uniforms(seed + 300, 40)
        rec = run_model_d(R, P0, 0, 40, u, movement_seed_for_label=seed)
        for r in rec.records:
            for (a, b) in r.removed_set:
                _check((a, b) not in R0,
                       f"t={r.t}: original edge ({a},{b}) removed")
            sig = set(r.graph_signature)
            _check(R0 <= sig, f"t={r.t}: stored graph lost original edges")




def test_04_causal_chain_gate_based():
    states = [0, 1, 2, 3]
    R = TransitionGraph(states)
    R.add_edge(0, 2)
    P0 = Partition(states, [[0, 1], [2, 3]])
    u = [0.0]
    rec = run_model_d(R, P0, 0, 1, u, movement_seed_for_label=0)
    r0 = rec.records[0]
    _check(r0.splits_this_step >= 1, "expected refinement split")
    R2 = TransitionGraph(states)
    P2 = Partition(states, [[0, 1], [2, 3]])
    rec2 = run_model_d(R2, P2, 0, 1, [0.0], movement_seed_for_label=0)
    _check(rec2.records[0].created_edges_raw == 2,
           f"expected 2 creations from isolated z, got "
           f"{rec2.records[0].created_edges_raw}")
    _check(rec2.records[0].created_set == ((0, 2), (0, 3)),
           f"unexpected created set {rec2.records[0].created_set}")
    rec3 = run_model_d(R2, P2, 0, 2, [0.0, 0.0], movement_seed_for_label=0)
    _check(rec3.records[1].splits_this_step >= 1,
           "created edges must influence subsequent refinement")




def test_05_exact_edge_set_accounting():
    R, P0 = generate_instance(5, 8, 0.35, 2)
    u = pre_draw_uniforms(42, 30)
    rec = run_model_d(R, P0, 0, 30, u, movement_seed_for_label=5)
    prev = R.edge_set()
    for r in rec.records:
        cur = set(r.graph_signature)
        created, removed = set(r.created_set), set(r.removed_set)
        _check(cur == (prev | created) - removed,
               f"t={r.t}: edge-set accounting mismatch")
        _check(r.created_edges_raw == len(created)
               and r.removed_edges_raw == len(removed),
               f"t={r.t}: counter/edge-set mismatch")
        _check(not (created & removed), f"t={r.t}: simultaneous create+remove")
        _check(created & prev == set(), f"t={r.t}: created edge already present")
        prev = cur




def test_06_recurrence_definitions():
    R, P0 = generate_instance(6, 8, 0.3, 2)
    u = pre_draw_uniforms(9, 20)
    rec = run_model_d(R, P0, 0, 20, u, movement_seed_for_label=6)
    z_traj = [rec.initial_z] + [r.z_after for r in rec.records]
    _check(rec.trajectory_state_recurrence ==
           (len(set(z_traj)) < len(z_traj)), "trajectory recurrence mismatch")
    configs = list(zip(z_traj, rec.partition_signatures, rec.graph_signatures))
    _check(rec.configuration_recurrence ==
           (len(set(configs)) < len(configs)), "config recurrence mismatch")
    initial_key = (rec.initial_z,
                   rec.initial_partition.signature(),
                   rec.initial_graph.signature(),
                   ())
    full_keys = [initial_key] + [r.augmented_key for r in rec.records]
    _check(rec.full_augmented_recurrence ==
           (len(set(full_keys)) < len(full_keys)),
           "augmented recurrence mismatch (must include t=0 key)")
    dc = [r.created_edges_raw for r in rec.records]
    rcr = run_control_random_matched(R, P0, 0, 20, u, 6, dc, removal_age=5)
    initial_key_cr = (rcr.initial_z,
                      rcr.initial_partition.signature(),
                      rcr.initial_graph.signature(),
                      ())
    full_keys_cr = [initial_key_cr] + [r.augmented_key for r in rcr.records]
    _check(rcr.full_augmented_recurrence ==
           (len(set(full_keys_cr)) < len(full_keys_cr)),
           "CR augmented recurrence mismatch (must include t=0 key)")




def test_07_stabilization_indices():
    sigs = ["x", "x", "y", "y", "y"]
    _check(_stabilization_index_including_t0(sigs) == 2,
           "stabilization index must include t=0 and mark last change")
    sigs2 = ["x"] * 5
    _check(_stabilization_index_including_t0(sigs2) == 0,
           "constant sequence stabilizes at 0")




def test_08_model_separation_behavioural():
    states = [0, 1, 2, 3]
    R = TransitionGraph(states)
    R.add_edge(0, 1)
    R.add_edge(0, 2)
    R.add_edge(1, 3)
    R.add_edge(2, 3)
    P0 = Partition(states, [[0, 1], [2, 3]])
    u = pre_draw_uniforms(11, 10)
    rB = run_model_b(R, P0, 0, 10, u, movement_seed_for_label=11)
    rC = run_model_c(R, P0, 0, 10, u, movement_seed_for_label=11)
    _check(rB.partition_signatures != rC.partition_signatures,
           "B and C must be behaviourally distinguishable on this fixture")
    rA = run_model_a(R, P0, 0, 10, u, movement_seed_for_label=11)
    _check(all(r.block_count == 2 for r in rA.records),
           "A must never refine")




def test_09_crn_selection_correctness():
    S = [0, 1, 2]
    for u, expected in [(0.0, 0), (0.33, 0), (0.34, 1), (0.66, 1),
                        (0.67, 2), (0.999, 2), (1.0 - 1e-12, 2)]:
        got, trav = apply_movement(u, set(S), 99)
        _check(got == expected and trav, f"u={u}: got {got}, want {expected}")
    got, trav = apply_movement(0.5, set(), 99)
    _check(got == 99 and not trav, "empty successor set must stall")
    got, trav = apply_movement(0.0, {0}, 5)
    _check(got == 0 and trav, "successor 0 must be selectable (state-zero bug)")




def test_10_reproducibility():
    R, P0 = generate_instance(7, 10, 0.3, 3)
    u = pre_draw_uniforms(13, 25)
    kw = dict(movement_seed_for_label=7)


    def serialize(rec):
        return json.dumps({
            "partition_signatures": rec.partition_signatures,
            "graph_signatures": rec.graph_signatures,
            "records": [
                {f: getattr(r, f) for f in
                 ("t", "z_before", "z_after", "block_count",
                  "partition_blocks", "graph_signature", "created_set",
                  "removed_set", "created_edges_raw", "removed_edges_raw",
                  "ages_signature", "augmented_key", "requested_create",
                  "creation_pool_size")}
                for r in rec.records]},
            sort_keys=True, default=str)


    r1 = run_model_d(R, P0, 0, 25, u, **kw)
    r2 = run_model_d(R, P0, 0, 25, u, **kw)
    _check(serialize(r1) == serialize(r2), "D serialized results diverged")
    dc = [r.created_edges_raw for r in r1.records]
    c1 = run_control_random_matched(R, P0, 0, 25, u, 7, dc, removal_age=5)
    c2 = run_control_random_matched(R, P0, 0, 25, u, 7, dc, removal_age=5)
    _check(serialize(c1) == serialize(c2), "CR serialized results diverged")




def test_11_block_lookup_regression():
    P = Partition(range(6), [[0, 1], [2, 3], [4, 5]])
    _check(P.block_of(0) == 0 and P.block_of(3) == 1 and P.block_of(5) == 2,
           "block_of lookup wrong")
    _check(P.block(0) == frozenset({0, 1}), "block accessor wrong")
    _check(P.equivalent(0, 1) and not P.equivalent(1, 2), "equivalence wrong")
    try:
        Partition(range(4), [[0, 1], [1, 2], [3]])
        raise TestFailure("duplicate membership must raise")
    except ValueError:
        pass
    try:
        Partition(range(4), [[0, 1], [2]])
        raise TestFailure("incomplete cover must raise")
    except ValueError:
        pass




def test_12a_anonymity_index_coupling():
    R, P0 = generate_instance(3, 8, 0.35, 2)
    steps = 20
    u = pre_draw_uniforms(77, steps)
    perm = list(range(8))[::-1]
    base = run_model_d(R, P0, 0, steps, u, movement_seed_for_label=3)
    relab = run_model_d(
        _relabel_graph(R, perm), _relabel_partition(P0, perm), perm[0],
        steps, u, movement_seed_for_label=3,
        index_hook=lambda t, succ_sorted:
            succ_sorted.index(perm[base.records[t].z_after])
            if base.records[t].traversed else 0)
    for t in range(steps):
        _check(relab.records[t].z_after == perm[base.records[t].z_after],
               f"t={t}: index-coupled relabelled trajectory diverged")




def _relabel_graph(R: TransitionGraph, perm: Sequence[int]) -> TransitionGraph:
    g = TransitionGraph([perm[s] for s in R.states()])
    for (a, b) in R.edges():
        g.add_edge(perm[a], perm[b])
    return g




def _relabel_partition(P: Partition, perm: Sequence[int]) -> Partition:
    return Partition([perm[s] for s in P.states()],
                     [[perm[s] for s in b] for b in P.blocks()])




def test_12b_anonymity_distributional():
    states = [0, 1, 2, 3]
    R = TransitionGraph(states)
    R.add_edge(0, 1)
    R.add_edge(0, 2)
    P0 = Partition(states, [[0, 1], [2, 3]])
    perm = [2, 3, 0, 1]
    trials = 4000
    counts_base = {1: 0, 2: 0}
    counts_relab = {perm[1]: 0, perm[2]: 0}
    for k in range(trials):
        u = random.Random(1000 + k).random()
        z, _ = apply_movement(u, R.successors(0), 0)
        counts_base[z] += 1
        u2 = random.Random(5000 + k).random()
        z2, _ = apply_movement(u2, _relabel_graph(R, perm).successors(perm[0]), perm[0])
        counts_relab[z2] += 1
    for s in (1, 2):
        p_base = counts_base[s] / trials
        p_relab = counts_relab[perm[s]] / trials
        _check(abs(p_base - 0.5) < 0.05 and abs(p_relab - 0.5) < 0.05,
               f"successor {s}: base {p_base:.3f}, relabelled "
               f"{p_relab:.3f}; both must be ~0.5")




def test_12c_anonymity_implementation_consistency():
    import math as _math
    for n in (1, 2, 3, 5, 8):
        S = list(range(n))
        covered = set()
        for k in range(200):
            u = k / 200
            idx = min(int(_math.floor(u * n)), n - 1)
            covered.add(S[idx])
        _check(covered == set(S),
               f"n={n}: selection rule cannot reach every successor")




def test_13_state_zero_successor_regression():
    states = [0, 1]
    R = TransitionGraph(states)
    R.add_edge(1, 0)
    P0 = Partition(states, [[0], [1]])
    u = [0.0, 0.0, 0.0]
    rec = run_model_a(R, P0, 1, 3, u, movement_seed_for_label=0)
    _check([r.z_after for r in rec.records] == [0, 0, 0],
           "state 0 must be reachable as a successor (state-zero bug)")
    rec_c = run_model_c(R, P0, 1, 3, u, movement_seed_for_label=0)
    _check([r.z_after for r in rec_c.records] == [0, 0, 0],
           "state 0 must be reachable through the gate (model C)")




def test_14_exact_cr_matching():
    """F6: canonical comparison on both sides for the reconstructed
    post-refinement partition."""
    R, P0 = generate_instance(8, 10, 0.3, 3)
    steps = 30
    u = pre_draw_uniforms(21, steps)
    rD = run_model_d(R, P0, 0, steps, u, movement_seed_for_label=8)
    dc = [r.created_edges_raw for r in rD.records]
    rCR = run_control_random_matched(R, P0, 0, steps, u, 8, dc, removal_age=5)
    for t in range(steps):
        _check(rCR.records[t].created_edges_raw == rD.records[t].created_edges_raw,
               f"t={t}: creation count not matched exactly")
        _check(rCR.records[t].requested_create == rD.records[t].created_edges_raw,
               f"t={t}: requested count not recorded")
        _check(rCR.records[t].creation_pool_size >= rCR.records[t].created_edges_raw,
               f"t={t}: pool smaller than requested (invariant violation)")
        for (a, b) in rCR.records[t].created_set:
            _check(a != b, "self loop in CR creation")
    for name, rr in (("D", rD), ("CR", rCR)):
        expected = replay_removals(R, rr.records, removal_age=5)
        for k, r in enumerate(rr.records):
            _check(set(r.removed_set) == expected[k],
                   f"{name} t={k}: recorded removal set "
                   f"{sorted(r.removed_set)} != independently replayed "
                   f"predicate output {sorted(expected[k])}")


    Rcur = R.copy()
    Pcur = P0.copy()
    for t in range(steps):
        rec_t = rCR.records[t]
        gate_pre = gate_partition(Rcur, Pcur)
        P_post, _ = refine_once(gate_pre, Pcur)
        _check(_canonical_blocks(P_post.blocks()) ==
               _canonical_blocks(rec_t.partition_blocks),
               f"CR t={t}: reconstructed post-refinement partition "
               f"does not match recorded partition_blocks")
        pre_edges = Rcur.edge_set()
        for (a, b) in rec_t.created_set:
            _check((a, b) not in pre_edges,
                   f"CR t={t}: created edge ({a},{b}) was already present")
            _check(not P_post.equivalent(a, b),
                   f"CR t={t}: created edge ({a},{b}) not cross-block under "
                   f"post-refinement partition")
        for e in rec_t.created_set:
            Rcur.add_edge(*e)
        for e in rec_t.removed_set:
            Rcur.remove_edge(*e)
        _check(Rcur.edge_set() == set(rec_t.graph_signature),
               f"CR t={t}: reconstructed graph diverges from recorded "
               f"graph_signature")
        Pcur = P_post


def test_15_augmented_recurrence():
    states = [0, 1, 2, 3]
    R = TransitionGraph(states)
    P = Partition(states, [[0, 1], [2, 3]])
    ages_a = {(0, 2): 3}
    ages_b = {(0, 2): 4}
    k1 = _augmented_key(0, P, R, ages_a, 5, removal_age=5)
    k2 = _augmented_key(0, P, R, ages_b, 5, removal_age=5)
    _check(k1 != k2, "different bounded ages must yield different keys")
    k3 = _augmented_key(0, P, R, {(0, 2): 100}, 105, removal_age=5)
    k4 = _augmented_key(0, P, R, {(0, 2): 5}, 10, removal_age=5)
    _check(k3 == k4, "ages must be bounded by the removal threshold")
    k5 = _augmented_key(0, P, R, {}, 5, removal_age=5)
    _check(k5[:3] == (0, P.signature(), R.signature()), "key structure wrong")




def test_16_cli_validation():
    _check(_parse_args(["--test"]) is not None, "--test must parse")
    for bad in (["--seeds", "5", "--seed", "3"],
                ["--n", "0"], ["--steps", "0"], ["--n", "-3"],
                ["--edge-prob", "0"], ["--edge-prob", "1.5"],
                ["--initial-blocks", "99"],
                ["--removal-age", "0"],
                ["--single-run"]):
        try:
            _validate_args(_parse_args(bad))
            raise TestFailure(f"arguments {bad} must be rejected")
        except SystemExit:
            raise TestFailure(f"arguments {bad} must raise ValueError, not exit")
        except ValueError:
            pass




def test_17_all_records_diagnostics():
    """F7: recorded consistency violations must match an INDEPENDENT
    reconstruction of the gate from the recorded graph and partition at
    each timestep.  This is not a universal invariant across models;
    Model A can legitimately have nonzero violations."""
    R, P0 = generate_instance(9, 10, 0.3, 3)
    steps = 15
    u = pre_draw_uniforms(31, steps)
    for rec in (run_model_a(R, P0, 0, steps, u, 9),
                run_model_b(R, P0, 0, steps, u, 9),
                run_model_c(R, P0, 0, steps, u, 9),
                run_model_d(R, P0, 0, steps, u, 9)):
        _check(len(rec.records) == steps, "missing step records")
        _check(len(rec.partition_signatures) == steps + 1,
               "partition signatures must include t=0")
        _check(len(rec.graph_signatures) == steps + 1,
               "graph signatures must include t=0")
        for f in ("final_partition", "final_graph", "final_gate",
                  "partition_stable_at", "graph_stable_at",
                  "combined_stable_at"):
            _check(getattr(rec, f) is not None, f"{f} missing")
        for r in rec.records:
            P_step = Partition(range(10), r.partition_blocks)
            R_step = TransitionGraph(range(10))
            for edge in r.graph_signature:
                R_step.add_edge(*edge)
            expected = len(consistency_violations(gate_partition(R_step, P_step),
                                                  P_step))
            _check(r.consistency_violations == expected,
                   f"t={r.t}: recorded consistency diagnostic does not match "
                   f"independent reconstruction in {rec.model} "
                   f"(recorded {r.consistency_violations}, expected {expected})")
            _check(r.partition_blocks is not None and r.graph_signature is not None,
                   f"t={r.t}: missing trace")




def test_a1_distributional_equivariance_primary():
    states = [0, 1, 2, 3, 4]
    R = TransitionGraph(states)
    for b in (1, 2, 3, 4):
        R.add_edge(0, b)
    P0 = Partition(states, [[0, 1], [2], [3, 4]])
    perm = [4, 0, 3, 1, 2]
    trials = 6000
    base = {b: 0 for b in (1, 2, 3, 4)}
    relab = {perm[b]: 0 for b in (1, 2, 3, 4)}
    for k in range(trials):
        z, _ = apply_movement(random.Random(9000 + k).random(),
                              R.successors(0), 0)
        base[z] += 1
        z2, _ = apply_movement(random.Random(17000 + k).random(),
                               _relabel_graph(R, perm).successors(perm[0]), perm[0])
        relab[z2] += 1
    for b in (1, 2, 3, 4):
        pb, pr = base[b] / trials, relab[perm[b]] / trials
        _check(abs(pb - 0.25) < 0.04 and abs(pr - 0.25) < 0.04,
               f"successor {b}: base {pb:.3f}, relabelled {pr:.3f}; "
               f"both must be ~0.25")




def test_a2_cr_semantics_invariants():
    """F5: draw 5 movement variates for a 5-step run."""
    states = [0, 1, 2, 3]
    R = TransitionGraph(states)
    R.add_edge(0, 1); R.add_edge(0, 2); R.add_edge(0, 3)
    R.add_edge(1, 0); R.add_edge(2, 0); R.add_edge(3, 0)
    R.add_edge(1, 2); R.add_edge(2, 1); R.add_edge(1, 3); R.add_edge(3, 1)
    R.add_edge(2, 3); R.add_edge(3, 2)
    P0 = Partition(states, [[0], [1], [2], [3]])
    u_short = pre_draw_uniforms(3, 3)
    try:
        run_control_random_matched(R, P0, 0, 3, u_short, 0,
                                   d_created_per_step=[99, 0, 0],
                                   removal_age=5)
        raise TestFailure("shortfall must raise ControlMatchingFailure")
    except ControlMatchingFailure:
        pass
    u = pre_draw_uniforms(3, 5)
    random.seed(12345)
    r1 = run_model_d(R, P0, 0, 5, u, movement_seed_for_label=0)
    random.seed(999)
    r2 = run_model_d(R, P0, 0, 5, u, movement_seed_for_label=0)
    _check([r.removed_set for r in r1.records] ==
           [r.removed_set for r in r2.records],
           "D removal must be deterministic (independent of global RNG)")
    random.seed(12345)
    c1 = run_control_random_matched(R, P0, 0, 5, u, 0,
                                    [r.created_edges_raw for r in r1.records],
                                    removal_age=5)
    random.seed(999)
    c2 = run_control_random_matched(R, P0, 0, 5, u, 0,
                                    [r.created_edges_raw for r in r1.records],
                                    removal_age=5)
    _check([r.removed_set for r in c1.records] ==
           [r.removed_set for r in c2.records],
           "CR removal must be deterministic (independent of global RNG)")
    for name, rr in (("D", r1), ("CR", c1)):
        expected = replay_removals(R, rr.records, removal_age=5)
        for k, r in enumerate(rr.records):
            _check(set(r.removed_set) == expected[k],
                   f"A2 {name} t={k}: removal set != replayed predicate")




def test_a3_random_stream_separation():
    for s in (0, 1, 4, 12345):
        si, sm, sc = init_stream_seed(s), move_stream_seed(s), cr_stream_seed(s)
        _check(len({si, sm, sc}) == 3, f"seed {s}: stream seeds collide")
        _check(si != s and sm != s and sc != s,
               f"seed {s}: derived seed equals raw seed")
    for s1, s2 in ((0, 1), (4, 5), (10, 11)):
        for f in (init_stream_seed, move_stream_seed, cr_stream_seed):
            _check(f(s1) != f(s2), "stream seed derivation not injective")
    for s in (0, 1, 4):
        ri = random.Random(init_stream_seed(s))
        rm = random.Random(move_stream_seed(s))
        init_seq = [ri.random() for _ in range(50)]
        move_seq = [rm.random() for _ in range(50)]
        _check(init_seq != move_seq,
               f"seed {s}: U_init and U_move reproduce the same sequence")
    R, P0 = generate_instance(4, 8, 0.3, 2)
    steps = 20
    u = pre_draw_uniforms(4, steps)
    rm_check = random.Random(move_stream_seed(4))
    expected_u = [rm_check.random() for _ in range(steps)]
    _check(u == expected_u, "U_move must derive from move_stream_seed")
    rD = run_model_d(R, P0, 0, steps, u, movement_seed_for_label=4)
    dc = [r.created_edges_raw for r in rD.records]
    u_before = list(u)
    run_control_random_matched(R, P0, 0, steps, u, 4, dc, removal_age=5)
    _check(u == u_before, "CR draws must not mutate the movement stream")
    R2, P02 = generate_instance(4, 8, 0.3, 2)
    _check(R2.edge_set() == R.edge_set() and
           P02.signature() == P0.signature(),
           "initial generation must depend only on its own seed")
    _check(len(u) == steps, "one movement variate per timestep")




def test_a4_cr_cannot_shift_movement():
    R, P0 = generate_instance(6, 10, 0.3, 3)
    steps = 25
    u = pre_draw_uniforms(6, steps)
    rD1 = run_model_d(R, P0, 0, steps, u, movement_seed_for_label=6)
    dc = [r.created_edges_raw for r in rD1.records]
    u_snapshot = list(u)
    for k in range(3):
        run_control_random_matched(R, P0, 0, steps, u, 6, dc, removal_age=5)
    _check(u == u_snapshot, "CR activity altered the movement variates")
    rD2 = run_model_d(R, P0, 0, steps, u, movement_seed_for_label=6)
    _check([r.z_after for r in rD1.records] == [r.z_after for r in rD2.records],
           "D trajectory changed after CR activity")
    _check([r.created_set for r in rD1.records] ==
           [r.created_set for r in rD2.records],
           "D creation sets changed after CR activity")




def run_all_tests():
    tests = [
        ("T00_history_redundancy", test_00_history_redundancy),
        ("T01_partition_invariants", test_01_partition_invariants),
        ("T02_candidate_generation", test_02_candidate_generation),
        ("T03_removal_preserves_R0", test_03_removal_preserves_R0),
        ("T04_causal_chain_gate_based", test_04_causal_chain_gate_based),
        ("T05_exact_edge_set_accounting", test_05_exact_edge_set_accounting),
        ("T06_recurrence_definitions", test_06_recurrence_definitions),
        ("T07_stabilization_indices", test_07_stabilization_indices),
        ("T08_model_separation_behavioural", test_08_model_separation_behavioural),
        ("T09_crn_selection_correctness", test_09_crn_selection_correctness),
        ("T10_reproducibility", test_10_reproducibility),
        ("T11_block_lookup_regression", test_11_block_lookup_regression),
        ("T12a_anonymity_index_coupling", test_12a_anonymity_index_coupling),
        ("T12b_anonymity_distributional", test_12b_anonymity_distributional),
        ("T12c_anonymity_impl_consistency", test_12c_anonymity_implementation_consistency),
        ("T13_state_zero_successor_regression", test_13_state_zero_successor_regression),
        ("T14_exact_cr_matching", test_14_exact_cr_matching),
        ("T15_augmented_recurrence", test_15_augmented_recurrence),
        ("T16_cli_validation", test_16_cli_validation),
        ("T17_all_records_diagnostics", test_17_all_records_diagnostics),
        ("A1_distributional_equivariance_primary", test_a1_distributional_equivariance_primary),
        ("A2_cr_semantics_invariants", test_a2_cr_semantics_invariants),
        ("A3_random_stream_separation", test_a3_random_stream_separation),
        ("A4_cr_cannot_shift_movement", test_a4_cr_cannot_shift_movement),
    ]
    results = {}
    for name, fn in tests:
        try:
            fn()
            results[name] = "PASS"
            print(f"  {name}: PASS")
        except Exception as exc:
            results[name] = f"FAIL ({type(exc).__name__}: {exc})"
            print(f"  {name}: FAIL ({type(exc).__name__}: {exc})")
    n_pass = sum(1 for v in results.values() if v == "PASS")
    print(f"\n  {n_pass}/{len(tests)} tests passed")
    with open(os.path.join(OUT_DIR, "test_results.json"), "w") as f:
        json.dump(results, f, indent=2)
    return results




# ===========================================================================
# 11.  Diagnostic gates
# ===========================================================================


CRITICAL_GATES = {
    "A1_state_zero_regression",
    "E_partition_correctness_full",
    "H_metric_integrity_full",
    "I_reproducibility",
    "T14_exact_cr_matching",
}




def run_diagnostic_gates(per_seed, step_traces, graph_trace_rows, universe):
    gates = {}
    try:
        test_13_state_zero_successor_regression()
        gates["A1_state_zero_regression"] = True
    except Exception:
        gates["A1_state_zero_regression"] = False
    try:
        R, P0 = generate_instance(3, 8, 0.4, 2)
        u = pre_draw_uniforms(1, 20)
        rec = run_model_d(R, P0, 0, 20, u, movement_seed_for_label=1)
        init = len(rec.initial_graph)
        created = sum(r.created_edges_raw for r in rec.records)
        removed = sum(r.removed_edges_raw for r in rec.records)
        gates["B_insertion_consistency"] = (
            len(rec.final_graph) == init + created - removed)
    except Exception:
        gates["B_insertion_consistency"] = False
    try:
        test_03_removal_preserves_R0()
        gates["C_removal_preserves_R0"] = True
    except Exception:
        gates["C_removal_preserves_R0"] = False
    try:
        test_04_causal_chain_gate_based()
        gates["D_causal_influence"] = True
    except Exception:
        gates["D_causal_influence"] = False
    try:
        ok = True
        for row in per_seed:
            try:
                blocks = json.loads(row["final_partition"])
            except Exception:
                ok = False; break
            flat = []
            bad = False
            for b in blocks:
                if not isinstance(b, list) or not b:
                    bad = True; break
                for s in b:
                    if s not in universe:
                        bad = True; break
                    flat.append(s)
                if bad: break
            if bad:
                ok = False; break
            if len(flat) != len(set(flat)) or set(flat) != set(universe):
                ok = False; break
        gates["E_partition_correctness_full"] = ok
    except Exception:
        gates["E_partition_correctness_full"] = False
    try:
        test_08_model_separation_behavioural()
        gates["F_model_separation_behavioural"] = True
    except Exception:
        gates["F_model_separation_behavioural"] = False
    try:
        ok = True
        for row in per_seed:
            if row["model"] in ("D", "CR"):
                for k in ("trajectory_state_recurrence",
                          "configuration_recurrence",
                          "full_augmented_recurrence"):
                    if k not in row:
                        ok = False; break
        gates["G_recurrence_terminology"] = ok
    except Exception:
        gates["G_recurrence_terminology"] = False
    try:
        graphs = defaultdict(dict)
        for g in graph_trace_rows:
            if g["model"] in ("D", "CR"):
                graphs[(g["model"], g["seed"])][int(g["t"])] = {
                    tuple(e) for e in json.loads(g["graph_signature"])}
        changes = defaultdict(dict)
        for r in step_traces:
            if r["model"] in ("D", "CR"):
                changes[(r["model"], r["seed"])][int(r["t"])] = (
                    {tuple(e) for e in json.loads(r["created_set"])},
                    {tuple(e) for e in json.loads(r["removed_set"])})
        ok = bool(graphs) and graphs.keys() == changes.keys()
        if ok:
            for key in graphs:
                times = sorted(t for t in graphs[key] if t >= 0)
                if -1 not in graphs[key]:
                    ok = False; break
                prev = graphs[key][-1]
                for t in times:
                    created, removed = changes[key][t]
                    expected = (prev | created) - removed
                    if graphs[key][t] != expected:
                        ok = False; break
                    prev = graphs[key][t]
                if not ok: break
        gates["H_metric_integrity_full"] = ok
    except Exception:
        gates["H_metric_integrity_full"] = False
    try:
        tres = run_all_tests_silent()
        gates["I_reproducibility"] = tres.get("T10_reproducibility") == "PASS"
    except Exception:
        gates["I_reproducibility"] = False
    try:
        test_14_exact_cr_matching()
        gates["T14_exact_cr_matching"] = True
    except Exception:
        gates["T14_exact_cr_matching"] = False
    return gates




def run_all_tests_silent():
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        return run_all_tests()




# ===========================================================================
# 12.  Experiment driver
# ===========================================================================


DEFAULT_CONFIG = dict(
    N_STATES=12, EDGE_PROBABILITY=0.25, INITIAL_BLOCKS=3,
    STEPS=100, SEEDS=list(range(100)),
)


PRNG_PROTOCOL = (
    "MT19937 via random.Random (CPython).  Three domain-separated streams "
    "per experimental seed s: U_init = Random(s*1000000 + 1); U_move = "
    "Random(s*1000000 + 2), pre-drawn one uniform per (s, t), shared by "
    "A/B/C/D/CR; U_ctrl = Random(s*1000000 + 3), CR-only.  Streams are "
    "distinct by construction; independence is NOT claimed.")




def _provenance() -> Dict[str, Any]:
    import platform
    prov: Dict[str, Any] = {
        "python_version": platform.python_version(),
        "python_full_version": platform.python_version_tuple(),
        "python_executable": sys.executable,
        "python_build": sys.version.replace("\n", " "),
        "platform": platform.platform(),
        "prng_protocol": PRNG_PROTOCOL,
    }
    try:
        with open(__file__, "rb") as f:
            src = f.read()
        prov["source_md5"] = hashlib.md5(src).hexdigest()
        prov["source_sha256"] = hashlib.sha256(src).hexdigest()
        prov["source_bytes"] = len(src)
    except OSError:
        prov["source_md5"] = None
        prov["source_sha256"] = None
        prov["source_bytes"] = None
    return prov




def _result_row(r: RunResult) -> Dict[str, Any]:
    z_traj = [r.initial_z] + [rec.z_after for rec in r.records]
    return dict(
        model=r.model, seed=r.seed,
        initial_blocks=r.initial_blocks,
        initial_edges=r.initial_edges,
        initial_z=r.initial_z,
        final_blocks=(r.final_partition.num_blocks() if r.final_partition else None),
        final_edges=(len(r.final_graph) if r.final_graph else None),
        final_gate_edges=(len(r.final_gate) if r.final_gate else None),
        total_splits=sum(rec.splits_this_step for rec in r.records),
        n_refinement_events=sum(1 for rec in r.records if rec.splits_this_step > 0),
        total_created_raw=sum(rec.created_edges_raw for rec in r.records),
        total_removed_raw=sum(rec.removed_edges_raw for rec in r.records),
        n_traversed=sum(1 for rec in r.records if rec.traversed),
        n_stalls=sum(1 for rec in r.records if rec.stalled),
        consistency_violation_sum=sum(rec.consistency_violations for rec in r.records),
        partition_stable_at=r.partition_stable_at,
        graph_stable_at=r.graph_stable_at,
        combined_stable_at=r.combined_stable_at,
        trajectory_state_recurrence=r.trajectory_state_recurrence,
        configuration_recurrence=r.configuration_recurrence,
        full_augmented_recurrence=r.full_augmented_recurrence,
        distinct_states=len(set(z_traj)),
        created_total=r.created_total,
        created_ever_effective=r.created_ever_effective,
        created_affecting_refinement=r.created_affecting_refinement,
        n_cap_saturated=sum(1 for rec in r.records if rec.cap_saturated),
        mean_candidates_pre_cap=(sum(rec.candidates_pre_cap for rec in r.records)
                                 / len(r.records) if r.records else None),
        final_partition=json.dumps(
            [list(b) for b in (r.final_partition.blocks() if r.final_partition else [])]),
        final_edges_json=json.dumps(
            sorted(r.final_graph.edges()) if r.final_graph else []),
        final_gate_edges_json=json.dumps(
            sorted(r.final_gate.edges()) if r.final_gate else []),
        trajectory=json.dumps(z_traj),
    )




def _stats(vals):
    if not vals:
        return {}
    m = sum(vals) / len(vals)
    s = sorted(vals)
    med = s[len(s)//2] if len(s) % 2 else 0.5*(s[len(s)//2-1]+s[len(s)//2])
    var = sum((x-m)**2 for x in vals) / len(vals)
    return dict(mean=m, median=med, std=math.sqrt(var),
                min=s[0], max=s[-1], n=len(vals))




def _paired_differences(per_seed, model_x, model_y, metrics):
    by = defaultdict(dict)
    for r in per_seed:
        by[r["model"]][r["seed"]] = r
    out = []
    for metric in metrics:
        diffs = []
        for seed in sorted(set(by[model_x]) & set(by[model_y])):
            vx, vy = by[model_x][seed].get(metric), by[model_y][seed].get(metric)
            if vx is None or vy is None:
                continue
            diffs.append(float(vx) - float(vy))
        st = _stats(diffs)
        if st:
            out.append(dict(metric=metric, pair=f"{model_x}-{model_y}", **st))
    return out




def run_full(n_states, edge_prob, n_initial_blocks, steps, seeds,
             cap_per_source=None, removal_age=5, out_subdir=None):
    global OUT_DIR
    saved_dir = OUT_DIR
    if out_subdir:
        OUT_DIR = os.path.join(saved_dir, out_subdir)
        os.makedirs(OUT_DIR, exist_ok=True)
    try:
        per_seed, step_rows, partition_rows, graph_trace_rows, final_graph_rows = \
            [], [], [], [], []
        divergence = {
            "n_seeds": 0,
            "n_seeds_excluded_control_infeasible": 0,
            "D_creates_edges": 0,
            "D_removes_edges": 0,
            "D_final_partition_differs_from_C": 0,
            "D_final_graph_differs_from_C": 0,
            "D_final_graph_differs_from_CR": 0,
            "D_stored_reach_differs_from_C": 0,
            "D_gate_reach_differs_from_C": 0,
            "D_final_partition_differs_from_CR": 0,
            "D_stored_reach_differs_from_CR": 0,
            "D_gate_reach_differs_from_CR": 0,
            "D_trajectory_differs_from_C": 0,
            "D_trajectory_differs_from_CR": 0,
            "D_combined_stable_count": 0,
            "D_full_augmented_recurrence": 0,
            "D_configuration_recurrence": 0,
            "D_trajectory_state_recurrence": 0,
        }
        for seed in seeds:
            R, P0 = generate_instance(seed, n_states, edge_prob, n_initial_blocks)
            z0 = seed % n_states
            uniforms = pre_draw_uniforms(seed, steps)
            rA = run_model_a(R, P0, z0, steps, uniforms, seed)
            rB = run_model_b(R, P0, z0, steps, uniforms, seed)
            rC = run_model_c(R, P0, z0, steps, uniforms, seed)
            rD = run_model_d(R, P0, z0, steps, uniforms, seed,
                             cap_per_source=cap_per_source,
                             removal_age=removal_age)
            d_created = [rec.created_edges_raw for rec in rD.records]
            try:
                rCR = run_control_random_matched(
                    R, P0, z0, steps, uniforms, seed,
                    d_created_per_step=d_created, removal_age=removal_age)
            except ControlMatchingFailure as exc:
                divergence["n_seeds_excluded_control_infeasible"] += 1
                print(f"  [seed {seed}] control infeasible: {exc}")
                rCR = None
            runs = [rA, rB, rC, rD] + ([rCR] if rCR is not None else [])
            for r in runs:
                per_seed.append(_result_row(r))
                graph_trace_rows.append(dict(
                    model=r.model, seed=r.seed, t=-1,
                    graph_signature=json.dumps(
                        [list(e) for e in r.initial_graph.edge_set()])))
                for s in r.records:
                    step_rows.append(dict(
                        model=r.model, seed=r.seed, t=s.t,
                        z_before=s.z_before, z_after=s.z_after,
                        block_count=s.block_count,
                        gate_edge_count=s.gate_edge_count,
                        admissible_edge_count=s.admissible_edge_count,
                        created_raw=s.created_edges_raw,
                        removed_raw=s.removed_edges_raw,
                        net_change=s.net_change,
                        consistency_violations=s.consistency_violations,
                        splits=s.splits_this_step,
                        traversed=int(s.traversed), stalled=int(s.stalled),
                        requested_create=s.requested_create,
                        creation_pool_size=s.creation_pool_size,
                        candidates_pre_cap=s.candidates_pre_cap,
                        candidates_post_cap=s.candidates_post_cap,
                        cap_saturated=int(s.cap_saturated),
                        unique_target_blocks=s.unique_target_blocks,
                        created_set=json.dumps([list(e) for e in s.created_set]),
                        removed_set=json.dumps([list(e) for e in s.removed_set])))
                    partition_rows.append(dict(
                        model=r.model, seed=r.seed, t=s.t,
                        partition=json.dumps([list(b) for b in s.partition_blocks])))
                    graph_trace_rows.append(dict(
                        model=r.model, seed=r.seed, t=s.t,
                        graph_signature=json.dumps([list(e) for e in s.graph_signature])))
                final_graph_rows.append(dict(
                    model=r.model, seed=r.seed,
                    final_edges=sorted(r.final_graph.edges()) if r.final_graph else []))
            divergence["n_seeds"] += 1
            if sum(r.created_edges_raw for r in rD.records) > 0:
                divergence["D_creates_edges"] += 1
            if sum(r.removed_edges_raw for r in rD.records) > 0:
                divergence["D_removes_edges"] += 1
            if rC.final_partition.signature() != rD.final_partition.signature():
                divergence["D_final_partition_differs_from_C"] += 1
            if rC.final_graph.edge_set() != rD.final_graph.edge_set():
                divergence["D_final_graph_differs_from_C"] += 1
            if rC and rD:
                tC = [rec.z_after for rec in rC.records]
                tD = [rec.z_after for rec in rD.records]
                if tC != tD:
                    divergence["D_trajectory_differs_from_C"] += 1
            if rCR is not None:
                if rCR.final_graph.edge_set() != rD.final_graph.edge_set():
                    divergence["D_final_graph_differs_from_CR"] += 1
                if rCR.final_partition.signature() != rD.final_partition.signature():
                    divergence["D_final_partition_differs_from_CR"] += 1
                if [rec.z_after for rec in rCR.records] != \
                        [rec.z_after for rec in rD.records]:
                    divergence["D_trajectory_differs_from_CR"] += 1
                c_gate = reachable_from(rCR.final_gate, z0)
                d_gate = reachable_from(rD.final_gate, z0)
                if c_gate != d_gate:
                    divergence["D_gate_reach_differs_from_CR"] += 1
                c_stored_cr = reachable_from(rCR.final_graph, z0)
                d_stored_cr = reachable_from(rD.final_graph, z0)
                if c_stored_cr != d_stored_cr:
                    divergence["D_stored_reach_differs_from_CR"] += 1
            c_stored = reachable_from(rC.final_graph, z0)
            d_stored = reachable_from(rD.final_graph, z0)
            if c_stored != d_stored:
                divergence["D_stored_reach_differs_from_C"] += 1
            c_gate = reachable_from(rC.final_gate, z0)
            d_gate = reachable_from(rD.final_gate, z0)
            if c_gate != d_gate:
                divergence["D_gate_reach_differs_from_C"] += 1
            if rD.combined_stable_at is not None:
                divergence["D_combined_stable_count"] += 1
            if rD.full_augmented_recurrence:
                divergence["D_full_augmented_recurrence"] += 1
            if rD.configuration_recurrence:
                divergence["D_configuration_recurrence"] += 1
            if rD.trajectory_state_recurrence:
                divergence["D_trajectory_state_recurrence"] += 1


        summary_rows = []
        metrics = ["final_blocks", "final_edges", "final_gate_edges",
                   "total_created_raw", "total_removed_raw",
                   "partition_stable_at", "graph_stable_at", "combined_stable_at",
                   "distinct_states", "created_ever_effective",
                   "created_affecting_refinement", "n_cap_saturated"]
        for model in ("A", "B", "C", "D", "CR"):
            rows = [r for r in per_seed if r["model"] == model]
            for metric in metrics:
                vals = [float(r[metric]) for r in rows if r.get(metric) is not None]
                for sn, v in _stats(vals).items():
                    summary_rows.append(dict(model=model, metric=metric,
                                             stat=sn, value=v))
        paired = (_paired_differences(per_seed, "D", "C", metrics) +
                  _paired_differences(per_seed, "D", "CR", metrics))


        _write_csv("per_seed_results.csv", per_seed)
        _write_csv("step_traces.csv", step_rows)
        _write_csv("partition_traces.csv", partition_rows)
        _write_csv("graph_trace.csv", graph_trace_rows)
        _write_csv("final_graphs.csv", final_graph_rows)
        _write_csv("summary.csv", summary_rows)
        _write_csv("paired_differences.csv", paired)
        with open(os.path.join(OUT_DIR, "configuration.json"), "w") as f:
            json.dump(dict(
                n_states=n_states, edge_probability=edge_prob,
                initial_blocks=n_initial_blocks, steps=steps,
                seeds=list(seeds), cap_per_source=cap_per_source,
                removal_age=removal_age,
                provenance=_provenance(),
                stream_seeds={str(s): {
                    "init": init_stream_seed(s),
                    "move": move_stream_seed(s),
                    "ctrl": cr_stream_seed(s)} for s in seeds},
                divergence=divergence),
                f, indent=2, default=str)
        return dict(per_seed=per_seed, step_traces=step_rows,
                    summary=summary_rows, paired=paired,
                    graph_trace_rows=graph_trace_rows,
                    divergence=divergence)
    finally:
        OUT_DIR = saved_dir




# ===========================================================================
# 13.  Report generation
# ===========================================================================


def _mean_of(rows, metric, model):
    vals = []
    for r in rows:
        if r["model"] != model:
            continue
        v = r.get(metric, "")
        if v is None or v == "":
            continue
        try:
            vals.append(float(v))
        except (TypeError, ValueError):
            pass
    return (sum(vals)/len(vals)) if vals else None




def write_report(config, divergence, per_seed, paired, gates):
    lines = []
    a = lines.append
    failed_critical = [g for g in CRITICAL_GATES if not gates.get(g, False)]
    any_critical_fail = bool(failed_critical)
    a("# GI Task 9.2 — Phase 2 report (v2 specification)")
    a("")
    a("## 0. Diagnostic gates")
    a("")
    a("| gate | critical | result |")
    a("|---|---|---|")
    for name in sorted(gates):
        a(f"| {name} | {'yes' if name in CRITICAL_GATES else 'no'} "
          f"| {'PASS' if gates[name] else '**FAIL**'} |")
    a("")
    if any_critical_fail:
        a("**CRITICAL GATE FAILURE(S):** " + ", ".join(sorted(failed_critical)))
        a("")
        a("No positive verdict is asserted.")
        a("")
    a("## A. Executive summary")
    a("")
    if any_critical_fail:
        a("**Cannot assert a result** — critical diagnostic gates failed.")
    else:
        a("All critical gates passed under CPython execution.")
    a("")
    a("## B. Mathematical definitions (v2)")
    a("")
    a("- State: S_t = (z_t, P_t, R_t, A_t) on a fixed Omega; R_0 immutable.")
    a("- Gate: R_t^g = { (a,b) in R_t : a !~_{P_t} b }; local form: "
      "S_g(z) = { b in R.successors(z) : z !~_P b }.")
    a("- Movement: z_{t+1} = sorted(S_g(z_t))[min(floor(u_t*|S|), |S|-1)]; "
      "stall only when S_g(z_t) is empty.  Uniformity for an ideal "
      "continuous U is exact and independent of ordering; on CPython's "
      "finite-precision arithmetic the selection rule is an approximate "
      "realisation and no numerical bound is claimed.")
    a("- Refinement: exactly one round per step, P_{t+1} = RefineOnce(R_t^g, P_t).")
    a("- Candidates (uncapped primary model): "
      "C_t = { (z_t,b) : b != z_t, b notin beta(z_t), b notin S_R(z_t), "
      "P_{t+1}(b) notin B_out(z_t) } computed from z_t, R_t, P_{t+1}.")
    a("- Removal: DETERMINISTIC inactivity threshold L in BOTH D and CR.")
    a("- CR control: identical to D in movement, refinement, and removal; "
      "creates exactly |C_t^D| edges uniform without replacement from "
      "Pool_t under P_{t+1}.  Shortfall raises ControlMatchingFailure.")
    a("- Randomness: three domain-separated streams per seed; distinctness "
      "claimed, independence NOT claimed.")
    a("- Recurrence: full augmented key = (z, P.signature, R.signature, "
      "bounded ages).  The augmented sequence compared in T06 includes "
      "the initial t=0 key.")
    a("")
    a("## C. D-vs-CR causal contrast")
    a("")
    a("Both models share initial conditions, movement variates, movement "
      "rule, refinement rule, deterministic removal rule, and per-step "
      "creation counts.  They differ ONLY in the placement rule.")
    a("")
    a("## D. Proofs")
    a("")
    a("### D.1 History redundancy")
    a("H_0 = empty.  If (a,b) in H_t then a !~_{P_t} b, and P_{t+1} "
      "refines P_t, so a !~_{P_{t+1}} b.  Hence every dynamic edge is "
      "always cross-block and G(P_t, H_t) = G(P_t, empty).")
    a("")
    a("### D.2 Movement distribution")
    a("Idealized result: for finite S and U ~ Uniform[0,1), "
      "i = min(floor(u*|S|), |S|-1) maps equal u-intervals onto the sorted "
      "enumeration, giving probability 1/|S| per element.  Finite-"
      "precision note: CPython's random() returns a 53-bit float; the "
      "multiplication by |S| and floor may introduce rounding, so the "
      "implemented rule is an approximate realisation.  No numerical "
      "bound on the discrepancy is claimed.")
    a("")
    a("### D.3 CR feasibility invariant")
    a("C_t^D ⊆ Pool_t holds state-wise.  Cross-model condition "
      "|Pool_t^CR| >= |C_t^D| is checked before selection; a violation "
      "aborts the seed with a reported ControlMatchingFailure.  T14 "
      "reconstructs each CR pre-step graph and post-refinement partition "
      "and verifies every CR-created edge was absent and cross-block.")
    a("")
    a("## E. Methodology")
    a("")
    for k, v in config.items():
        if isinstance(v, dict):
            a(f"- {k} = {json.dumps(v, sort_keys=True, default=str)}")
        else:
            a(f"- {k} = {v}")
    a("")
    a("## F. Results (means over seeds)")
    a("")
    metrics = ["final_blocks", "final_edges", "final_gate_edges",
               "total_created_raw", "total_removed_raw",
               "created_ever_effective", "created_affecting_refinement",
               "partition_stable_at", "graph_stable_at",
               "combined_stable_at", "distinct_states"]
    a("| model | " + " | ".join(metrics) + " |")
    a("|" + "---|" * (len(metrics)+1))
    for m in ("A", "B", "C", "D", "CR"):
        cells = []
        for metric in metrics:
            mu = _mean_of(per_seed, metric, m)
            cells.append(f"{mu:.2f}" if mu is not None else "n/a")
        a(f"| {m} | " + " | ".join(cells) + " |")
    a("")
    a("## G. Paired per-seed differences")
    a("")
    a("| pair | metric | mean diff | std | min | max | n |")
    a("|---|---|---|---|---|---|---|")
    for p in paired:
        a(f"| {p['pair']} | {p['metric']} | {p['mean']:.3f} | {p['std']:.3f} "
          f"| {p['min']:.1f} | {p['max']:.1f} | {p['n']} |")
    a("")
    a("## H. Divergence counters")
    a("")
    for k, v in divergence.items():
        a(f"- {k} = {v}")
    a("")
    a("## I. Limitations")
    a("")
    a("- Single configuration unless cap-sensitivity is run separately.")
    a("- Reachability is measured from z_0 in stored and gate graphs "
      "separately.")
    a("- The optional cap is label-dependent.")
    a("- Streams are distinct but not proven independent.")
    a("- Paired differences report effect size only.")
    a("")
    a("## J. Evidence categories")
    a("")
    a("- Proofs: sections D.1-D.3.")
    a("- Tests: T00-T17, A1-A4 (CPython execution on fixtures).")
    a("- Empirical results: sections F-H.")
    a("")
    a("## K. Terminology")
    a("")
    a("Model D is a finite directed graph with a dynamically refined "
      "partition and inactivity-based edge churn.  No claims of "
      "collective computation, fields, novelty, or intelligence are made.")
    a("")
    a("## L. Verdict")
    a("")
    n = max(divergence["n_seeds"] -
            divergence["n_seeds_excluded_control_infeasible"], 0)
    if any_critical_fail:
        a("**No verdict.**  Critical diagnostic gates failed.")
    elif n == 0:
        a("**No verdict.**  No feasible seeds remained.")
    elif divergence["D_final_partition_differs_from_CR"] == 0 and \
            divergence["D_gate_reach_differs_from_CR"] == 0 and \
            divergence["D_stored_reach_differs_from_CR"] == 0:
        a("**Negative behavioural result:** under the matched control, D's "
          "partition-conditioned placement produced no distinguishable "
          "difference from uniform placement on any recorded observable.")
    else:
        a("**Distinguishable from matched control:** D differs from CR on "
          "at least one behavioural observable (see section H).")
    a("")
    _write_text("experiment_report.md", "\n".join(lines) + "\n")




# ===========================================================================
# 14.  IO and CLI
# ===========================================================================


OUT_DIR = "experiment_results"




def _ensure_out_dir():
    os.makedirs(OUT_DIR, exist_ok=True)




def _write_csv(name, rows):
    if not rows:
        return
    path = os.path.join(OUT_DIR, name)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in w.fieldnames})




def _write_text(name, text):
    with open(os.path.join(OUT_DIR, name), "w", encoding="utf-8") as f:
        f.write(text)




def _validate_args(args):
    if args.seeds is not None and args.seed is not None:
        raise ValueError("--seeds and --seed are mutually exclusive")
    if args.single_run and args.seed is None:
        raise ValueError("--single-run requires --seed")
    if args.n is not None and args.n < 1:
        raise ValueError("--n must be >= 1")
    if args.steps is not None and args.steps < 1:
        raise ValueError("--steps must be >= 1")
    if args.seeds is not None and args.seeds < 1:
        raise ValueError("--seeds must be >= 1")
    if args.edge_prob is not None and not (0.0 < args.edge_prob <= 1.0):
        raise ValueError("--edge-prob must be in (0, 1]")
    if args.initial_blocks is not None:
        if args.initial_blocks < 1:
            raise ValueError("--initial-blocks must be >= 1")
        if args.initial_blocks > (args.n or DEFAULT_CONFIG["N_STATES"]):
            raise ValueError("--initial-blocks must not exceed the state count")
    if args.removal_age < 1:
        raise ValueError("--removal-age must be >= 1")
    if args.cap is not None and args.cap < 1:
        raise ValueError("--cap must be >= 1")
    return args




def _parse_args(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--test", action="store_true")
    p.add_argument("--seeds", type=int, default=None)
    p.add_argument("--steps", type=int, default=None)
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--single-run", action="store_true")
    p.add_argument("--n", type=int, default=None)
    p.add_argument("--edge-prob", type=float, default=None)
    p.add_argument("--initial-blocks", type=int, default=None)
    p.add_argument("--cap", type=int, default=None)
    p.add_argument("--removal-age", type=int, default=5)
    p.add_argument("--cap-sensitivity", action="store_true")
    return p.parse_args(argv)




def _run_cap_sensitivity(n, ep, ib, steps, seeds, removal_age):
    results = {}
    for cap in (1, 2, 3, None):
        label = "unlimited" if cap is None else str(cap)
        print(f"\n=== cap sensitivity: cap={label} ===")
        res = run_full(n, ep, ib, steps, seeds, cap_per_source=cap,
                       removal_age=removal_age, out_subdir=f"cap_{label}")
        results[label] = res["divergence"]
    print("\n=== cap sensitivity summary ===")
    print(json.dumps(results, indent=2, default=str))




def main(argv=None):
    args = _validate_args(_parse_args(sys.argv[1:] if argv is None else argv))
    if args.test:
        _ensure_out_dir()
        results = run_all_tests()
        return 0 if all(v == "PASS" for v in results.values()) else 2
    n = args.n or DEFAULT_CONFIG["N_STATES"]
    ep = args.edge_prob if args.edge_prob is not None else DEFAULT_CONFIG["EDGE_PROBABILITY"]
    ib = args.initial_blocks or DEFAULT_CONFIG["INITIAL_BLOCKS"]
    steps = args.steps or DEFAULT_CONFIG["STEPS"]
    if args.seeds is not None:
        seeds = list(range(args.seeds))
    elif args.seed is not None:
        seeds = [args.seed]
    else:
        seeds = DEFAULT_CONFIG["SEEDS"]
    _ensure_out_dir()


    if args.cap_sensitivity:
        _run_cap_sensitivity(n, ep, ib, steps, seeds, args.removal_age)
        return 0


    if args.single_run:
        R, P0 = generate_instance(args.seed, n, ep, ib)
        uniforms = pre_draw_uniforms(args.seed, steps)
        print(f"[single run] seed={args.seed} n={n} ep={ep} ib={ib} "
              f"cap={args.cap} removal_age={args.removal_age}")
        runners = [(run_model_a, "A"), (run_model_b, "B"),
                   (run_model_c, "C"),
                   (lambda *a, **k: run_model_d(*a, cap_per_source=args.cap,
                                                removal_age=args.removal_age, **k),
                    "D")]
        for runner, name in runners:
            rec = runner(R, P0, args.seed % n, steps, uniforms,
                         movement_seed_for_label=args.seed)
            print(f"\n=== {name} ===")
            for s in rec.records[:15]:
                print(f"  t={s.t:>2} z {s.z_before}->{s.z_after} "
                      f"|P|={s.block_count} |R|={s.admissible_edge_count} "
                      f"|gate|={s.gate_edge_count} "
                      f"+{s.created_edges_raw} -{s.removed_edges_raw}")
            print(f"  stable P={rec.partition_stable_at} "
                  f"R={rec.graph_stable_at} combined={rec.combined_stable_at}")
        return 0


    result = run_full(n, ep, ib, steps, seeds, cap_per_source=args.cap,
                      removal_age=args.removal_age)
    gates = run_diagnostic_gates(result["per_seed"], result["step_traces"],
                                 result["graph_trace_rows"],
                                 list(range(n)))
    write_report(dict(n_states=n, edge_probability=ep, initial_blocks=ib,
                      steps=steps, n_seeds=len(seeds),
                      cap_per_source=args.cap, removal_age=args.removal_age,
                      provenance=_provenance(),
                      stream_seeds={str(s): {
                          "init": init_stream_seed(s),
                          "move": move_stream_seed(s),
                          "ctrl": cr_stream_seed(s)} for s in seeds}),
                 result["divergence"], result["per_seed"],
                 result["paired"], gates)
    d = result["divergence"]
    print("\n=== Execution summary ===")
    print(f"  seeds={len(seeds)} steps={steps} |Omega|={n} "
          f"cap={args.cap} removal_age={args.removal_age}")
    print(f"  divergence: {json.dumps(d, indent=2, default=str)}")
    print("  diagnostic gates:")
    for k in sorted(gates):
        tag = " CRITICAL" if k in CRITICAL_GATES else ""
        print(f"    {k}: {'PASS' if gates[k] else 'FAIL'}{tag}")
    failed_critical = [g for g in CRITICAL_GATES if not gates.get(g, False)]
    if failed_critical:
        print(f"  CRITICAL GATE FAILURE: {failed_critical}")
        return 2
    return 0




if __name__ == "__main__":
    sys.exit(main())
