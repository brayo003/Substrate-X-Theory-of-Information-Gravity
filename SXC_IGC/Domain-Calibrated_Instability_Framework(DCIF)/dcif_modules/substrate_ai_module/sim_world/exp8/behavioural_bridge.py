"""Conditional behavioural bridge: agents exploit a robust coincidence primitive.

Only justified when Exp A (or D) reaches Category ≥4 in classification.
Task: two observer agents each deposit one subthreshold cue; a decision agent
reads the field and acts if the collective latch fires. Ground truth = whether
the two cues were spatially coincident (near vs far).

Causal isolation vs linear / reaction-off / independent / symbolic messaging.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from sim_world.exp8 import config as cfg
from sim_world.exp8.field_core import FieldSim, activated, pair_sites
from sim_world.exp8.baselines import symbolic_coincidence


def run_bridge_trial(seed: int, near: bool, mode: str) -> dict[str, Any]:
    """
    Modes:
      nonlinear_full | linear_telegraph | reaction_off | independent | symbolic
    """
    sep = cfg.BRIDGE_SEP_NEAR if near else cfg.BRIDGE_SEP_FAR
    a, b, mid = pair_sites(seed, sep)
    y_true = int(near)

    if mode == "symbolic":
        y_pred = symbolic_coincidence([a, b], cfg.BRIDGE_SEP_NEAR)
        return {
            "seed": seed, "near": near, "mode": mode, "failed": False,
            "y_true": y_true, "y_pred": y_pred, "correct": int(y_pred == y_true),
            "comm_volume": 2, "note": "explicit coordinates shared",
        }

    if mode == "independent":
        # Each agent only sees own deposit; decision agent gets no field → always 0
        return {
            "seed": seed, "near": near, "mode": mode, "failed": False,
            "y_true": y_true, "y_pred": 0, "correct": int(0 == y_true),
            "comm_volume": 0, "note": "no shared medium",
        }

    abl = mode
    sim = FieldSim(abl)
    # Observer A, Observer B deposit independently
    sim.deposit(*a, cfg.BRIDGE_OBS_AMP, 0)
    sim.deposit(*b, cfg.BRIDGE_OBS_AMP, 0)
    if not sim.evolve(cfg.BRIDGE_EVOLVE):
        return {"seed": seed, "near": near, "mode": mode, "failed": True,
                "solver_failed": True}
    # Decision agent reads field only
    y_pred = int(activated(sim, *mid))
    return {
        "seed": seed, "near": near, "mode": mode, "failed": False,
        "y_true": y_true, "y_pred": y_pred, "correct": int(y_pred == y_true),
        "local_max": sim.local_max(*mid), "comm_volume": 0,
        "note": "decision from field latch only",
    }


def run_behavioural_bridge(seeds: list[int], justified: bool) -> dict[str, Any]:
    if not justified:
        return {
            "justified": False,
            "skipped": True,
            "reason": "No Category≥4 primitive from A–F; bridge not forced.",
            "causal_pass": False,
        }

    modes = (
        "nonlinear_full",
        "linear_telegraph",
        "reaction_off",
        "independent",
        "symbolic",
    )
    trials = []
    for seed in seeds:
        for near in (True, False):
            for mode in modes:
                trials.append(run_bridge_trial(seed, near, mode))

    summary = {}
    for mode in modes:
        sub = [t for t in trials if t.get("mode") == mode and not t.get("failed")]
        if not sub:
            summary[mode] = {"n": 0, "accuracy": None, "f1": None}
            continue
        yt = [t["y_true"] for t in sub]
        yp = [t["y_pred"] for t in sub]
        tp = sum(1 for a, b in zip(yt, yp) if a == 1 and b == 1)
        fp = sum(1 for a, b in zip(yt, yp) if a == 0 and b == 1)
        fn = sum(1 for a, b in zip(yt, yp) if a == 1 and b == 0)
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        summary[mode] = {
            "n": len(sub),
            "accuracy": float(np.mean([t["correct"] for t in sub])),
            "f1": f1,
            "precision": prec,
            "recall": rec,
        }

    nl = summary.get("nonlinear_full", {})
    lin = summary.get("linear_telegraph", {})
    indep = summary.get("independent", {})
    sym = summary.get("symbolic", {})
    causal_pass = bool(
        (nl.get("f1") or 0) >= 0.75
        and (lin.get("f1") or 0) < 0.4
        and (indep.get("f1") or 0) < 0.4
    )
    return {
        "justified": True,
        "skipped": False,
        "trials": trials,
        "summary": summary,
        "causal_pass": causal_pass,
        "notes": {
            "nonlinear_f1": nl.get("f1"),
            "linear_f1": lin.get("f1"),
            "independent_f1": indep.get("f1"),
            "symbolic_f1": sym.get("f1"),
            "interpretation": (
                "Causal pass = nonlinear latch used for decision; linear/independent fail. "
                "Symbolic may still achieve F1=1.0 (fair baseline; not a failure of substrate)."
            ),
        },
    }
