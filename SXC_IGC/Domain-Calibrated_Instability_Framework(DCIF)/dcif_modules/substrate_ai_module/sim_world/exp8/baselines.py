"""Conventional baselines for Task 8 operations — fair, not weakened."""
from __future__ import annotations

import math
from typing import Any

from sim_world.exp8 import config as cfg


def symbolic_coincidence(sites: list[tuple[float, float]], near_sep: float = cfg.A_NEAR_SEP) -> int:
    """Explicit pairwise distance AND — what messaging/blackboard can do."""
    if len(sites) < 2:
        return 0
    for i in range(len(sites)):
        for j in range(i + 1, len(sites)):
            d = math.hypot(sites[i][0] - sites[j][0], sites[i][1] - sites[j][1])
            if d <= near_sep + 1.0:
                return 1
    return 0


def symbolic_temporal(delay: int, window: int = 5) -> int:
    return int(delay <= window)


def run_baseline_A(seeds: list[int]) -> dict[str, Any]:
    """Symbolic baseline achieves perfect AND by construction on labeled cases."""
    rows = []
    for seed in seeds:
        for case, sites, y_true in _A_cases(seed):
            y_pred = symbolic_coincidence(sites)
            # single: 0 sites pair → 0; near → 1; far → 0
            if case == "single":
                y_pred = 0
            rows.append({
                "seed": seed, "case": case, "y_true": y_true, "y_pred": y_pred,
                "correct": int(y_pred == y_true), "baseline": "symbolic_distance",
            })
    acc = sum(r["correct"] for r in rows) / len(rows) if rows else 0
    return {"baseline": "symbolic_coincidence", "accuracy": acc, "trials": rows,
            "note": "Explicit coordinates + distance; not field dynamics."}


def _A_cases(seed: int):
    from sim_world.exp8.field_core import pair_sites
    a, b, _ = pair_sites(seed, cfg.A_NEAR_SEP)
    af, bf, _ = pair_sites(seed, cfg.A_FAR_SEP)
    return [
        ("single", [a], 0),
        ("near_pair", [a, b], 1),
        ("far_pair", [af, bf], 0),
    ]


def fairness_notes() -> dict[str, Any]:
    return {
        "symbolic_baseline": "Full coordinate precision; unlimited symbolic ops",
        "nonlinear_field": f"grid {cfg.GRID_NX}x{cfg.GRID_NY}; scalar; local Gaussian deposits",
        "linear_field": "same grid/encoding; no reaction",
        "task7_carry_forward": "Messaging/BB F1=1.0 on AND — retained, not re-litigated",
        "claim_boundary": (
            "Task 8 evaluates intrinsic field computation; beating symbolic "
            "baselines is NOT required for Levels 1–4."
        ),
    }
