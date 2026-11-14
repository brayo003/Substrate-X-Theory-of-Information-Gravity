"""Experiments A–F: substrate computational operations."""
from __future__ import annotations

import math
from typing import Any

import numpy as np

from sim_world.exp8 import config as cfg
from sim_world.exp8.field_core import FieldSim, activated, pair_sites


# ---------------------------------------------------------------------------
# A — Coincidence detection (+ response surface)
# ---------------------------------------------------------------------------

def run_A_trial(seed: int, case: str, amp: float = cfg.A_SUB_AMP,
                sep: float | None = None, ablation: str = "nonlinear_full",
                n_inputs: int = 2) -> dict[str, Any]:
    """
    Cases:
      single | near_pair | far_pair | triple_near | custom_sep
    Ground truth from schedule labels (not deposit_log readout).
    """
    if sep is None:
        sep = cfg.A_NEAR_SEP if case in ("near_pair", "triple_near", "custom_sep") else cfg.A_FAR_SEP
    if case == "single":
        sep = cfg.A_FAR_SEP
    a, b, mid = pair_sites(seed, sep)
    sim = FieldSim(ablation)
    if case == "single":
        sim.deposit(*a, amp, 0)
        y_true = 0
        readout_xy = a
    elif case == "near_pair":
        sim.deposit(*a, amp, 0)
        sim.deposit(*b, amp, 0)
        y_true = 1
        readout_xy = mid
    elif case == "far_pair":
        sim.deposit(*a, amp, 0)
        sim.deposit(*b, amp, 0)
        y_true = 0
        readout_xy = mid
    elif case == "triple_near":
        # three points on a small triangle; each individually subthreshold
        rng = np.random.default_rng(seed + 7)
        cx, cy = mid
        pts = []
        for k in range(3):
            ang = 2 * math.pi * k / 3 + float(rng.uniform(0, 0.2))
            pts.append((cx + 1.2 * math.cos(ang), cy + 1.2 * math.sin(ang)))
        for p in pts:
            sim.deposit(p[0], p[1], amp * cfg.A_TRIPLE_FRAC, 0)
        y_true = 1
        readout_xy = (cx, cy)
    else:  # custom_sep
        sim.deposit(*a, amp, 0)
        sim.deposit(*b, amp, 0)
        y_true = int(sep <= cfg.A_NEAR_SEP + 1.0)
        readout_xy = mid

    if not sim.evolve(cfg.A_EVOLVE):
        return {"seed": seed, "case": case, "ablation": ablation, "failed": True,
                "solver_failed": True}
    y_pred = int(activated(sim, *readout_xy))
    st = sim.stats()
    return {
        "seed": seed, "case": case, "ablation": ablation, "failed": False,
        "amp": amp, "sep": sep, "y_true": y_true, "y_pred": y_pred,
        "correct": int(y_pred == y_true), "max_field": st["max"],
        "local_max": sim.local_max(*readout_xy),
        "frac_high": st["frac_high"], "n_steps": sim.n_steps,
    }


def run_A_response_surface(seeds: list[int], ablation: str = "nonlinear_full") -> dict[str, Any]:
    """Parameterized (amp × sep) activation probability for pairs."""
    cells = []
    for amp in cfg.A_AMP_GRID:
        for sep in cfg.A_SEP_GRID:
            acts = []
            fails = 0
            for seed in seeds:
                t = run_A_trial(seed, "custom_sep", amp=amp, sep=sep, ablation=ablation)
                if t.get("failed"):
                    fails += 1
                    continue
                acts.append(t["y_pred"])
            cells.append({
                "amp": amp, "sep": sep,
                "p_activate": float(np.mean(acts)) if acts else None,
                "n": len(acts), "n_failed": fails,
            })
    return {"ablation": ablation, "cells": cells, "n_seeds": len(seeds)}


def run_A_suite(seeds: list[int]) -> dict[str, Any]:
    cases = ("single", "near_pair", "far_pair", "triple_near")
    trials = []
    for seed in seeds:
        for abl in cfg.ABLATIONS:
            for case in cases:
                trials.append(run_A_trial(seed, case, ablation=abl))
    summary = _cls_summary(trials, cases_key="case", group_key="ablation")
    surface_nl = run_A_response_surface(seeds, "nonlinear_full")
    surface_lin = run_A_response_surface(seeds[: max(3, len(seeds) // 2)], "linear_telegraph")
    # Primary: near_pair recall vs far/single FPR for nonlinear
    nl = [t for t in trials if t.get("ablation") == "nonlinear_full" and not t.get("failed")]
    metrics = _binary_metrics(nl)
    return {
        "experiment": "A_coincidence",
        "trials": trials,
        "summary_by_ablation": summary,
        "response_surface_nl": surface_nl,
        "response_surface_lin": surface_lin,
        "primary_metrics": metrics,
    }


# ---------------------------------------------------------------------------
# B — Temporal integration
# ---------------------------------------------------------------------------

def run_B_trial(seed: int, delay: int, ablation: str = "nonlinear_full",
                reverse: bool = False) -> dict[str, Any]:
    a, b, mid = pair_sites(seed, cfg.B_SEP)
    sim = FieldSim(ablation)
    first, second = (b, a) if reverse else (a, b)
    sim.deposit(*first, cfg.B_SUB_AMP, 0)
    if delay > 0:
        if not sim.evolve(delay):
            return {"seed": seed, "delay": delay, "ablation": ablation,
                    "failed": True, "solver_failed": True}
    sim.deposit(*second, cfg.B_SUB_AMP, delay)
    if not sim.evolve(cfg.B_EVOLVE_AFTER, start_tick=delay + 1):
        return {"seed": seed, "delay": delay, "ablation": ablation,
                "failed": True, "solver_failed": True}
    # GT: activate if delay within field memory window (pilot-calibrated)
    y_true = int(delay <= cfg.B_MEM_WINDOW)
    y_pred = int(activated(sim, *mid))
    return {
        "seed": seed, "delay": delay, "ablation": ablation, "reverse": reverse,
        "failed": False, "y_true": y_true, "y_pred": y_pred,
        "correct": int(y_pred == y_true),
        "local_max": sim.local_max(*mid), "max_field": sim.stats()["max"],
    }


def run_B_suite(seeds: list[int]) -> dict[str, Any]:
    trials = []
    for seed in seeds:
        for abl in ("nonlinear_full", "linear_telegraph", "reaction_off", "no_inertia"):
            for delay in cfg.B_DELAYS:
                trials.append(run_B_trial(seed, delay, abl, reverse=False))
                if delay in (2, 10):
                    trials.append(run_B_trial(seed, delay, abl, reverse=True))
    # Integration window: p(activate) vs delay for nonlinear
    window = {}
    for d in cfg.B_DELAYS:
        sub = [t for t in trials if t.get("ablation") == "nonlinear_full"
               and t.get("delay") == d and not t.get("failed") and not t.get("reverse")]
        window[str(d)] = {
            "p_activate": float(np.mean([t["y_pred"] for t in sub])) if sub else None,
            "mean_local_max": float(np.mean([t["local_max"] for t in sub])) if sub else None,
            "n": len(sub),
        }
    return {"experiment": "B_temporal", "trials": trials, "integration_window": window}


# ---------------------------------------------------------------------------
# C — Spatial discrimination (equal mass)
# ---------------------------------------------------------------------------

def run_C_trial(seed: int, geometry: str, ablation: str = "nonlinear_full") -> dict[str, Any]:
    """
    Geometries with identical total deposited amplitude C_TOTAL_MASS:
      cluster (2× near), dispersed (2× far), line3, triangle
    GT: cluster/triangle → activate; dispersed → not; line3 → borderline (label 0)
    """
    rng = np.random.default_rng(seed + 99)
    cx = float(rng.uniform(18, cfg.GRID_X - 18))
    cy = float(rng.uniform(18, cfg.GRID_Y - 18))
    sim = FieldSim(ablation)
    mass = cfg.C_TOTAL_MASS

    if geometry == "cluster":
        a, b, mid = pair_sites(seed, cfg.A_NEAR_SEP, cx, cy)
        sim.deposit(*a, mass / 2, 0)
        sim.deposit(*b, mass / 2, 0)
        y_true = 1
        readout = mid
    elif geometry == "dispersed":
        a, b, mid = pair_sites(seed, cfg.A_FAR_SEP, cx, cy)
        sim.deposit(*a, mass / 2, 0)
        sim.deposit(*b, mass / 2, 0)
        y_true = 0
        readout = mid
    elif geometry == "triangle":
        amp = mass / 3
        pts = [(cx + 1.5 * math.cos(2 * math.pi * k / 3),
                cy + 1.5 * math.sin(2 * math.pi * k / 3)) for k in range(3)]
        for p in pts:
            sim.deposit(p[0], p[1], amp, 0)
        y_true = 1
        readout = (cx, cy)
    else:  # line3
        amp = mass / 3
        for k, dx in enumerate((-6.0, 0.0, 6.0)):
            sim.deposit(cx + dx, cy, amp, 0)
        y_true = 0  # spread along line — should not latch centrally
        readout = (cx, cy)

    if not sim.evolve(cfg.C_EVOLVE):
        return {"seed": seed, "geometry": geometry, "ablation": ablation, "failed": True}
    y_pred = int(activated(sim, *readout))
    return {
        "seed": seed, "geometry": geometry, "ablation": ablation, "failed": False,
        "total_mass": mass, "y_true": y_true, "y_pred": y_pred,
        "correct": int(y_pred == y_true), "local_max": sim.local_max(*readout),
        "max_field": sim.stats()["max"],
    }


def run_C_suite(seeds: list[int]) -> dict[str, Any]:
    geos = ("cluster", "dispersed", "triangle", "line3")
    trials = []
    for seed in seeds:
        for abl in ("nonlinear_full", "linear_telegraph", "no_propagation"):
            for g in geos:
                trials.append(run_C_trial(seed, g, abl))
    return {
        "experiment": "C_spatial",
        "trials": trials,
        "summary": _cls_summary(trials, cases_key="geometry", group_key="ablation"),
    }


# ---------------------------------------------------------------------------
# D — Threshold integration / hysteresis
# ---------------------------------------------------------------------------

def run_D_amplitude_sweep(seed: int, ablation: str = "nonlinear_full") -> dict[str, Any]:
    """Single deposit amp sweep → activation curve."""
    rows = []
    cx, cy = 25.0, 25.0
    for amp in cfg.D_AMP_SWEEP:
        sim = FieldSim(ablation)
        sim.deposit(cx, cy, amp, 0)
        ok = sim.evolve(cfg.D_EVOLVE)
        if not ok:
            rows.append({"amp": amp, "failed": True})
            continue
        rows.append({
            "amp": amp, "failed": False,
            "activated": int(activated(sim, cx, cy)),
            "local_max": sim.local_max(cx, cy),
            "max_field": sim.stats()["max"],
        })
    return {"seed": seed, "ablation": ablation, "curve": rows}


def run_D_hysteresis(seed: int, ablation: str = "nonlinear_full") -> dict[str, Any]:
    """
    Forward: ramp amp via successive weak deposits until activation.
    Reverse: after activation, wait; then add negative perturbations; see if drops.
    """
    cx, cy = 25.0, 25.0
    sim = FieldSim(ablation)
    forward_amp = None
    cum = 0.0
    for step, amp in enumerate(np.linspace(0.05, 0.9, 18)):
        # fresh sim each forward point for clean threshold
        s2 = FieldSim(ablation)
        s2.deposit(cx, cy, float(amp), 0)
        if not s2.evolve(cfg.D_EVOLVE):
            continue
        if activated(s2, cx, cy):
            forward_amp = float(amp)
            break
    # Reverse: start from high state via strong deposit, then apply negative bumps
    sim = FieldSim(ablation)
    sim.deposit(cx, cy, 1.2, 0)
    sim.evolve(cfg.D_HOLD)
    still_high_before = activated(sim, cx, cy)
    reverse_drop_amp = None
    for neg in np.linspace(-0.1, -1.5, 15):
        s3 = FieldSim(ablation)
        s3.deposit(cx, cy, 1.2, 0)
        s3.evolve(cfg.D_HOLD)
        s3.deposit(cx, cy, float(neg), cfg.D_HOLD)
        s3.evolve(cfg.D_HOLD)
        if not activated(s3, cx, cy):
            reverse_drop_amp = float(abs(neg))
            break
    hyst = None
    if forward_amp is not None and reverse_drop_amp is not None:
        hyst = float(forward_amp)  # width proxy: activation threshold vs need for large negative
    return {
        "seed": seed, "ablation": ablation, "failed": False,
        "forward_activation_amp": forward_amp,
        "still_high_after_strong": int(still_high_before),
        "reverse_drop_neg_amp": reverse_drop_amp,
        "hysteresis_proxy": hyst,
    }


def run_D_suite(seeds: list[int]) -> dict[str, Any]:
    sweeps, hyst = [], []
    for seed in seeds:
        for abl in ("nonlinear_full", "linear_telegraph", "reaction_off"):
            sweeps.append(run_D_amplitude_sweep(seed, abl))
            hyst.append(run_D_hysteresis(seed, abl))
    # Aggregate forward threshold for nonlinear
    fwd = [h["forward_activation_amp"] for h in hyst
           if h.get("ablation") == "nonlinear_full" and h.get("forward_activation_amp") is not None]
    return {
        "experiment": "D_threshold_hysteresis",
        "sweeps": sweeps,
        "hysteresis": hyst,
        "nl_mean_forward_amp": float(np.mean(fwd)) if fwd else None,
        "nl_n_forward": len(fwd),
    }


# ---------------------------------------------------------------------------
# E — Conflict / interference
# ---------------------------------------------------------------------------

def run_E_trial(seed: int, mode: str, ablation: str = "nonlinear_full") -> dict[str, Any]:
    """
    Modes:
      agree: two positive near
      oppose: positive + negative at same site
      compete_spatial: two positives far apart
      noise: target + noise
    Predictable amplitude outcomes — not semantic categories.
    """
    rng = np.random.default_rng(seed + 3)
    sim = FieldSim(ablation)
    cx, cy = 25.0, 25.0
    if mode == "agree":
        a, b, mid = pair_sites(seed, cfg.A_NEAR_SEP, cx, cy)
        sim.deposit(*a, cfg.E_AMP, 0)
        sim.deposit(*b, cfg.E_AMP, 0)
        # expect activation
        expect_act = 1
        readout = mid
    elif mode == "oppose":
        sim.deposit(cx, cy, cfg.E_AMP, 0)
        sim.deposit(cx, cy, -cfg.E_AMP, 0)
        expect_act = 0  # cancel
        readout = (cx, cy)
    elif mode == "compete_spatial":
        sim.deposit(15.0, 25.0, cfg.E_AMP, 0)
        sim.deposit(35.0, 25.0, cfg.E_AMP, 0)
        expect_act = 0  # neither midpoint nor far should need AND; each alone may latch if E_AMP large
        # With E_AMP=0.5 single deposit often crosses — use subthreshold compete
        # Re-run with weaker: handled below by checking both sites
        readout = (25.0, 25.0)
        # redefine: expect midpoint not activated for far compete with sub amp
    elif mode == "noise":
        sim.deposit(cx, cy, 0.22, 0)
        for _ in range(6):
            sim.deposit(float(rng.uniform(5, 45)), float(rng.uniform(5, 45)), 0.08, 0)
        expect_act = 0  # single 0.22 often below latch alone
        readout = (cx, cy)
    else:
        expect_act = 0
        readout = (cx, cy)

    # Fix compete_spatial with subthreshold amps
    if mode == "compete_spatial":
        sim = FieldSim(ablation)
        sim.deposit(15.0, 25.0, cfg.A_SUB_AMP, 0)
        sim.deposit(35.0, 25.0, cfg.A_SUB_AMP, 0)
        expect_act = 0
        readout = (25.0, 25.0)

    if not sim.evolve(cfg.E_EVOLVE):
        return {"seed": seed, "mode": mode, "ablation": ablation, "failed": True}
    y_pred = int(activated(sim, *readout))
    raw_mid = float(sim.grid()[sim.grid().shape[0] // 2, sim.grid().shape[1] // 2])
    return {
        "seed": seed, "mode": mode, "ablation": ablation, "failed": False,
        "y_true": expect_act, "y_pred": y_pred, "correct": int(y_pred == expect_act),
        "local_max": sim.local_max(*readout), "max_field": sim.stats()["max"],
        "note": "scalar polarity; not multi-semantic",
    }


def run_E_suite(seeds: list[int]) -> dict[str, Any]:
    modes = ("agree", "oppose", "compete_spatial", "noise")
    trials = []
    for seed in seeds:
        for abl in ("nonlinear_full", "linear_telegraph"):
            for m in modes:
                trials.append(run_E_trial(seed, m, abl))
    return {
        "experiment": "E_conflict",
        "trials": trials,
        "summary": _cls_summary(trials, cases_key="mode", group_key="ablation"),
        "limitation": "Signed deposits cancel locally; not distinct semantic channels.",
    }


# ---------------------------------------------------------------------------
# F — Pattern completion / degradation
# ---------------------------------------------------------------------------

def run_F_trial(seed: int, mode: str, ablation: str = "nonlinear_full") -> dict[str, Any]:
    """
    Modes:
      full_template: strong deposit → high state
      partial_only: weak partial without prior template
      partial_after_template: establish high, damage with negative, partial restore
      amplify_control: same partial_only (alias for Category≤1 check)
    Genuine completion requires recovering info not in partial input via attractor.
    """
    rng = np.random.default_rng(seed + 11)
    cx, cy = 25.0, 25.0
    sim = FieldSim(ablation)
    if mode == "full_template":
        sim.deposit(cx, cy, cfg.F_TEMPLATE_AMP, 0)
        if not sim.evolve(cfg.F_EVOLVE):
            return {"seed": seed, "mode": mode, "failed": True}
        y_pred = int(activated(sim, cx, cy))
        y_true = 1
        recovered_extra = False
    elif mode == "partial_only":
        sim.deposit(cx, cy, cfg.F_TEMPLATE_AMP * cfg.F_PARTIAL_FRAC, 0)
        if not sim.evolve(cfg.F_EVOLVE):
            return {"seed": seed, "mode": mode, "failed": True}
        y_pred = int(activated(sim, cx, cy))
        y_true = 0  # partial alone should not complete to high if below threshold
        recovered_extra = False
    elif mode == "partial_after_template":
        # Establish attractor
        sim.deposit(cx, cy, cfg.F_TEMPLATE_AMP, 0)
        sim.evolve(30)
        high1 = activated(sim, cx, cy)
        # Damage
        sim.deposit(cx, cy, -0.8, 30)
        sim.evolve(20)
        mid_state = sim.local_max(cx, cy)
        # Partial restore (less than original)
        sim.deposit(cx, cy, cfg.F_TEMPLATE_AMP * cfg.F_PARTIAL_FRAC, 50)
        sim.evolve(30)
        y_pred = int(activated(sim, cx, cy))
        # Completion claim: returns to high after damage+partial, AND partial_only would not
        y_true = 1 if high1 else 0
        recovered_extra = bool(y_pred and mid_state < cfg.ACTIVATION_THRESH)
    else:
        return {"seed": seed, "mode": mode, "failed": True, "error": "unknown mode"}

    return {
        "seed": seed, "mode": mode, "ablation": ablation, "failed": False,
        "y_true": y_true, "y_pred": y_pred, "correct": int(y_pred == y_true),
        "local_max": sim.local_max(cx, cy),
        "recovered_extra": int(recovered_extra) if mode == "partial_after_template" else 0,
        "max_field": sim.stats()["max"],
    }


def run_F_suite(seeds: list[int]) -> dict[str, Any]:
    modes = ("full_template", "partial_only", "partial_after_template")
    trials = []
    for seed in seeds:
        for abl in ("nonlinear_full", "linear_telegraph"):
            for m in modes:
                trials.append(run_F_trial(seed, m, abl))
    # Completion evidence: partial_after recovers more than partial_only
    nl = [t for t in trials if t.get("ablation") == "nonlinear_full" and not t.get("failed")]
    po = [t for t in nl if t["mode"] == "partial_only"]
    pa = [t for t in nl if t["mode"] == "partial_after_template"]
    completion_lift = None
    if po and pa:
        completion_lift = float(np.mean([t["y_pred"] for t in pa]) - np.mean([t["y_pred"] for t in po]))
    return {
        "experiment": "F_pattern",
        "trials": trials,
        "completion_lift_nl": completion_lift,
        "summary": _cls_summary(trials, cases_key="mode", group_key="ablation"),
    }


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _binary_metrics(trials: list[dict]) -> dict[str, Any]:
    by_case: dict[str, list] = {}
    for t in trials:
        by_case.setdefault(t["case"], []).append(t)
    out = {}
    for case, sub in by_case.items():
        yt = [t["y_true"] for t in sub]
        yp = [t["y_pred"] for t in sub]
        tp = sum(1 for a, b in zip(yt, yp) if a == 1 and b == 1)
        fp = sum(1 for a, b in zip(yt, yp) if a == 0 and b == 1)
        fn = sum(1 for a, b in zip(yt, yp) if a == 1 and b == 0)
        tn = sum(1 for a, b in zip(yt, yp) if a == 0 and b == 0)
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        out[case] = {"n": len(sub), "tp": tp, "fp": fp, "fn": fn, "tn": tn,
                     "precision": prec, "recall": rec, "f1": f1,
                     "accuracy": float(np.mean([t["correct"] for t in sub]))}
    # Overall treating near/triple as positive cases present in list
    all_yt = [t["y_true"] for t in trials]
    all_yp = [t["y_pred"] for t in trials]
    tp = sum(1 for a, b in zip(all_yt, all_yp) if a == 1 and b == 1)
    fp = sum(1 for a, b in zip(all_yt, all_yp) if a == 0 and b == 1)
    fn = sum(1 for a, b in zip(all_yt, all_yp) if a == 1 and b == 0)
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    out["overall"] = {"precision": prec, "recall": rec, "f1": f1, "n": len(trials)}
    return out


def _cls_summary(trials, cases_key, group_key):
    out = {}
    for t in trials:
        if t.get("failed"):
            continue
        g = t[group_key]
        c = t[cases_key]
        out.setdefault(g, {}).setdefault(c, {"n": 0, "acc_sum": 0, "act_sum": 0})
        out[g][c]["n"] += 1
        out[g][c]["acc_sum"] += t.get("correct", 0)
        out[g][c]["act_sum"] += t.get("y_pred", 0)
    for g in out:
        for c in out[g]:
            n = out[g][c]["n"]
            out[g][c]["accuracy"] = out[g][c]["acc_sum"] / n if n else None
            out[g][c]["p_activate"] = out[g][c]["act_sum"] / n if n else None
            del out[g][c]["acc_sum"]
            del out[g][c]["act_sum"]
    return out
