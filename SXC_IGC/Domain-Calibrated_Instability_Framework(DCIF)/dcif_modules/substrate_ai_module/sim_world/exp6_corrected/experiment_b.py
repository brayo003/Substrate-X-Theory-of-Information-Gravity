"""Experiment B — Multi-agent collective information processing (Gate G6 / Claim C).

Three-agent design:
  Agent A deposits information X at site A.
  Agent B deposits information Y at site B.
  Agent C receives no direct A/B messages (except via the assigned architecture)
  and must recover the combined / interaction state.

Cases: Control1 none | Control2 X-only | Control3 Y-only | Test X+Y

Interaction task (primary):
  Label BOTH_NEAR = 1 iff X and Y are both deposited AND spatial separation ≤ near_sep.
  Distinguishes:
    - X alone, Y alone, neither
    - X+Y far (multiplexed presence without required spatial relation)
    - X+Y near (interaction / spatial relationship)

  Agent C's readout features are architecture-visible only.
  A fixed, documented decision rule (no train/test leakage of ground truth) maps
  features → label. Conventional architectures use explicit records; substrates
  use local samples at A, B, and midpoint.
"""
from __future__ import annotations

import math
import os
import sys
from typing import Any

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_SIM = os.path.dirname(_HERE)
_PARENT = os.path.dirname(_SIM)
for _p in (_PARENT, _SIM):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from sim_world.exp6_corrected import config as cfg
from sim_world.exp6_corrected.architectures import make_memory
from sim_world.exp6_corrected.statistics import classification_metrics


CASES = ("none", "X", "Y", "XY_near", "XY_far")
NEAR_SEP = cfg.EXP_B_SEPARATIONS[0]   # 6.0
FAR_SEP = cfg.EXP_B_SEPARATIONS[1]    # 18.0


def _site_pair(seed: int, separation: float) -> tuple[tuple[float, float], tuple[float, float]]:
    rng = np.random.default_rng(seed + 303)
    cx = float(rng.uniform(15.0, cfg.GRID_X - 15.0))
    cy = float(rng.uniform(15.0, cfg.GRID_Y - 15.0))
    angle = float(rng.uniform(0, 2 * math.pi))
    hx, hy = 0.5 * separation * math.cos(angle), 0.5 * separation * math.sin(angle)
    a = (float(np.clip(cx - hx, 5, cfg.GRID_X - 5)),
         float(np.clip(cy - hy, 5, cfg.GRID_Y - 5)))
    b = (float(np.clip(cx + hx, 5, cfg.GRID_X - 5)),
         float(np.clip(cy + hy, 5, cfg.GRID_Y - 5)))
    return a, b


def _true_label(case: str) -> int:
    """Interaction label: 1 only for XY_near."""
    return 1 if case == "XY_near" else 0


def _deposit_case(mem, case: str, site_a, site_b, tick: int = 0) -> None:
    amp = cfg.SUB_DEPOSIT_AMP if mem.name.endswith("sub") else 1.0
    if case in ("X", "XY_near", "XY_far"):
        mem.deposit("X", site_a[0], site_a[1], amp, tick, meta={"channel": "X"})
        # Also deposit as event markers for structured memories
        mem.deposit("event", site_a[0], site_a[1], amp, tick, meta={"which": "X"})
    if case in ("Y", "XY_near", "XY_far"):
        # For scalar substrate, Y is a second positive deposit at site B
        # (spatial multiplexing — not claimed as independent semantic channels)
        mem.deposit("Y", site_b[0], site_b[1], amp, tick, meta={"channel": "Y"})
        mem.deposit("event", site_b[0], site_b[1], amp, tick, meta={"which": "Y"})


def _agent_c_features(mem, site_a, site_b, tick: int) -> dict[str, float]:
    """Features recoverable by Agent C through the assigned architecture only."""
    mx = 0.5 * (site_a[0] + site_b[0])
    my = 0.5 * (site_a[1] + site_b[1])
    feats = {
        "sig_A": float(mem.query_at("X", site_a[0], site_a[1], tick)),
        "sig_B": float(mem.query_at("Y", site_b[0], site_b[1], tick)),
        "sig_mid": float(mem.query_at("event", mx, my, tick)),
        "sig_A_event": float(mem.query_at("event", site_a[0], site_a[1], tick)),
        "sig_B_event": float(mem.query_at("event", site_b[0], site_b[1], tick)),
    }
    # Structured records
    known_x = [r for r in mem.list_known("X", tick)] + [
        r for r in mem.list_known("event", tick) if (r.get("meta") or {}).get("which") == "X"
    ]
    known_y = [r for r in mem.list_known("Y", tick)] + [
        r for r in mem.list_known("event", tick) if (r.get("meta") or {}).get("which") == "Y"
    ]
    feats["n_X_records"] = float(len(known_x))
    feats["n_Y_records"] = float(len(known_y))
    if known_x and known_y:
        dmin = min(
            math.hypot(rx["x"] - ry["x"], rx["y"] - ry["y"])
            for rx in known_x for ry in known_y
        )
        feats["record_sep"] = float(dmin)
    else:
        feats["record_sep"] = float("inf")
    return feats


def _predict_interaction(condition: str, feats: dict[str, float],
                         near_sep: float = NEAR_SEP) -> int:
    """
    Documented readout rule (no ground-truth access).

    Structured (msg/blackboard): BOTH_NEAR if both X and Y records exist and
    recorded separation ≤ near_sep.

    Spatial (pheromone / substrates): BOTH_NEAR if signals at A and B exceed
    threshold AND midpoint signal exceeds an interaction threshold that is
    higher than expected from a single isolated deposit.
    """
    if condition in ("direct_msg", "blackboard"):
        if feats["n_X_records"] >= 1 and feats["n_Y_records"] >= 1:
            return 1 if feats["record_sep"] <= near_sep + 1e-6 else 0
        return 0

    if condition == "independent":
        return 0

    # Spatial media thresholds (fixed a priori)
    if condition == "pheromone":
        thr_site = 0.2
        thr_mid = 0.15
    elif condition == "nonlinear_sub":
        thr_site = 0.35
        thr_mid = 0.25
    else:  # linear_sub
        thr_site = 0.15
        thr_mid = 0.12

    a_on = max(feats["sig_A"], feats["sig_A_event"]) >= thr_site
    b_on = max(feats["sig_B"], feats["sig_B_event"]) >= thr_site
    mid_on = feats["sig_mid"] >= thr_mid
    # Interaction criterion: both sites active AND midpoint elevated
    # (for far deposits, midpoint should stay low → predicts 0)
    if a_on and b_on and mid_on:
        return 1
    return 0


def _predict_presence(condition: str, feats: dict[str, float]) -> str:
    """Secondary: classify none / X / Y / both (multiplex), not the interaction label."""
    if condition in ("direct_msg", "blackboard"):
        has_x = feats["n_X_records"] >= 1
        has_y = feats["n_Y_records"] >= 1
    elif condition == "independent":
        has_x = has_y = False
    else:
        thr = 0.35 if condition == "nonlinear_sub" else 0.15
        has_x = max(feats["sig_A"], feats["sig_A_event"]) >= thr
        has_y = max(feats["sig_B"], feats["sig_B_event"]) >= thr
    if has_x and has_y:
        return "both"
    if has_x:
        return "X"
    if has_y:
        return "Y"
    return "none"


def run_trial_exp_b(seed: int, condition: str, case: str) -> dict[str, Any]:
    sep = NEAR_SEP if case == "XY_near" else FAR_SEP
    if case in ("none", "X", "Y"):
        sep = FAR_SEP  # irrelevant; sites still defined
    site_a, site_b = _site_pair(seed, sep)
    # For single-input cases, still define both sites for probe geometry
    if case in ("X", "Y", "none"):
        site_a, site_b = _site_pair(seed, FAR_SEP)

    mem = make_memory(condition)
    _deposit_case(mem, case, site_a, site_b, tick=0)

    # Agents A and B disconnect: evolve without further deposits.
    # Keep evolve_ticks < MSG_TTL so direct messaging is tested on collective
    # combination (not TTL expiry). Persistence across long delays is Exp A.
    evolve_ticks = min(5, cfg.MSG_TTL - 1)
    for t in range(1, evolve_ticks + 1):
        mem.tick_update(t)
        if mem.failed():
            return {
                "seed": seed, "condition": condition, "case": case,
                "failed": True, "solver_failed": True,
                "usage": mem.usage().to_dict(),
            }

    tick = evolve_ticks
    feats = _agent_c_features(mem, site_a, site_b, tick)
    y_true = _true_label(case)
    y_pred = _predict_interaction(condition, feats)
    presence_pred = _predict_presence(condition, feats)

    # True presence class for secondary metric
    if case == "none":
        presence_true = "none"
    elif case == "X":
        presence_true = "X"
    elif case == "Y":
        presence_true = "Y"
    else:
        presence_true = "both"

    return {
        "seed": seed,
        "condition": condition,
        "case": case,
        "failed": False,
        "solver_failed": False,
        "site_a": list(site_a),
        "site_b": list(site_b),
        "separation": math.hypot(site_a[0] - site_b[0], site_a[1] - site_b[1]),
        "features": feats,
        "y_true_interaction": y_true,
        "y_pred_interaction": y_pred,
        "interaction_correct": int(y_pred == y_true),
        "presence_true": presence_true,
        "presence_pred": presence_pred,
        "presence_correct": int(presence_pred == presence_true),
        "usage": mem.usage().to_dict(),
        "field_stats": mem.field_stats() if hasattr(mem, "field_stats") else None,
    }


def run_experiment_b(seeds: list[int], conditions: list[str] | None = None,
                     verbose: bool = True) -> dict[str, Any]:
    conditions = list(conditions or cfg.CONDITIONS)
    trials = []
    total = len(seeds) * len(conditions) * len(CASES)
    done = 0
    for seed in seeds:
        for cond in conditions:
            for case in CASES:
                trials.append(run_trial_exp_b(seed, cond, case))
                done += 1
                if verbose and done % 40 == 0:
                    print(f"  ExpB {done}/{total}")

    summary = {}
    for cond in conditions:
        subset = [t for t in trials if t["condition"] == cond and not t.get("failed")]
        failed = [t for t in trials if t["condition"] == cond and t.get("failed")]
        if not subset:
            summary[cond] = {"n": 0, "n_failed": len(failed)}
            continue
        y_true = [t["y_true_interaction"] for t in subset]
        y_pred = [t["y_pred_interaction"] for t in subset]
        cls = classification_metrics(y_true, y_pred, positive=1)
        # Per-case accuracy
        by_case = {}
        for case in CASES:
            sc = [t for t in subset if t["case"] == case]
            by_case[case] = {
                "n": len(sc),
                "interaction_acc": float(np.mean([t["interaction_correct"] for t in sc])) if sc else 0.0,
                "presence_acc": float(np.mean([t["presence_correct"] for t in sc])) if sc else 0.0,
            }
        # Distinguish combined from individuals: on XY_near, pred=1; on X and Y, pred=0
        x_only = [t for t in subset if t["case"] == "X"]
        y_only = [t for t in subset if t["case"] == "Y"]
        xy_near = [t for t in subset if t["case"] == "XY_near"]
        xy_far = [t for t in subset if t["case"] == "XY_far"]
        # Balanced accuracy: mean of TPR (xy_near) and TNR (all negatives)
        tpr = float(np.mean([t["y_pred_interaction"] for t in xy_near])) if xy_near else 0.0
        negatives = [t for t in subset if t["case"] != "XY_near"]
        tnr = float(np.mean([1 - t["y_pred_interaction"] for t in negatives])) if negatives else 0.0
        summary[cond] = {
            "n": len(subset),
            "n_failed": len(failed),
            "interaction_accuracy": float(np.mean([t["interaction_correct"] for t in subset])),
            "interaction_f1": float(cls["f1"]),
            "interaction_precision": float(cls["precision"]),
            "interaction_recall": float(cls["recall"]),
            "balanced_accuracy": 0.5 * (tpr + tnr),
            "presence_accuracy": float(np.mean([t["presence_correct"] for t in subset])),
            "interaction_metrics": cls,
            "by_case": by_case,
            "xy_near_hit_rate": tpr,
            "x_only_false_pos": float(np.mean([t["y_pred_interaction"] for t in x_only])) if x_only else 0.0,
            "y_only_false_pos": float(np.mean([t["y_pred_interaction"] for t in y_only])) if y_only else 0.0,
            "xy_far_pred_rate": float(np.mean([t["y_pred_interaction"] for t in xy_far])) if xy_far else 0.0,
            "none_false_pos": float(np.mean([
                t["y_pred_interaction"] for t in subset if t["case"] == "none"
            ])) if any(t["case"] == "none" for t in subset) else 0.0,
        }

    # G6 notes — pass requires BOTH_NEAR recovery + discrimination (F1, not raw acc)
    nl = summary.get("nonlinear_sub", {})
    g6 = {
        "agent_c_recovers_combined": nl.get("xy_near_hit_rate", 0) > 0.5,
        "distinguishable_from_individual": (
            nl.get("x_only_false_pos", 1) < 0.5 and nl.get("y_only_false_pos", 1) < 0.5
        ),
        "spatial_relation_matters": (
            nl.get("xy_near_hit_rate", 0) > nl.get("xy_far_pred_rate", 1) + 0.1
        ),
        "not_hardcoded_lookup": True,  # rule uses architecture features only
        "compared_to_conventional": True,
        "primary_metric": "interaction_f1",
        "pass_candidate": (
            nl.get("interaction_f1", 0) >= 0.5
            and nl.get("xy_near_hit_rate", 0) > 0.5
            and nl.get("x_only_false_pos", 1) < 0.5
            and nl.get("y_only_false_pos", 1) < 0.5
            and nl.get("xy_near_hit_rate", 0) > nl.get("xy_far_pred_rate", 1)
        ),
        "note_if_only_multiplex": (
            "If XY_near and XY_far are indistinguishable, report multiplexed "
            "persistent memory — not collective information processing."
        ),
        "note_accuracy_trap": (
            "Raw interaction_accuracy is NOT the primary endpoint: with 4/5 "
            "negative cases, always-predict-0 yields 0.8 accuracy and F1=0."
        ),
    }

    return {
        "experiment": "B_collective_information_processing",
        "primary_endpoint": cfg.PRIMARY_ENDPOINT,
        "cases": list(CASES),
        "trials": trials,
        "summary": summary,
        "g6_notes": g6,
        "n_seeds": len(seeds),
        "readout_rule": (
            "Structured: both records & sep≤near. "
            "Spatial: A&B above thr and midpoint above interaction thr."
        ),
    }
