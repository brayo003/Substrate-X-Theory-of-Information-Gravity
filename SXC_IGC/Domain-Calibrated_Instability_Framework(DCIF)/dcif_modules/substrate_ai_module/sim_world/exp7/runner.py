"""Pilot → freeze → confirmatory for Task 7 Tracks A and B."""
from __future__ import annotations

import json
import os
import time
from typing import Any

import numpy as np

from sim_world.exp7 import config as cfg
from sim_world.exp7.config import Exp7ProtocolFreeze
from sim_world.exp7.integrity import run_t1_t2
from sim_world.exp7.hazard_behaviour import run_track_a
from sim_world.exp7.collective_computation import run_track_b
from sim_world.exp6_corrected.statistics import paired_analysis, bonferroni_adjust


def _per_seed_exposure(trials, cond, mode, seeds):
    out = []
    for s in seeds:
        sub = [t for t in trials
               if t["condition"] == cond and t["info_mode"] == mode
               and t["seed"] == s and not t.get("failed")]
        out.append(float(sub[0]["hazard_exposure_ticks"]) if sub else float("nan"))
    return out


def _per_seed_and_f1(trials, cond, seeds):
    from sim_world.exp6_corrected.statistics import classification_metrics
    out = []
    for s in seeds:
        sub = [t for t in trials
               if t["condition"] == cond and t["seed"] == s and not t.get("failed")]
        if not sub:
            out.append(float("nan"))
            continue
        yt = [t["y_true"] for t in sub]
        yp = [t["y_pred"] for t in sub]
        out.append(float(classification_metrics(yt, yp, positive=1)["f1"]))
    return out


def analyze(track_a, track_b, seeds: list[int]) -> dict[str, Any]:
    alpha = cfg.ALPHA

    # Track A primary: nonlinear informed (C_immediate) vs A_no_discovery exposure
    exp_info = _per_seed_exposure(track_a["trials"], "nonlinear_sub", "C_immediate", seeds)
    exp_none = _per_seed_exposure(track_a["trials"], "nonlinear_sub", "A_no_discovery", seeds)
    pairs = [(a, b) for a, b in zip(exp_none, exp_info) if np.isfinite(a) and np.isfinite(b)]
    track_a_primary = {}
    if len(pairs) >= 2:
        # paired_analysis(a,b) → b−a; a=informed, b=none → positive = exposure reduction
        track_a_primary["nonlinear_exposure_reduction"] = paired_analysis(
            [p[1] for p in pairs],  # informed
            [p[0] for p in pairs],  # no-info
            alpha=alpha,
        )

    # Cross-architecture exposure reduction for C_immediate
    track_a_by_arch = {}
    for cond in cfg.CONDITIONS:
        ei = _per_seed_exposure(track_a["trials"], cond, "C_immediate", seeds)
        en = _per_seed_exposure(track_a["trials"], cond, "A_no_discovery", seeds)
        pairs = [(a, b) for a, b in zip(en, ei) if np.isfinite(a) and np.isfinite(b)]
        if len(pairs) >= 2:
            track_a_by_arch[cond] = paired_analysis(
                [p[1] for p in pairs], [p[0] for p in pairs], alpha=alpha
            )

    # Track B primary: nonlinear F1 vs baselines
    nl = _per_seed_and_f1(track_b["and_trials"], "nonlinear_sub", seeds)
    comps = {}
    raw_ps = []
    baselines = ["linear_sub", "direct_msg", "blackboard", "pheromone", "independent"]
    for base in baselines:
        bv = _per_seed_and_f1(track_b["and_trials"], base, seeds)
        pairs = [(a, b) for a, b in zip(bv, nl) if np.isfinite(a) and np.isfinite(b)]
        if len(pairs) < 2:
            comps[f"nl_vs_{base}"] = {"n": len(pairs), "note": "insufficient"}
            raw_ps.append(1.0)
            continue
        pa = paired_analysis([p[0] for p in pairs], [p[1] for p in pairs], alpha=alpha)
        comps[f"nl_vs_{base}"] = pa
        raw_ps.append(pa["p_value"])
    adj = bonferroni_adjust(raw_ps, cfg.N_TRACK_B_PRIMARY_COMPS)
    for i, base in enumerate(baselines):
        k = f"nl_vs_{base}"
        if "p_value" in comps.get(k, {}):
            comps[k]["p_bonferroni"] = adj[i]
            comps[k]["bonferroni_sig"] = adj[i] < alpha

    # Outcome classification
    t_pass = {
        "T1": True, "T2": True,  # filled by caller
        "T3": track_a["T3"]["pass"],
        "T4": track_a["T4"]["pass"],
        "T5": track_a["T5"]["pass"],
        "T6": track_a["T6"]["pass"],
        "T7": track_b["T7"]["pass"],
        "T8": track_b["T8"]["pass"],
        "T9": track_b["T9"]["pass"],
    }
    behav = t_pass["T3"] and t_pass["T4"] and t_pass["T5"]
    persist = behav and t_pass["T6"]
    nl_comp = t_pass["T7"] and t_pass["T8"]
    adv = nl_comp and t_pass["T9"]

    if adv and persist:
        outcome = "D_COMPARATIVE_ADVANTAGE"
    elif behav and nl_comp:
        outcome = "C_BOTH_CAPABILITIES"
    elif nl_comp and not behav:
        outcome = "B_NONLINEAR_COMPUTATION_WITHOUT_BEHAVIOUR"
    elif behav and not nl_comp:
        outcome = "A_BEHAVIOURAL_UTILITY_WITHOUT_NONLINEAR_SPECIFIC"
    else:
        outcome = "E_NO_NEW_CAPABILITY"

    level = 0
    if behav:
        level = 1
    if persist:
        level = 2
    if nl_comp and t_pass["T1"] and t_pass["T2"]:
        level = max(level, 3)
    if adv:
        level = 4

    return {
        "protocol": Exp7ProtocolFreeze().to_dict(),
        "track_a_primary": track_a_primary,
        "track_a_by_architecture": track_a_by_arch,
        "track_b_primary_comparisons": comps,
        "gates": t_pass,
        "outcome": outcome,
        "acceptance_level": level,
        "n_seeds": len(seeds),
    }


def estimate_n(pilot_b: dict) -> dict[str, Any]:
    seeds = sorted({t["seed"] for t in pilot_b["and_trials"]})
    nl = _per_seed_and_f1(pilot_b["and_trials"], "nonlinear_sub", seeds)
    lin = _per_seed_and_f1(pilot_b["and_trials"], "linear_sub", seeds)
    pairs = [(a, b) for a, b in zip(lin, nl) if np.isfinite(a) and np.isfinite(b)]
    if len(pairs) < 3:
        return {"recommended_n": 40, "reason": "default"}
    diffs = np.array([b - a for a, b in pairs])
    sd = float(np.std(diffs, ddof=1)) or 0.25
    n_rec = int(max(20, min(50, round(16.0 / (cfg.MIN_MEANINGFUL_EFFECT_DZ ** 2) * 1.5))))
    return {
        "pilot_n": len(pairs),
        "pilot_mean_diff": float(np.mean(diffs)),
        "pilot_sd_diff": sd,
        "recommended_n": n_rec,
        "metric": "and_gate_f1",
    }


def run_pipeline(out_dir: str, pilot_only: bool = False,
                 confirm_n: int | None = None, verbose: bool = True) -> dict[str, Any]:
    t0 = time.time()
    if verbose:
        print("=== T1/T2 integrity ===")
    integ = run_t1_t2()
    if not integ["proceed"]:
        return {"blocked": True, "integrity": integ}

    pilot_seeds = list(cfg.PILOT_SEEDS)
    if verbose:
        print(f"=== Pilot Track A/B seeds={pilot_seeds} ===")
    pilot_a = run_track_a(pilot_seeds, verbose=verbose)
    pilot_b = run_track_b(pilot_seeds, verbose=verbose)
    ss = estimate_n(pilot_b)

    # Pilot difficulty check for AND amp
    nl_f1 = pilot_b["and_summary"].get("nonlinear_sub", {}).get("f1", 0)
    lin_f1 = pilot_b["and_summary"].get("linear_sub", {}).get("f1", 0)
    pilot_notes = {
        "nonlinear_and_f1": nl_f1,
        "linear_and_f1": lin_f1,
        "ceiling_risk": nl_f1 >= 0.99 and lin_f1 >= 0.99,
        "floor_risk": nl_f1 < 0.1,
        "discriminates_nl_vs_lin": nl_f1 > lin_f1 + 0.15,
        "amp": cfg.AND_SUB_AMP,
    }

    gate_log = {
        "T1": "PASS" if integ["T1"]["pass"] else "FAIL",
        "T2": "PASS" if integ["T2"]["pass"] else "FAIL",
        "T3": "PASS" if pilot_a["T3"]["pass"] else "FAIL",
        "T4": "PASS" if pilot_a["T4"]["pass"] else "FAIL",
        "T5": "PASS" if pilot_a["T5"]["pass"] else "FAIL",
        "T6": "PASS" if pilot_a["T6"]["pass"] else "FAIL",
        "T7": "PASS" if pilot_b["T7"]["pass"] else "FAIL",
        "T8": "PASS" if pilot_b["T8"]["pass"] else "FAIL",
        "T9": "PASS" if pilot_b["T9"]["pass"] else "FAIL",
    }

    pilot_bundle = {
        "protocol": Exp7ProtocolFreeze().to_dict(),
        "integrity": integ,
        "track_a": {k: v for k, v in pilot_a.items() if k != "trials"},
        "track_a_trials": pilot_a["trials"],
        "track_b": {k: v for k, v in pilot_b.items()
                    if k not in ("and_trials", "ablation_trials", "secondary_trials")},
        "track_b_and_trials": pilot_b["and_trials"],
        "track_b_ablation_trials": pilot_b["ablation_trials"],
        "sample_size_estimate": ss,
        "pilot_notes": pilot_notes,
        "gate_log": gate_log,
        "elapsed_s": time.time() - t0,
        "exploratory": True,
    }
    pilot_path = os.path.join(out_dir, "exp7_pilot_results.json")
    with open(pilot_path, "w") as f:
        json.dump(pilot_bundle, f, indent=2, default=str)
    if verbose:
        print(f"Pilot → {pilot_path}")
        print("Pilot notes:", pilot_notes)
        print("Pilot gates:", gate_log)

    if pilot_only:
        return pilot_bundle

    if confirm_n is None:
        confirm_n = int(ss["recommended_n"])
    confirm_seeds = list(range(cfg.CONFIRM_SEED_START, cfg.CONFIRM_SEED_START + confirm_n))

    # Freeze config snapshot
    freeze_path = os.path.join(out_dir, "exp7_configuration.json")
    with open(freeze_path, "w") as f:
        json.dump({
            "frozen_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "protocol": Exp7ProtocolFreeze().to_dict(),
            "confirm_n": confirm_n,
            "confirm_seeds": confirm_seeds,
            "pilot_notes": pilot_notes,
            "primary_endpoints": {
                "track_a": cfg.TRACK_A_PRIMARY,
                "track_b": cfg.TRACK_B_PRIMARY,
            },
            "note": "No retuning after confirmatory inspection.",
        }, f, indent=2)

    if verbose:
        print(f"=== Confirmatory N={confirm_n} seeds {confirm_seeds[0]}..{confirm_seeds[-1]} ===")
    conf_a = run_track_a(confirm_seeds, verbose=verbose)
    conf_b = run_track_b(confirm_seeds, verbose=verbose)
    analysis = analyze(conf_a, conf_b, confirm_seeds)
    analysis["gates"]["T1"] = integ["T1"]["pass"]
    analysis["gates"]["T2"] = integ["T2"]["pass"]

    gate_log = {
        "T1": "PASS" if integ["T1"]["pass"] else "FAIL",
        "T2": "PASS" if integ["T2"]["pass"] else "FAIL",
        "T3": "PASS" if conf_a["T3"]["pass"] else "FAIL",
        "T4": "PASS" if conf_a["T4"]["pass"] else "FAIL",
        "T5": "PASS" if conf_a["T5"]["pass"] else "FAIL",
        "T6": "PASS" if conf_a["T6"]["pass"] else "FAIL",
        "T7": "PASS" if conf_b["T7"]["pass"] else "FAIL",
        "T8": "PASS" if conf_b["T8"]["pass"] else "FAIL",
        "T9": "PASS" if conf_b["T9"]["pass"] else "FAIL",
    }
    analysis["gate_log"] = gate_log

    # Recompute outcome with T1/T2
    analysis["gates"] = {**analysis["gates"], **{
        "T3": conf_a["T3"]["pass"], "T4": conf_a["T4"]["pass"],
        "T5": conf_a["T5"]["pass"], "T6": conf_a["T6"]["pass"],
        "T7": conf_b["T7"]["pass"], "T8": conf_b["T8"]["pass"],
        "T9": conf_b["T9"]["pass"],
    }}
    # Refresh outcome with full gates
    g = analysis["gates"]
    behav = g["T3"] and g["T4"] and g["T5"]
    persist = behav and g["T6"]
    nl_comp = g["T7"] and g["T8"]
    adv = nl_comp and g["T9"]
    if adv and persist:
        outcome = "D_COMPARATIVE_ADVANTAGE"
    elif behav and nl_comp:
        outcome = "C_BOTH_CAPABILITIES"
    elif nl_comp and not behav:
        outcome = "B_NONLINEAR_COMPUTATION_WITHOUT_BEHAVIOUR"
    elif behav and not nl_comp:
        outcome = "A_BEHAVIOURAL_UTILITY_WITHOUT_NONLINEAR_SPECIFIC"
    else:
        outcome = "E_NO_NEW_CAPABILITY"
    level = 0
    if behav:
        level = 1
    if persist:
        level = 2
    if nl_comp:
        level = max(level, 3)
    if adv:
        level = 4
    analysis["outcome"] = outcome
    analysis["acceptance_level"] = level

    confirm_bundle = {
        "protocol": Exp7ProtocolFreeze().to_dict(),
        "integrity": integ,
        "sample_size_estimate": ss,
        "confirm_n": confirm_n,
        "confirm_seeds": confirm_seeds,
        "track_a_summary": conf_a["summary"],
        "track_a_gates": {k: conf_a[k] for k in ("T3", "T4", "T5", "T6")},
        "track_a_gates_by_condition": conf_a["gates_by_condition"],
        "track_a_trials": conf_a["trials"],
        "track_b_and_summary": conf_b["and_summary"],
        "track_b_ablation_summary": conf_b["ablation_summary"],
        "track_b_secondary_summary": conf_b["secondary_summary"],
        "track_b_gates": {k: conf_b[k] for k in ("T7", "T8", "T9")},
        "track_b_and_trials": conf_b["and_trials"],
        "track_b_ablation_trials": conf_b["ablation_trials"],
        "analysis": analysis,
        "gate_log": gate_log,
        "elapsed_s": time.time() - t0,
    }
    out_path = os.path.join(out_dir, "exp7_results.json")
    with open(out_path, "w") as f:
        json.dump(confirm_bundle, f, indent=2, default=str)
    if verbose:
        print(f"Confirmatory → {out_path}")
        print("Outcome:", outcome, "Level:", level)
        print("Gates:", gate_log)
    return confirm_bundle
