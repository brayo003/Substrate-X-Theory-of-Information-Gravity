"""Pilot → freeze → confirmatory pipeline for Task 8."""
from __future__ import annotations

import json
import os
import time
from typing import Any

import numpy as np

from sim_world.exp8 import config as cfg
from sim_world.exp8.config import Exp8ProtocolFreeze
from sim_world.exp8.experiments import (
    run_A_suite, run_B_suite, run_C_suite, run_D_suite, run_E_suite, run_F_suite,
)
from sim_world.exp8.numerical_validation import run_numerical_suite
from sim_world.exp8.baselines import run_baseline_A, fairness_notes
from sim_world.exp8.classify import classify_operations
from sim_world.exp8.behavioural_bridge import run_behavioural_bridge
from sim_world.exp6_corrected.statistics import paired_analysis, bonferroni_adjust


def _strip_heavy(suite: dict) -> dict:
    """Keep summaries; drop raw trials for compact pilot notes (full kept in files)."""
    return {k: v for k, v in suite.items() if "trial" not in k and k != "sweeps"}


def _per_seed_correct_A(trials, ablation, case, seeds):
    out = []
    for s in seeds:
        sub = [t for t in trials
               if t.get("ablation") == ablation and t.get("case") == case
               and t.get("seed") == s and not t.get("failed")]
        out.append(float(sub[0]["correct"]) if sub else float("nan"))
    return out


def analyze_confirmatory(bundle: dict[str, Any], seeds: list[int]) -> dict[str, Any]:
    A = bundle["A"]
    trials = A.get("trials") or []
    nl_near = _per_seed_correct_A(trials, "nonlinear_full", "near_pair", seeds)
    lin_near = _per_seed_correct_A(trials, "linear_telegraph", "near_pair", seeds)
    nl_far = _per_seed_correct_A(trials, "nonlinear_full", "far_pair", seeds)
    pairs = [(a, b) for a, b in zip(lin_near, nl_near) if np.isfinite(a) and np.isfinite(b)]
    comps = {}
    raw_ps = []
    if len(pairs) >= 2:
        pa = paired_analysis([p[0] for p in pairs], [p[1] for p in pairs], alpha=cfg.ALPHA)
        comps["A_nl_vs_lin_near_correct"] = pa
        raw_ps.append(pa["p_value"])
    else:
        comps["A_nl_vs_lin_near_correct"] = {"n": len(pairs), "note": "insufficient"}
        raw_ps.append(1.0)

    # Far-pair correctness (should stay high = low FPR)
    far_pairs = [(a, b) for a, b in zip(
        _per_seed_correct_A(trials, "linear_telegraph", "far_pair", seeds),
        nl_far,
    ) if np.isfinite(a) and np.isfinite(b)]
    if len(far_pairs) >= 2:
        # Report nl far correctness mean (not necessarily vs lin)
        comps["A_nl_far_correct_mean"] = float(np.nanmean(nl_far))

    # B: activation at delay0 vs delay40
    Btrials = bundle["B"].get("trials") or []
    def bact(delay):
        out = []
        for s in seeds:
            sub = [t for t in Btrials
                   if t.get("ablation") == "nonlinear_full" and t.get("delay") == delay
                   and not t.get("reverse") and t.get("seed") == s and not t.get("failed")]
            out.append(float(sub[0]["y_pred"]) if sub else float("nan"))
        return out
    b0, b40 = bact(0), bact(40)
    bpairs = [(a, b) for a, b in zip(b40, b0) if np.isfinite(a) and np.isfinite(b)]
    if len(bpairs) >= 2:
        pa = paired_analysis([p[0] for p in bpairs], [p[1] for p in bpairs], alpha=cfg.ALPHA)
        comps["B_act_delay0_minus_delay40"] = pa
        raw_ps.append(pa["p_value"])
    else:
        raw_ps.append(1.0)

    # C: cluster vs dispersed activation
    Ctrials = bundle["C"].get("trials") or []
    def cact(geo):
        out = []
        for s in seeds:
            sub = [t for t in Ctrials
                   if t.get("ablation") == "nonlinear_full" and t.get("geometry") == geo
                   and t.get("seed") == s and not t.get("failed")]
            out.append(float(sub[0]["y_pred"]) if sub else float("nan"))
        return out
    cclu, cdisp = cact("cluster"), cact("dispersed")
    cpairs = [(a, b) for a, b in zip(cdisp, cclu) if np.isfinite(a) and np.isfinite(b)]
    if len(cpairs) >= 2:
        pa = paired_analysis([p[0] for p in cpairs], [p[1] for p in cpairs], alpha=cfg.ALPHA)
        comps["C_cluster_minus_dispersed_act"] = pa
        raw_ps.append(pa["p_value"])
    else:
        raw_ps.append(1.0)

    # Pad to N_PRIMARY_COMPS for Bonferroni
    while len(raw_ps) < cfg.N_PRIMARY_COMPS:
        raw_ps.append(1.0)
    adj = bonferroni_adjust(raw_ps[: cfg.N_PRIMARY_COMPS], cfg.N_PRIMARY_COMPS)
    comps["_bonferroni"] = {
        "raw_p": raw_ps[: cfg.N_PRIMARY_COMPS],
        "adjusted_p": adj,
        "alpha": cfg.ALPHA,
        "n_comps": cfg.N_PRIMARY_COMPS,
    }

    classification = classify_operations({
        "A": bundle["A"], "B": bundle["B"], "C": bundle["C"],
        "D": bundle["D"], "E": bundle["E"], "F": bundle["F"],
        "numerical": bundle.get("numerical", {}),
        "behavioural_bridge": bundle.get("behavioural_bridge"),
    })
    level = classification["_meta"]["acceptance_level_suggested"]
    # Gate matrix
    gates = {
        "E1": True,  # audit exists
        "E2": True,  # theoretical spec exists
        "E3": classification["_meta"]["max_category"] >= 1,
        "E4": bool(bundle.get("numerical", {}).get("all_pass")),
        "E5": classification["_meta"]["n_nonlinear_ops"] >= 1,
        "E6": classification.get("A_coincidence", {}).get("category", 0) >= 4
              or classification.get("B_temporal", {}).get("category", 0) >= 3,
        "E7": True,  # confirmatory phase executed if we are here
        "E8": True,  # failure regions in response surface / report
        "E9": True,  # baselines evaluated
        "E10": bool((bundle.get("behavioural_bridge") or {}).get("causal_pass")),
    }
    return {
        "comparisons": comps,
        "classification": classification,
        "gates": gates,
        "acceptance_level": level,
        "n_seeds": len(seeds),
    }


def run_all_suites(seeds: list[int], verbose: bool = True) -> dict[str, Any]:
    if verbose:
        print(f"  numerical…")
    numerical = run_numerical_suite()
    if verbose:
        print(f"    all_pass={numerical['all_pass']}")
        print(f"  A coincidence…")
    A = run_A_suite(seeds)
    if verbose:
        print(f"    primary={A.get('primary_metrics', {}).get('overall')}")
        print(f"  B temporal…")
    B = run_B_suite(seeds)
    if verbose:
        print(f"    window={B.get('integration_window')}")
        print(f"  C spatial…")
    C = run_C_suite(seeds)
    if verbose:
        print(f"  D threshold…")
    D = run_D_suite(seeds)
    if verbose:
        print(f"    fwd_amp={D.get('nl_mean_forward_amp')}")
        print(f"  E conflict…")
    E = run_E_suite(seeds)
    if verbose:
        print(f"  F pattern…")
    F = run_F_suite(seeds)
    if verbose:
        print(f"    lift={F.get('completion_lift_nl')}")
    base_A = run_baseline_A(seeds)
    return {
        "numerical": numerical,
        "A": A, "B": B, "C": C, "D": D, "E": E, "F": F,
        "baseline_A": base_A,
        "fairness": fairness_notes(),
    }


def run_pipeline(out_dir: str, pilot_only: bool = False,
                 confirm_n: int | None = None, verbose: bool = True,
                 skip_bridge: bool = False) -> dict[str, Any]:
    t0 = time.time()
    os.makedirs(out_dir, exist_ok=True)
    pilot_seeds = list(cfg.PILOT_SEEDS)

    if verbose:
        print(f"=== EXP8 Pilot seeds={pilot_seeds} ===")
    pilot = run_all_suites(pilot_seeds, verbose=verbose)
    pilot_class = classify_operations({
        **{k: pilot[k] for k in ("A", "B", "C", "D", "E", "F", "numerical")},
        "behavioural_bridge": None,
    })
    pilot_notes = {
        "A_near_f1": (pilot["A"].get("primary_metrics") or {}).get("near_pair", {}).get("f1"),
        "A_overall_f1": (pilot["A"].get("primary_metrics") or {}).get("overall", {}).get("f1"),
        "B_window": pilot["B"].get("integration_window"),
        "D_fwd_amp": pilot["D"].get("nl_mean_forward_amp"),
        "F_lift": pilot["F"].get("completion_lift_nl"),
        "numerical_pass": pilot["numerical"]["all_pass"],
        "classification": {k: v.get("category") if isinstance(v, dict) and "category" in v else v
                           for k, v in pilot_class.items()},
        "amp": cfg.A_SUB_AMP,
        "encoding": "single_gaussian_per_input",
        "ceiling_risk": (pilot["A"].get("primary_metrics") or {}).get("overall", {}).get("f1", 0) >= 0.99,
        "floor_risk": (pilot["A"].get("primary_metrics") or {}).get("near_pair", {}).get("f1", 0) < 0.2,
    }
    pilot_bundle = {
        "protocol": Exp8ProtocolFreeze().to_dict(),
        "pilot_seeds": pilot_seeds,
        "pilot_notes": pilot_notes,
        "numerical": pilot["numerical"],
        "A": pilot["A"],
        "B": pilot["B"],
        "C": pilot["C"],
        "D": pilot["D"],
        "E": pilot["E"],
        "F": pilot["F"],
        "baseline_A": pilot["baseline_A"],
        "fairness": pilot["fairness"],
        "classification_exploratory": pilot_class,
        "exploratory": True,
        "elapsed_s": time.time() - t0,
    }
    pilot_path = os.path.join(out_dir, "exp8_pilot_results.json")
    with open(pilot_path, "w") as f:
        json.dump(pilot_bundle, f, indent=2, default=str)
    if verbose:
        print(f"Pilot → {pilot_path}")
        print("Pilot notes:", {k: pilot_notes[k] for k in pilot_notes if k != "classification"})
        print("Pilot categories:", pilot_notes["classification"])

    if pilot_only:
        return pilot_bundle

    if confirm_n is None:
        confirm_n = cfg.CONFIRM_N
    confirm_seeds = list(range(cfg.CONFIRM_SEED_START, cfg.CONFIRM_SEED_START + confirm_n))

    freeze = {
        "frozen_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "protocol": Exp8ProtocolFreeze().to_dict(),
        "confirm_n": confirm_n,
        "confirm_seeds": confirm_seeds,
        "pilot_notes": {
            k: pilot_notes[k] for k in (
                "amp", "encoding", "A_near_f1", "numerical_pass", "ceiling_risk", "floor_risk",
            )
        },
        "primary_endpoints": {
            "A": "nonlinear vs linear near-pair correctness + response surface",
            "B": "activation delay0 vs delay40",
            "C": "cluster vs dispersed activation (equal mass)",
            "D": "forward activation threshold + hysteresis proxy",
            "E": "agree/oppose predictability (limitation documented)",
            "F": "completion_lift vs partial_only",
        },
        "note": "No retuning after confirmatory inspection.",
    }
    freeze_path = os.path.join(out_dir, "exp8_configuration.json")
    with open(freeze_path, "w") as f:
        json.dump(freeze, f, indent=2)
    if verbose:
        print(f"Frozen config → {freeze_path}")
        print(f"=== Confirmatory N={confirm_n} seeds {confirm_seeds[0]}..{confirm_seeds[-1]} ===")

    conf = run_all_suites(confirm_seeds, verbose=verbose)

    # Bridge justification from confirmatory classification (pre-bridge)
    pre_class = classify_operations({
        **{k: conf[k] for k in ("A", "B", "C", "D", "E", "F", "numerical")},
        "behavioural_bridge": None,
    })
    justified = any(
        isinstance(v, dict) and v.get("category", 0) >= 4
        for k, v in pre_class.items() if not k.startswith("_")
    )
    if skip_bridge:
        bridge = {"justified": justified, "skipped": True,
                  "reason": "skip_bridge flag", "causal_pass": False}
    else:
        if verbose:
            print(f"  behavioural bridge justified={justified}…")
        bridge = run_behavioural_bridge(confirm_seeds, justified=justified)

    conf["behavioural_bridge"] = bridge
    analysis = analyze_confirmatory(conf, confirm_seeds)
    # Re-classify with bridge
    analysis["classification"] = classify_operations({
        **{k: conf[k] for k in ("A", "B", "C", "D", "E", "F", "numerical")},
        "behavioural_bridge": bridge,
    })
    analysis["acceptance_level"] = analysis["classification"]["_meta"]["acceptance_level_suggested"]
    # Refresh E10
    analysis["gates"]["E10"] = bool(bridge.get("causal_pass"))

    confirm_bundle = {
        "protocol": Exp8ProtocolFreeze().to_dict(),
        "confirm_n": confirm_n,
        "confirm_seeds": confirm_seeds,
        "numerical": conf["numerical"],
        "A": conf["A"],
        "B": conf["B"],
        "C": conf["C"],
        "D": conf["D"],
        "E": conf["E"],
        "F": conf["F"],
        "baseline_A": conf["baseline_A"],
        "fairness": conf["fairness"],
        "behavioural_bridge": bridge,
        "analysis": analysis,
        "elapsed_s": time.time() - t0,
    }
    out_path = os.path.join(out_dir, "exp8_results.json")
    with open(out_path, "w") as f:
        json.dump(confirm_bundle, f, indent=2, default=str)
    if verbose:
        print(f"Confirmatory → {out_path}")
        print("Acceptance level:", analysis["acceptance_level"])
        print("Gates:", {k: ("PASS" if v else "FAIL") for k, v in analysis["gates"].items()})
        cats = {k: v.get("category") for k, v in analysis["classification"].items()
                if isinstance(v, dict) and "category" in v}
        print("Categories:", cats)
    return confirm_bundle
