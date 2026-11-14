"""Paired comparisons and effect sizes for Task 9."""
from __future__ import annotations

from typing import Any, Sequence

import numpy as np


def paired_correct_rates(
    trials: list[dict],
    arch_a: str,
    arch_b: str,
    *,
    key_arch: str = "arch",
    metric: str = "correct",
) -> dict[str, Any]:
    by_seed_a = {t["seed"]: t[metric] for t in trials if t.get(key_arch) == arch_a and not t.get("failed")}
    by_seed_b = {t["seed"]: t[metric] for t in trials if t.get(key_arch) == arch_b and not t.get("failed")}
    seeds = sorted(set(by_seed_a) & set(by_seed_b))
    if not seeds:
        return {"arch_a": arch_a, "arch_b": arch_b, "n": 0}
    da = np.array([by_seed_a[s] for s in seeds], dtype=float)
    db = np.array([by_seed_b[s] for s in seeds], dtype=float)
    diff = da - db
    mean_diff = float(np.mean(diff))
    sd = float(np.std(diff, ddof=1)) if len(diff) > 1 else 0.0
    dz = mean_diff / sd if sd > 1e-12 else (float("inf") if abs(mean_diff) > 0 else 0.0)
    # Sign permutation test
    rng = np.random.default_rng(0)
    n_perm = min(5000, 2 ** len(diff)) if len(diff) <= 12 else 5000
    count = 0
    abs_obs = abs(mean_diff)
    for _ in range(n_perm):
        signs = rng.choice([-1, 1], size=len(diff))
        if abs(float(np.mean(signs * diff))) >= abs_obs - 1e-15:
            count += 1
    p_perm = (count + 1) / (n_perm + 1)
    # Wilcoxon-ish sign count
    n_pos = int(np.sum(diff > 0))
    n_neg = int(np.sum(diff < 0))
    return {
        "arch_a": arch_a,
        "arch_b": arch_b,
        "n": len(seeds),
        "mean_a": float(np.mean(da)),
        "mean_b": float(np.mean(db)),
        "mean_diff": mean_diff,
        "d_z": float(dz) if np.isfinite(dz) else None,
        "p_perm": float(p_perm),
        "n_pos": n_pos,
        "n_neg": n_neg,
        "seeds": seeds,
    }


def bonferroni(pvals: Sequence[float], alpha: float, m: int | None = None) -> list[dict[str, Any]]:
    m = len(pvals) if m is None else m
    out = []
    for i, p in enumerate(pvals):
        adj = min(1.0, float(p) * m)
        out.append({"index": i, "p": float(p), "p_adj": adj, "reject": adj < alpha})
    return out
