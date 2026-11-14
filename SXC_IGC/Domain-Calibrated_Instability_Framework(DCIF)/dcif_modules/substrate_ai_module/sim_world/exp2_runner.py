"""
EXP2 Experiment Runner
======================

Controlled repeated-trial experiment to determine whether the actual
field-derived spectral observable (C_spectral) improves autonomous-agent
coordination decisions compared with equivalent systems without that signal.

EXPERIMENTAL CONDITIONS
-----------------------
  baseline     — no substrate signal (signal=0.0); agents use need+task-availability only
  spectral     — actual field-derived C_spectral from compute_spectral_transport_observable
  time_reversed— same spectral values as a reference run, reversed in time
  shuffled     — same spectral values, random temporal order
  constant     — constant signal equal to the trial-level mean of spectral series

PAIRING
-------
All five conditions within a trial share the same seed (identical field
init, agent init, task schedule). RNG streams are isolated per purpose.

PRIMARY METRIC
--------------
  coord_completion_rate: fraction of coordination task opportunities where
  ≥ MIN_COORD_AGENTS agents committed to cooperate within the task window.
  Higher is better (pre-registered; not changed after seeing data).

EXPERIMENT IDs
--------------
  Format: {run_type}_{condition}_{seed}_{tau_str}
  run_type: "diag" (diagnostic, 10 seeds) or "main" (full experiment)
  This prevents cross-experiment data contamination.

USAGE
-----
  python exp2_runner.py --diagnostic        # 10 seeds, smoke test
  python exp2_runner.py --main              # 30 seeds, full experiment
  python exp2_runner.py --pilot 5           # 5 seeds pilot
  python exp2_runner.py --diagnostic --tau 3.0 2.0  # explicit tau values
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

import numpy as np

from sim_world.exp2_environment import (
    run_trial,
    N_AGENTS,
    MIN_COORD_AGENTS,
    COORD_REWARD,
    INDEP_REWARD,
)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CONDITIONS = ["baseline", "spectral", "time_reversed", "shuffled", "constant"]

@dataclass
class RunConfig:
    run_type: str = "main"          # "diag" | "main" | "pilot"
    n_ticks: int = 80               # ticks per trial
    tau: float = 3.0                # relaxation time
    c: float = 1.0                  # propagation speed
    n_trials: int = 30              # trials per condition
    base_seed: int = 5000           # seeds: base_seed, base_seed+1, ...
    conditions: list = field(default_factory=lambda: list(CONDITIONS))
    tau_scan: list = field(default_factory=list)  # extra tau values for tau scan


DIAG_CONFIG = RunConfig(run_type="diag", n_ticks=80, tau=3.0, n_trials=10,
                        base_seed=5000)
MAIN_CONFIG = RunConfig(run_type="main", n_ticks=80, tau=3.0, n_trials=30,
                        base_seed=5000)


# ---------------------------------------------------------------------------
# Experiment ID
# ---------------------------------------------------------------------------

def make_exp_id(run_type: str, condition: str, seed: int, tau: float) -> str:
    tau_str = f"tau{tau:.1f}".replace(".", "p")
    return f"{run_type}_{condition}_{seed}_{tau_str}"


# ---------------------------------------------------------------------------
# Run one condition for one seed
# ---------------------------------------------------------------------------

def run_one(seed: int, condition: str, cfg: RunConfig) -> dict[str, Any]:
    exp_id = make_exp_id(cfg.run_type, condition, seed, cfg.tau)
    return run_trial(
        seed=seed,
        condition=condition,
        n_ticks=cfg.n_ticks,
        tau=cfg.tau,
        c=cfg.c,
        exp_id=exp_id,
    )


# ---------------------------------------------------------------------------
# Run full experiment batch
# ---------------------------------------------------------------------------

def run_batch(cfg: RunConfig, verbose: bool = True) -> list[dict[str, Any]]:
    """Run all conditions for all seeds. Returns flat list of trial results."""
    all_results: list[dict] = []
    total = cfg.n_trials * len(cfg.conditions)
    done = 0
    t0 = time.time()

    for trial_idx in range(cfg.n_trials):
        seed = cfg.base_seed + trial_idx
        for condition in cfg.conditions:
            result = run_one(seed, condition, cfg)
            # Drop per_tick to keep summary file manageable; save separately
            per_tick = result.pop("per_tick")
            all_results.append(result)
            done += 1
            if verbose and (done % 10 == 0 or done <= 5):
                elapsed = time.time() - t0
                rate = round(elapsed / done, 2)
                remaining = round(rate * (total - done), 1)
                print(
                    f"  [{done:3d}/{total}] {cfg.run_type}/{condition} "
                    f"seed={seed} "
                    f"coord_rate={result.get('coord_completion_rate', '?')} "
                    f"elapsed={elapsed:.1f}s eta={remaining}s"
                )

    return all_results


# ---------------------------------------------------------------------------
# Tau scan (exploratory, not main experiment)
# ---------------------------------------------------------------------------

def run_tau_scan(
    tau_values: list[float],
    n_trials: int = 10,
    base_seed: int = 6000,
    n_ticks: int = 80,
    verbose: bool = True,
) -> list[dict[str, Any]]:
    """Run spectral condition across multiple tau values. Exploratory only."""
    results = []
    for tau in tau_values:
        cfg = RunConfig(
            run_type="tau_scan",
            n_ticks=n_ticks,
            tau=tau,
            n_trials=n_trials,
            base_seed=base_seed,
            conditions=["spectral", "baseline"],
        )
        for trial_idx in range(n_trials):
            seed = base_seed + trial_idx
            for condition in ["spectral", "baseline"]:
                r = run_one(seed, condition, cfg)
                r.pop("per_tick", None)
                results.append(r)
        if verbose:
            tau_res = [r for r in results if r["tau"] == tau and
                       r["condition"] == "spectral"]
            mean_ccr = np.mean([r["coord_completion_rate"] or 0
                                for r in tau_res])
            print(f"  tau={tau:.2f} spectral coord_rate={mean_ccr:.1%}")
    return results


# ---------------------------------------------------------------------------
# Statistical analysis
# ---------------------------------------------------------------------------

def _mean_std(vals: list[float]) -> tuple[float, float]:
    if not vals:
        return float("nan"), float("nan")
    arr = np.array(vals)
    return float(np.mean(arr)), float(np.std(arr, ddof=1) if len(arr) > 1 else 0.0)


def _paired_ttest_manual(a: list[float], b: list[float]) -> tuple[float, float]:
    """Manual paired t-test (no scipy required)."""
    d = [ai - bi for ai, bi in zip(a, b)]
    n = len(d)
    if n < 2:
        return float("nan"), float("nan")
    mean_d = sum(d) / n
    var_d = sum((x - mean_d) ** 2 for x in d) / (n - 1)
    if var_d == 0:
        return float("nan"), float("nan")
    t = mean_d / math.sqrt(var_d / n)
    # Normal approximation for df >= 20
    if n >= 20:
        z = abs(t)
        # erfc approximation
        p = math.erfc(z / math.sqrt(2.0))
        return t, float(p)
    return t, float("nan")


def _bootstrap_ci(d: list[float], n_boot: int = 2000) -> tuple[float, float]:
    rng = np.random.default_rng(99)
    arr = np.array(d)
    boot = np.array([float(np.mean(rng.choice(arr, size=len(arr), replace=True)))
                     for _ in range(n_boot)])
    return float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))


def _cohens_d(d: list[float]) -> float:
    arr = np.array(d)
    std = float(np.std(arr, ddof=1))
    return float("nan") if std == 0 else float(np.mean(arr) / std)


def compare_conditions(
    results: list[dict],
    cond_a: str = "spectral",
    cond_b: str = "baseline",
    metric: str = "coord_completion_rate",
) -> dict[str, Any]:
    """Paired comparison of two conditions matched by seed."""
    a_map = {r["seed"]: r[metric] for r in results
             if r["condition"] == cond_a and r[metric] is not None}
    b_map = {r["seed"]: r[metric] for r in results
             if r["condition"] == cond_b and r[metric] is not None}
    seeds = sorted(set(a_map) & set(b_map))
    if not seeds:
        return {"error": "no paired seeds"}
    a_vals = [a_map[s] for s in seeds]
    b_vals = [b_map[s] for s in seeds]
    d_vals = [a - b for a, b in zip(a_vals, b_vals)]

    n = len(d_vals)
    mean_d = float(np.mean(d_vals))
    std_d = float(np.std(d_vals, ddof=1)) if n > 1 else 0.0
    se_d = std_d / math.sqrt(n) if n > 0 else 0.0
    t, p = _paired_ttest_manual(a_vals, b_vals)
    ci_lo, ci_hi = _bootstrap_ci(d_vals)
    cd = _cohens_d(d_vals)

    alpha = 0.05 / 4   # Bonferroni: 4 comparisons
    significant = not math.isnan(p) and p < alpha

    direction = ("spectral_better" if mean_d > 0
                 else ("no_difference" if mean_d == 0 else "spectral_worse"))

    return {
        "cond_a": cond_a, "cond_b": cond_b,
        "metric": metric, "n_pairs": n,
        "mean_a": round(float(np.mean(a_vals)), 6),
        "mean_b": round(float(np.mean(b_vals)), 6),
        "mean_diff": round(mean_d, 6),
        "std_diff": round(std_d, 6),
        "ci_95": [round(ci_lo, 6), round(ci_hi, 6)],
        "t": round(t, 4) if not math.isnan(t) else None,
        "p_raw": round(p, 6) if not math.isnan(p) else None,
        "p_bonferroni": round(min(p * 4, 1.0), 6) if not math.isnan(p) else None,
        "cohens_d": round(cd, 4) if not math.isnan(cd) else None,
        "significant": significant,
        "direction": direction,
        "bonferroni_alpha": alpha,
    }


def lead_lag_analysis(
    per_tick_records: list[dict],
    max_lead: int = 10,
) -> dict[str, Any]:
    """
    Measure cross-correlation between C_spectral (actual) and
    coordination demand (coord_task_active), at lead times -max_lead..+max_lead.

    Positive lead k: C_spectral at tick t is correlated with demand at tick t+k
    (C_spectral leads demand — predictive).
    Negative lead k: C_spectral at tick t is correlated with demand at tick t+k
    (C_spectral lags demand — reactive).

    Returns dict with lag_values and cross_correlations.
    """
    if not per_tick_records:
        return {}
    ticks = sorted(set(r["tick"] for r in per_tick_records))
    # Gather arrays indexed by tick
    c_sp = {r["tick"]: r["c_spectral_actual"] for r in per_tick_records}
    demand = {r["tick"]: int(r["coord_task_active"]) for r in per_tick_records}

    c_arr = np.array([c_sp.get(t, 0.0) for t in ticks])
    d_arr = np.array([demand.get(t, 0) for t in ticks], dtype=float)

    # Normalise
    c_norm = (c_arr - c_arr.mean()) / (c_arr.std() + 1e-12)
    d_norm = (d_arr - d_arr.mean()) / (d_arr.std() + 1e-12)
    n = len(ticks)

    lags = list(range(-max_lead, max_lead + 1))
    xcorr = []
    for lag in lags:
        if lag == 0:
            xc = float(np.mean(c_norm * d_norm))
        elif lag > 0:
            # C_spectral leads by lag ticks
            xc = float(np.mean(c_norm[:-lag] * d_norm[lag:]))
        else:
            # C_spectral lags by |lag| ticks
            xc = float(np.mean(c_norm[-lag:] * d_norm[:lag]))
        xcorr.append(round(xc, 6))

    # Find peak lead
    peak_idx = int(np.argmax(np.abs(xcorr)))
    return {
        "lags": lags,
        "cross_correlations": xcorr,
        "peak_lag": lags[peak_idx],
        "peak_xcorr": xcorr[peak_idx],
        "contemporaneous": xcorr[max_lead],  # lag=0
    }


def analyse_results(
    results: list[dict],
    per_tick_all: list[dict] | None = None,
) -> dict[str, Any]:
    """Full analysis of experiment results."""
    metric = "coord_completion_rate"
    comparisons = ["baseline", "time_reversed", "shuffled", "constant"]
    comparison_results = {
        f"spectral_vs_{comp}": compare_conditions(results, "spectral", comp, metric)
        for comp in comparisons
    }

    # Summary per condition
    summary: dict[str, Any] = {}
    for cond in CONDITIONS:
        cond_results = [r for r in results if r["condition"] == cond
                        and r[metric] is not None]
        vals = [r[metric] for r in cond_results]
        m, s = _mean_std(vals)
        summary[cond] = {
            "n": len(vals),
            "mean": round(m, 6) if not math.isnan(m) else None,
            "std":  round(s, 6) if not math.isnan(s) else None,
            "mean_resources": round(float(np.mean([r["mean_resources"]
                                                   for r in cond_results])), 4)
                              if cond_results else None,
            "coordination_rate": round(float(np.mean([r["coordination_rate"]
                                                      for r in cond_results])), 4)
                                 if cond_results else None,
        }

    # Lead-lag (if per-tick records available)
    lead_lag = {}
    if per_tick_all:
        spectral_ticks = [r for r in per_tick_all if r["condition"] == "spectral"]
        lead_lag = lead_lag_analysis(spectral_ticks)

    return {
        "primary_metric": metric,
        "metric_direction": "higher_is_better",
        "bonferroni_alpha": 0.05 / 4,
        "summary": summary,
        "comparisons": comparison_results,
        "lead_lag": lead_lag,
    }


# ---------------------------------------------------------------------------
# Save helpers
# ---------------------------------------------------------------------------

def _save(obj: Any, path: str) -> None:
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)
    print(f"  Saved → {path}  ({os.path.getsize(path)//1024}KB)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="EXP2 runner")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--diagnostic", action="store_true",
                       help="Diagnostic run: 10 seeds")
    group.add_argument("--main", action="store_true",
                       help="Main experiment: 30 seeds")
    group.add_argument("--pilot", type=int, metavar="N",
                       help="Pilot run: N seeds")
    parser.add_argument("--tau", type=float, nargs="+", default=[3.0],
                        help="Tau value(s). First is used for main/diag.")
    parser.add_argument("--tau-scan", action="store_true",
                        help="Also run tau scan after main experiment")
    parser.add_argument("--no-per-tick", action="store_true",
                        help="Skip saving per-tick JSONL (faster, smaller)")
    args = parser.parse_args()

    tau = args.tau[0]

    if args.diagnostic:
        cfg = RunConfig(run_type="diag", n_ticks=80, tau=tau, n_trials=10,
                        base_seed=5000)
        prefix = "exp2_diag"
    elif args.main:
        cfg = RunConfig(run_type="main", n_ticks=80, tau=tau, n_trials=30,
                        base_seed=5000)
        prefix = "exp2_main"
    else:
        cfg = RunConfig(run_type="pilot", n_ticks=80, tau=tau,
                        n_trials=args.pilot, base_seed=5000)
        prefix = f"exp2_pilot{args.pilot}"

    print("\n" + "=" * 65)
    print(f"  EXP2 EXPERIMENT RUNNER")
    print(f"  Mode:       {cfg.run_type}")
    print(f"  Trials:     {cfg.n_trials} per condition")
    print(f"  Conditions: {cfg.conditions}")
    print(f"  Ticks:      {cfg.n_ticks}")
    print(f"  Tau:        {cfg.tau}")
    print(f"  Seeds:      {cfg.base_seed} … {cfg.base_seed + cfg.n_trials - 1}")
    print("=" * 65)

    t0 = time.time()

    # Run with per-tick collection for lead-lag analysis
    # (we collect per_tick separately to keep summary file small)
    all_results: list[dict] = []
    per_tick_all: list[dict] = []
    total = cfg.n_trials * len(cfg.conditions)
    done = 0

    for trial_idx in range(cfg.n_trials):
        seed = cfg.base_seed + trial_idx
        for condition in cfg.conditions:
            exp_id = make_exp_id(cfg.run_type, condition, seed, cfg.tau)
            result = run_trial(
                seed=seed,
                condition=condition,
                n_ticks=cfg.n_ticks,
                tau=cfg.tau,
                c=cfg.c,
                exp_id=exp_id,
            )
            per_tick = result.pop("per_tick")
            if not args.no_per_tick:
                per_tick_all.extend(per_tick)
            all_results.append(result)
            done += 1
            if done % 10 == 0 or done <= cfg.n_trials:
                elapsed = time.time() - t0
                ccr = result.get("coord_completion_rate")
                cs_std = result.get("c_spectral_std", "?")
                print(f"  [{done:3d}/{total}] {condition:>14} seed={seed} "
                      f"coord_rate={ccr} "
                      f"C_spectral_std={cs_std}")

    elapsed = time.time() - t0
    print(f"\n  Total elapsed: {elapsed:.1f}s")

    # Analysis
    print("\n--- Statistical Analysis ---")
    analysis = analyse_results(all_results, per_tick_all if per_tick_all else None)

    # Print key results
    print(f"\n  Primary metric: {analysis['primary_metric']} (higher=better)")
    print(f"  {'condition':>14}  {'mean':>8}  {'std':>8}  {'coord_rate':>10}")
    print("  " + "-" * 50)
    for cond, s in analysis["summary"].items():
        m = f"{s['mean']:.4f}" if s.get("mean") is not None else "  n/a "
        sd = f"{s['std']:.4f}" if s.get("std") is not None else "  n/a "
        cr = f"{s['coordination_rate']:.1%}" if s.get("coordination_rate") else "  n/a"
        print(f"  {cond:>14}  {m:>8}  {sd:>8}  {cr:>10}")

    print(f"\n  Bonferroni alpha = {analysis['bonferroni_alpha']:.4f}")
    print(f"  {'comparison':>30}  {'diff':>8}  {'95% CI':>18}  {'p':>8}  {'d':>7}  {'sig':>5}")
    print("  " + "-" * 80)
    for key, comp in analysis["comparisons"].items():
        if "error" in comp:
            print(f"  {key:>30}: {comp['error']}")
            continue
        ci = comp["ci_95"]
        p = comp.get("p_raw")
        d = comp.get("cohens_d")
        sig = "✓" if comp["significant"] else "~"
        print(f"  {key:>30}: "
              f"{comp['mean_diff']:+.4f}  "
              f"[{ci[0]:+.4f},{ci[1]:+.4f}]  "
              f"{(str(round(p,4)) if p else 'n/a'):>8}  "
              f"{(str(round(d,3)) if d else 'n/a'):>7}  "
              f"{sig}")

    if analysis.get("lead_lag"):
        ll = analysis["lead_lag"]
        print(f"\n  Lead-lag: contemporaneous xcorr={ll['contemporaneous']:.4f}  "
              f"peak_lag={ll['peak_lag']}  peak_xcorr={ll['peak_xcorr']:.4f}")
        if ll["peak_lag"] > 0:
            print(f"  → C_spectral leads coordination demand by {ll['peak_lag']} ticks "
                  f"(potential predictive signal)")
        elif ll["peak_lag"] < 0:
            print(f"  → C_spectral lags coordination demand by {abs(ll['peak_lag'])} ticks "
                  f"(reactive / contemporaneous tracking)")
        else:
            print(f"  → Peak at lag=0 (contemporaneous correlation only)")

    # Tau scan
    tau_scan_results: list[dict] = []
    if args.tau_scan:
        print("\n--- Tau Scan ---")
        tau_values = args.tau if len(args.tau) > 1 else [0.5, 1.0, 1.5, 2.0, 3.0, 5.0]
        tau_scan_results = run_tau_scan(tau_values, n_trials=10, base_seed=6000,
                                        n_ticks=cfg.n_ticks)

    # Save
    _save(all_results, os.path.join(_HERE, f"{prefix}_results.json"))
    _save(analysis, os.path.join(_HERE, f"{prefix}_analysis.json"))
    if per_tick_all and not args.no_per_tick:
        jsonl_path = os.path.join(_HERE, f"{prefix}_per_tick.jsonl")
        with open(jsonl_path, "w") as f:
            for rec in per_tick_all:
                f.write(json.dumps(rec) + "\n")
        print(f"  Saved → {jsonl_path}  ({len(per_tick_all)} records)")
    if tau_scan_results:
        _save(tau_scan_results, os.path.join(_HERE, f"{prefix}_tau_scan.json"))

    print("=" * 65)


if __name__ == "__main__":
    main()
