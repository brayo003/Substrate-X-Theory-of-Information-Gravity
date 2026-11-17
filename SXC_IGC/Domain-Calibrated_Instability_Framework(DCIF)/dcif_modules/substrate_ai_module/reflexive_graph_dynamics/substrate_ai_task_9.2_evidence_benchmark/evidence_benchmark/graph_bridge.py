"""Bridge to one.py model runners without modifying them.

Extracts directed graph sequences used as communication topologies.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

# Import substrate from project root without altering it
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import one as substrate  # noqa: E402


@dataclass
class ModelTimeline:
    model: str
    seed: int
    run: Any  # RunResult
    graphs: List[Any]  # TransitionGraph snapshots G_0 .. G_T
    partitions: List[Any]
    created_edges: List[Set[Tuple[Any, Any]]]  # per step
    removed_edges: List[Set[Tuple[Any, Any]]]
    total_created: int
    total_removed: int
    control_infeasible: bool = False
    infeasible_reason: str = ""


def graph_from_signature(states, signature) -> "substrate.TransitionGraph":
    g = substrate.TransitionGraph(states)
    for a, b in signature:
        g.add_edge(a, b)
    return g


def bidirected(R) -> "substrate.TransitionGraph":
    """Conventional undirected view: every edge present in both directions."""
    g = substrate.TransitionGraph(R.states())
    for a, b in R.edges():
        g.add_edge(a, b)
        g.add_edge(b, a)
    return g


def relabel_graph(R, perm: Dict[Any, Any]):
    g = substrate.TransitionGraph([perm[s] for s in R.states()])
    for a, b in R.edges():
        g.add_edge(perm[a], perm[b])
    return g


def relabel_partition(P, perm: Dict[Any, Any]):
    blocks = [[perm[s] for s in b] for b in P.blocks()]
    return substrate.Partition([perm[s] for s in P.states()], blocks)


def _timeline_from_run(model: str, seed: int, run, R0) -> ModelTimeline:
    states = sorted(R0.states())
    graphs = [R0.copy()]
    partitions = [run.initial_partition.copy() if run.initial_partition else None]
    created, removed = [], []
    for rec in run.records:
        graphs.append(graph_from_signature(states, rec.graph_signature))
        # reconstruct partition from serialized blocks
        blocks = [list(b) for b in rec.partition_blocks]
        partitions.append(substrate.Partition(states, blocks))
        created.append(set(rec.created_set))
        removed.append(set(rec.removed_set))
    return ModelTimeline(
        model=model, seed=seed, run=run, graphs=graphs, partitions=partitions,
        created_edges=created, removed_edges=removed,
        total_created=sum(len(s) for s in created),
        total_removed=sum(len(s) for s in removed),
    )


def run_all_models(
    seed: int,
    n_states: int,
    edge_prob: float,
    n_initial_blocks: int,
    steps: int,
    cap_per_source=None,
    removal_age: int = 5,
) -> Dict[str, ModelTimeline]:
    """Run A,B,C,D,CR with identical paired init; return timelines."""
    R0, P0 = substrate.generate_instance(seed, n_states, edge_prob, n_initial_blocks)
    z0 = seed % n_states
    uniforms = substrate.pre_draw_uniforms(seed, steps)

    rA = substrate.run_model_a(R0, P0, z0, steps, uniforms, seed)
    rB = substrate.run_model_b(R0, P0, z0, steps, uniforms, seed)
    rC = substrate.run_model_c(R0, P0, z0, steps, uniforms, seed)
    rD = substrate.run_model_d(
        R0, P0, z0, steps, uniforms, seed,
        cap_per_source=cap_per_source, removal_age=removal_age)
    d_created = [rec.created_edges_raw for rec in rD.records]

    out: Dict[str, ModelTimeline] = {
        "A": _timeline_from_run("A", seed, rA, R0),
        "B": _timeline_from_run("B", seed, rB, R0),
        "C": _timeline_from_run("C", seed, rC, R0),
        "D": _timeline_from_run("D", seed, rD, R0),
    }
    try:
        rCR = substrate.run_control_random_matched(
            R0, P0, z0, steps, uniforms, seed,
            d_created_per_step=d_created, removal_age=removal_age)
        out["CR"] = _timeline_from_run("CR", seed, rCR, R0)
    except substrate.ControlMatchingFailure as exc:
        out["CR"] = ModelTimeline(
            model="CR", seed=seed, run=None, graphs=[R0.copy()],
            partitions=[P0.copy()], created_edges=[], removed_edges=[],
            total_created=0, total_removed=0,
            control_infeasible=True, infeasible_reason=str(exc),
        )
    # stash shared init on D for convenience
    out["_R0"] = R0  # type: ignore
    out["_P0"] = P0  # type: ignore
    out["_z0"] = z0  # type: ignore
    out["_d_created"] = d_created  # type: ignore
    return out


def make_mv_timeline(R0, steps: int, seed: int) -> ModelTimeline:
    """Conventional baseline topology: static bidirected initial graph."""
    G = bidirected(R0)
    graphs = [G.copy() for _ in range(steps + 1)]
    return ModelTimeline(
        model="MV", seed=seed, run=None, graphs=graphs,
        partitions=[], created_edges=[], removed_edges=[],
        total_created=0, total_removed=0,
    )


def verify_d_cr_creation_match(tl_d: ModelTimeline, tl_cr: ModelTimeline) -> bool:
    if tl_cr.control_infeasible:
        return False
    if len(tl_d.created_edges) != len(tl_cr.created_edges):
        return False
    for a, b in zip(tl_d.created_edges, tl_cr.created_edges):
        if len(a) != len(b):
            return False
    return True
