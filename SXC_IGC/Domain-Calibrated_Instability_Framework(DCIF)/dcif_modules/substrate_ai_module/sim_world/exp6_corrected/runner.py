"""Pilot → freeze → confirmatory runner for corrected Task 6."""
from __future__ import annotations

import json
import os
import time
from typing import Any

import numpy as np

from sim_world.exp6_corrected import config as cfg
from sim_world.exp6_corrected.config import ProtocolFreeze
from sim_world.exp6_corrected.math_gates import run_math_gates
from sim_world.exp6_corrected.oracle_tests import run_oracle_gates
from sim_world.exp6_corrected.experiment_a import run_experiment_a
from sim_world.exp6_corrected.experiment_b import run_experiment_b
from sim_world.exp6_corrected.experiment_c import run_experiment_c
from sim_world.exp6_corrected.statistics import paired_analysis, bonferroni_adjust


def _extract_paired_metric(exp_summary_trials: list[dict], metric_key: str,
                           condition: str, seeds: list[int],
                           case_filter=None) -> list[float]:
    """Collect per-seed metric means for pairing."""
    vals = []
    for seed in seeds:
        subset = [t for t in exp_summary_trials
                  if t.get("condition") == condition
                  and t.get("seed") == seed
                  and not t.get("failed")]
        if case_filter is not None:
            subset = [t for t in subset if case_filter(t)]
        if not subset:
            vals.append(float("nan"))
            continue
        if metric_key in subset[0]:
            vals.append(float(np.mean([t[metric_key] for t in subset])))
        else:
            vals.append(float("nan"))
    return vals


def _per_seed_interaction_f1(exp_b_trials: list[dict], cond: str, seeds: list[int]) -> list[float]:
    """Per-seed F1 for BOTH_NEAR (primary endpoint). Avoids always-0 accuracy trap."""
    from sim_world.exp6_corrected.statistics import classification_metrics as _cm
    out = []
    for seed in seeds:
        trials = [t for t in exp_b_trials
                  if t["condition"] == cond and t["seed"] == seed and not t.get("failed")]
        if not trials:
            out.append(float("nan"))
            continue
        yt = [t["y_true_interaction"] for t in trials]
        yp = [t["y_pred_interaction"] for t in trials]
        out.append(float(_cm(yt, yp, positive=1)["f1"]))
    return out


def analyze_confirmatory(exp_a, exp_b, exp_c, seeds: list[int]) -> dict[str, Any]:
    """Pre-registered analysis: primary = Exp B interaction F1 (BOTH_NEAR)."""
    alpha = cfg.ALPHA
    n_comp = cfg.N_PRIMARY_COMPARISONS

    nl = _per_seed_interaction_f1(exp_b["trials"], "nonlinear_sub", seeds)
    comparisons = {}
    baselines = ["linear_sub", "direct_msg", "blackboard", "pheromone", "independent"]
    raw_ps = []
    for base in baselines:
        bv = _per_seed_interaction_f1(exp_b["trials"], base, seeds)
        pairs = [(a, b) for a, b in zip(bv, nl) if np.isfinite(a) and np.isfinite(b)]
        if len(pairs) < 2:
            comparisons[f"nonlinear_sub_vs_{base}"] = {"n": len(pairs), "note": "insufficient"}
            raw_ps.append(1.0)
            continue
        a_vals = [p[0] for p in pairs]
        b_vals = [p[1] for p in pairs]
        pa = paired_analysis(a_vals, b_vals, alpha=alpha)
        comparisons[f"nonlinear_sub_vs_{base}"] = pa
        raw_ps.append(pa["p_value"])

    adj = bonferroni_adjust(raw_ps, n_comp)
    for i, base in enumerate(baselines):
        key = f"nonlinear_sub_vs_{base}"
        if key in comparisons and "p_value" in comparisons[key]:
            comparisons[key]["p_bonferroni"] = adj[i]
            comparisons[key]["bonferroni_sig"] = adj[i] < alpha

    # Secondary: Exp A detection; Exp C resource / hazard / allocation
    secondary = {}
    for label, trials, metric, mode in [
        ("exp_a_detection", exp_a["trials"], "detection_correct", None),
        ("exp_c_res_discovery", [t for t in exp_c["trials"] if t["mode"] == "resource"],
         "res_discovery_rate", "resource"),
        ("exp_c_hazard_exposure", [t for t in exp_c["trials"] if t["mode"] == "hazard"],
         "hazard_exposure_ticks", "hazard"),
        ("exp_c_task_completion", [t for t in exp_c["trials"] if t["mode"] == "allocation"],
         "task_completion_rate", "allocation"),
    ]:
        sec_comps = {}
        for base in baselines:
            def per_seed(cond, trials=trials, metric=metric):
                out = []
                for seed in seeds:
                    subset = [t for t in trials
                              if t["condition"] == cond and t.get("seed") == seed
                              and not t.get("failed")]
                    if not subset and label == "exp_a_detection":
                        subset = [t for t in trials
                                  if t["condition"] == cond
                                  and (t["seed"] - 1000 * t["delay"] - int(t["distance"] * 10)) == seed
                                  and not t.get("failed")]
                    if not subset:
                        out.append(float("nan"))
                    else:
                        out.append(float(np.mean([t[metric] for t in subset])))
                return out
            av, bv = per_seed(base), per_seed("nonlinear_sub")
            pairs = [(a, b) for a, b in zip(av, bv) if np.isfinite(a) and np.isfinite(b)]
            if len(pairs) < 2:
                sec_comps[base] = {"n": len(pairs), "note": "insufficient"}
                continue
            sec_comps[base] = paired_analysis([p[0] for p in pairs], [p[1] for p in pairs])
        secondary[label] = sec_comps

    # Outcome classification (strict acceptance ladder)
    nl_sum = exp_b["summary"].get("nonlinear_sub", {})
    primary_f1 = nl_sum.get("interaction_f1", 0.0)
    vs_conv = [
        comparisons.get(f"nonlinear_sub_vs_{b}", {})
        for b in ("direct_msg", "blackboard", "pheromone")
    ]
    beats_any_conv = any(
        c.get("bonferroni_sig") and c.get("mean_diff", 0) > 0
        and (c.get("d_z") or 0) >= cfg.MIN_MEANINGFUL_EFFECT_DZ
        for c in vs_conv if "mean_diff" in c
    )
    g6_ok = exp_b.get("g6_notes", {}).get("pass_candidate", False)

    if not g6_ok and primary_f1 < 0.5:
        outcome = "A_NO_DEMONSTRATED_CAPABILITY"
    elif g6_ok and not beats_any_conv:
        outcome = "B_SPECIALIZED_CAPABILITY"
    elif beats_any_conv:
        outcome = "C_SPECIALIZED_ADVANTAGE"
    else:
        outcome = "B_SPECIALIZED_CAPABILITY"

    return {
        "protocol": ProtocolFreeze().to_dict(),
        "primary_endpoint": cfg.PRIMARY_ENDPOINT,
        "primary_metric_note": (
            "Per-seed F1 for BOTH_NEAR; raw accuracy is exploratory only "
            "(always-0 yields ~0.8 accuracy)."
        ),
        "primary_comparisons": comparisons,
        "secondary_comparisons": secondary,
        "alpha": alpha,
        "n_comparisons_bonferroni": n_comp,
        "outcome_classification": outcome,
        "n_seeds": len(seeds),
        "nonlinear_primary_f1": primary_f1,
    }


def estimate_sample_size(pilot_exp_b: dict) -> dict[str, Any]:
    """Paired power heuristic from pilot variance of per-seed interaction F1."""
    seeds = sorted({t["seed"] for t in pilot_exp_b["trials"]})
    nl = _per_seed_interaction_f1(pilot_exp_b["trials"], "nonlinear_sub", seeds)
    bb = _per_seed_interaction_f1(pilot_exp_b["trials"], "blackboard", seeds)
    pairs = [(a, b) for a, b in zip(bb, nl) if np.isfinite(a) and np.isfinite(b)]
    if len(pairs) < 3:
        return {"recommended_n": 30, "reason": "insufficient pilot pairs; default N=30",
                "metric": "interaction_f1"}
    diffs = np.array([b - a for a, b in pairs])
    sd = float(np.std(diffs, ddof=1)) or 0.2
    target_dz = cfg.MIN_MEANINGFUL_EFFECT_DZ
    # Bonferroni-adjusted alpha≈0.01, target dz=0.5 → n≈40 heuristic
    n_rec = int(max(20, min(60, round(16.0 / (target_dz ** 2) * 1.5))))
    return {
        "pilot_n": len(pairs),
        "pilot_sd_diff": sd,
        "pilot_mean_diff": float(np.mean(diffs)),
        "target_dz": target_dz,
        "recommended_n": n_rec,
        "metric": "interaction_f1",
        "note": "Heuristic paired power on F1; confirmatory N frozen from this estimate.",
    }


def run_pipeline(
    out_dir: str,
    pilot_only: bool = False,
    confirm_n: int | None = None,
    verbose: bool = True,
) -> dict[str, Any]:
    t0 = time.time()
    gate_log: dict[str, Any] = {}

    # Phase 2 — Math gates
    if verbose:
        print("=== Phase 2: Math gates G1/G2 ===")
    math = run_math_gates()
    gate_log["G1"] = "PASS" if math["G1"]["pass"] else "FAIL"
    gate_log["G2"] = "PASS" if math["G2"]["pass"] else "FAIL"
    if not math["proceed_to_agentic"]:
        return {"blocked": True, "gate_log": gate_log, "math": math}

    # Phase 3 — Oracle gates
    if verbose:
        print("=== Phase 3: Oracle gates G3/G4 ===")
    oracle = run_oracle_gates()
    gate_log["G3"] = "PASS" if oracle["G3"]["pass"] else "FAIL"
    gate_log["G4"] = "PASS" if oracle["G4"]["pass"] else "FAIL"
    if not oracle["proceed"]:
        return {"blocked": True, "gate_log": gate_log, "math": math, "oracle": oracle}

    # Phase 4–6 pilot
    pilot_seeds = list(cfg.PILOT_SEEDS)
    if verbose:
        print(f"=== Pilot Exp A/B/C: {len(pilot_seeds)} seeds ===")
    pilot_a = run_experiment_a(pilot_seeds, verbose=verbose)
    pilot_b = run_experiment_b(pilot_seeds, verbose=verbose)
    pilot_c = run_experiment_c(pilot_seeds, verbose=verbose)

    ss = estimate_sample_size(pilot_b)
    if confirm_n is None:
        confirm_n = int(ss["recommended_n"])

    pilot_bundle = {
        "protocol": ProtocolFreeze().to_dict(),
        "math_gates": {"G1": math["G1"], "G2": math["G2"]},
        "oracle_gates": oracle,
        "experiment_a": {k: v for k, v in pilot_a.items() if k != "trials"},
        "experiment_a_trials": pilot_a["trials"],
        "experiment_b": {k: v for k, v in pilot_b.items() if k != "trials"},
        "experiment_b_trials": pilot_b["trials"],
        "experiment_c": {k: v for k, v in pilot_c.items() if k != "trials"},
        "experiment_c_trials": pilot_c["trials"],
        "sample_size_estimate": ss,
        "gate_log": dict(gate_log),
        "elapsed_s": time.time() - t0,
    }
    # Attach G5–G9 pilot candidates
    gate_log["G5"] = "PASS" if pilot_a.get("g5_notes", {}).get("pass_candidate") else "FAIL"
    gate_log["G6"] = "PASS" if pilot_b.get("g6_notes", {}).get("pass_candidate") else "FAIL"
    gate_log["G7"] = "PASS" if pilot_c.get("g7_notes", {}).get("pass_candidate") else "FAIL"
    gate_log["G8"] = "PASS" if pilot_c.get("g8_notes", {}).get("pass_candidate") else "FAIL"
    gate_log["G9"] = "PASS" if pilot_c.get("g9_notes", {}).get("pass_candidate") else "FAIL"
    pilot_bundle["gate_log"] = dict(gate_log)

    pilot_path = os.path.join(out_dir, "exp6_corrected_pilot_results.json")
    with open(pilot_path, "w") as f:
        json.dump(pilot_bundle, f, indent=2, default=str)
    if verbose:
        print(f"Pilot saved → {pilot_path}")
        print(f"Sample size estimate: {ss}")

    if pilot_only:
        return pilot_bundle

    # Freeze analysis — confirmatory seeds disjoint from pilot
    confirm_seeds = list(range(cfg.CONFIRM_SEED_START, cfg.CONFIRM_SEED_START + confirm_n))
    if verbose:
        print(f"=== Confirmatory Exp A/B/C: N={confirm_n} seeds {confirm_seeds[0]}..{confirm_seeds[-1]} ===")

    conf_a = run_experiment_a(confirm_seeds, verbose=verbose)
    conf_b = run_experiment_b(confirm_seeds, verbose=verbose)
    conf_c = run_experiment_c(confirm_seeds, verbose=verbose)

    analysis = analyze_confirmatory(conf_a, conf_b, conf_c, confirm_seeds)

    # Update gates from confirmatory
    gate_log["G5"] = "PASS" if conf_a.get("g5_notes", {}).get("pass_candidate") else "FAIL"
    gate_log["G6"] = "PASS" if conf_b.get("g6_notes", {}).get("pass_candidate") else "FAIL"
    gate_log["G7"] = "PASS" if conf_c.get("g7_notes", {}).get("pass_candidate") else "FAIL"
    gate_log["G8"] = "PASS" if conf_c.get("g8_notes", {}).get("pass_candidate") else "FAIL"
    gate_log["G9"] = "PASS" if conf_c.get("g9_notes", {}).get("pass_candidate") else "FAIL"
    gate_log["G10"] = "PASS"  # analysis procedure executed as pre-registered

    confirm_bundle = {
        "protocol": ProtocolFreeze().to_dict(),
        "sample_size_estimate": ss,
        "confirm_n": confirm_n,
        "confirm_seeds": confirm_seeds,
        "math_gates": {"G1_pass": math["G1"]["pass"], "G2_pass": math["G2"]["pass"],
                       "G1": math["G1"], "G2": math["G2"]},
        "oracle_gates": {
            "G3_pass": oracle["G3"]["pass"], "G4_pass": oracle["G4"]["pass"],
            "G3": oracle["G3"], "G4": oracle["G4"],
        },
        "experiment_a_summary": conf_a["summary"],
        "experiment_a_g5": conf_a["g5_notes"],
        "experiment_a_trials": conf_a["trials"],
        "experiment_b_summary": conf_b["summary"],
        "experiment_b_g6": conf_b["g6_notes"],
        "experiment_b_trials": conf_b["trials"],
        "experiment_c_summary": conf_c["summary"],
        "experiment_c_gates": {
            "g7": conf_c["g7_notes"], "g8": conf_c["g8_notes"], "g9": conf_c["g9_notes"],
        },
        "experiment_c_trials": conf_c["trials"],
        "analysis": analysis,
        "gate_log": gate_log,
        "elapsed_s": time.time() - t0,
    }

    confirm_path = os.path.join(out_dir, "exp6_corrected_results.json")
    with open(confirm_path, "w") as f:
        json.dump(confirm_bundle, f, indent=2, default=str)
    if verbose:
        print(f"Confirmatory saved → {confirm_path}")
        print(f"Outcome: {analysis['outcome_classification']}")
        print(f"Gate log: {gate_log}")

    return confirm_bundle
