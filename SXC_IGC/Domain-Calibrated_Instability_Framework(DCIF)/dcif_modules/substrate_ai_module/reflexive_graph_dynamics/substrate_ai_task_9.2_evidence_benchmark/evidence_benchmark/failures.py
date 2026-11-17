"""Exogenous edge-failure schedules (identical across models for a seed)."""

from __future__ import annotations

from typing import Any, Dict, List, Set, Tuple

from .streams import failure_rng


def schedule_edge_failures(
    seed: int,
    graph_edges: List[Tuple[Any, Any]],
    r0_edges: Set[Tuple[Any, Any]],
    fail_round: int,
    fraction: float = 0.20,
) -> Dict[int, Set[Tuple[Any, Any]]]:
    """Remove a fraction of edges at fail_round.

    Prefers non-R0 edges when available so the schedule stresses dynamic
    connectivity; falls back to any edges if needed. Same seed → same set
    when given the same candidate edge list. For cross-model pairing we pass
    the union of candidates or R0 edges only so the schedule is model-agnostic.

    For the benchmark we use R0 edges as the candidate pool so every model
    sees the identical failure set regardless of dynamic creations.
    """
    if fraction <= 0:
        return {}
    rng = failure_rng(seed)
    candidates = sorted(set(graph_edges))
    if not candidates:
        return {}
    k = max(1, int(round(fraction * len(candidates))))
    k = min(k, len(candidates))
    chosen = set(rng.sample(candidates, k))
    return {fail_round: chosen}
