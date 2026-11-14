"""
EXP3 Runner
===========

Execution protocol (strict order per specification):
  1. python exp3_runner.py --pilot          # 10 seeds, calibrate task_window
  2. python exp3_runner.py --tau-scan       # 10 seeds × 4 tau values
  3. python exp3_runner.py --main           # 40 seeds (after freezing config)

Experiment IDs: {run_type}_{condition}_{seed}_tau{tau_str}
Never identified by seed alone.

All ablations are strictly online (no future information).
See exp3_environment.py for complete condition definitions.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from dataclasses import dataclass, field, asdict
from typing import Any

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

import numpy as np

from sim_world.exp3_environment import (
    run_trial, CONDITIONS,
    N_AGENTS, MIN_COORD_AGENTS, TASK_WINDOW_TICKS,
)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class RunConfig:
    run_type: str = "main"
    n_ticks: int = 100
    tau: float = 2.0
    c: float = 1.0
    n_trials: int = 40
    base_seed: int = 7000
    task_window: int = TASK_WINDOW_TICKS
    min_coord: int = MIN_COORD_AGENTS
    conditions: list = field(default_factory=lambda: list(CONDITIONS))


PILOT_CONFIG  = RunConfig(run_type="pilot",    n_ticks=100, tau=3.0, n_trials=20, base_seed=9100)
MAIN_CONFIG   = RunConfig(run_type="main",     n_ticks=100, tau=3.0, n_trials=40, base_seed=7000)
TAU_SCAN_TAUS = [1.5, 2.0, 2.5, 3.0]
TAU_SCAN_BASE = 8000


def make_exp_id(run_type: str, condition: str, seed: int, tau: float) -> str:
    tau_str = f"{tau:.1f}".replace(".", "p")
    return f"exp3_{run_type}_{condition}_{seed}_tau{tau_str}"


# ---------------------------------------------------------------------------
# Single run
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
        task_window=cfg.task_window,
        min_coord=cfg.min_coord,
    )


# ---------------------------------------------------------------------------
# Batch runner
# ---------------------------------------------------------------------------

def run_batch(
    cfg: RunConfig,
    per_tick_path: str | None = None,
    verbose: bool = True,
) -> list[dict[str, Any]]:
    """Run all conditions for all seeds. Streams per-tick records to JSONL."""
    summaries: list[dict] = []
    total = cfg.n_trials * len(cfg.conditions)
    done = 0
    t0 = time.time()

    jsonl_f = open(per_tick_path, "w") if per_tick_path else None

    try:
        for trial_idx in range(cfg.n_trials):
            seed = cfg.base_seed + trial_idx
            for condition in cfg.conditions:
                result = run_one(seed, condition, cfg)
                per_tick = result.pop("per_tick")
                summaries.append(result)
                done += 1

                if jsonl_f:
                    for rec in per_tick:
                        jsonl_f.write(json.dumps(rec) + "\n")
                    jsonl_f.flush()

                if verbose and (done % (len(cfg.conditions) * 2) == 0 or done <= len(cfg.conditions)):
                    elapsed = time.time() - t0
                    ccr = result.get("coord_completion_rate")
                    ucr = result.get("unnecessary_coop_rate")
                    print(f"  [{done:3d}/{total}] {condition:>16} seed={seed} "
                          f"CCR={ccr} UCR={ucr:.3f} "
                          f"elapsed={elapsed:.0f}s")
    finally:
        if jsonl_f:
            jsonl_f.close()

    return summaries


# ---------------------------------------------------------------------------
# Pilot calibration
# ---------------------------------------------------------------------------

def run_pilot(tau: float = 3.0, verbose: bool = True) -> dict[str, Any]:
    """
    Run pilot with task_window=3, 5, and 8 to calibrate.
    Target: baseline CCR 40-75%.
    Returns the recommended task_window.
    """
    print("\n--- PILOT CALIBRATION ---")
    recommendations = {}
    for tw in [3, 5, 8]:
        cfg = RunConfig(
            run_type="pilot", n_ticks=100, tau=tau,
            n_trials=20, base_seed=9100,
            task_window=tw, min_coord=MIN_COORD_AGENTS,
            conditions=["baseline", "spectral"],
        )
        summaries = run_batch(cfg, verbose=False)
        base_ccrs = [r["coord_completion_rate"] for r in summaries
                     if r["condition"] == "baseline" and r["coord_completion_rate"] is not None]
        spec_ccrs = [r["coord_completion_rate"] for r in summaries
                     if r["condition"] == "spectral" and r["coord_completion_rate"] is not None]
        base_mean = float(np.mean(base_ccrs)) if base_ccrs else 0.
        spec_mean = float(np.mean(spec_ccrs)) if spec_ccrs else 0.
        in_target = 0.40 <= base_mean <= 0.75
        print(f"  task_window={tw}: baseline_CCR={base_mean:.3f} spectral_CCR={spec_mean:.3f} "
              f"{'✓ IN TARGET' if in_target else '✗ outside 40-75%'}")
        recommendations[tw] = {"baseline": base_mean, "spectral": spec_mean, "in_target": in_target}

    # Select best window
    for tw in [3, 5, 8]:
        if recommendations[tw]["in_target"]:
            print(f"  → Selected task_window={tw} (baseline CCR in target range)")
            return {"recommended_window": tw, "results": recommendations}

    # None in perfect range — pick closest to 0.57 (midpoint of 40-75%)
    best = min([3, 5, 8], key=lambda tw: abs(recommendations[tw]["baseline"] - 0.57))
    print(f"  → No window in 40-75%. Using closest: task_window={best} "
          f"(baseline={recommendations[best]['baseline']:.3f})")
    return {"recommended_window": best, "results": recommendations}


# ---------------------------------------------------------------------------
# Tau scan
# ---------------------------------------------------------------------------

def run_tau_scan(
    tau_values: list[float] = TAU_SCAN_TAUS,
    n_trials: int = 10,
    base_seed: int = TAU_SCAN_BASE,
    n_ticks: int = 100,
    verbose: bool = True,
) -> list[dict[str, Any]]:
    """Exploratory tau scan. Spectral + baseline conditions only."""
    print("\n--- TAU SCAN (exploratory) ---")
    all_results: list[dict] = []
    for tau in tau_values:
        cfg = RunConfig(
            run_type="tau_scan", n_ticks=n_ticks, tau=tau,
            n_trials=n_trials, base_seed=base_seed,
            conditions=["spectral", "baseline"],
        )
        summaries = run_batch(cfg, verbose=False)
        all_results.extend(summaries)
        spec = [r["coord_completion_rate"] for r in summaries
                if r["condition"] == "spectral" and r["coord_completion_rate"] is not None]
        base = [r["coord_completion_rate"] for r in summaries
                if r["condition"] == "baseline" and r["coord_completion_rate"] is not None]
        c_std = [r["c_spectral_std"] for r in summaries if r["condition"] == "spectral"]
        if spec and base:
            print(f"  tau={tau:.1f}: spectral={np.mean(spec):.3f}  baseline={np.mean(base):.3f}  "
                  f"diff={np.mean(spec)-np.mean(base):+.3f}  "
                  f"c_spectral_std={np.mean(c_std):.4f}")
    return all_results


# ---------------------------------------------------------------------------
# Statistical helpers
# ---------------------------------------------------------------------------

def _paired_ttest(a: list[float], b: list[float]) -> tuple[float, float]:
    d = [ai - bi for ai, bi in zip(a, b)]
    n = len(d)
    if n < 2: return float("nan"), float("nan")
    mean_d = sum(d) / n
    var_d = sum((x - mean_d)**2 for x in d) / (n - 1)
    if var_d == 0: return float("nan"), float("nan")
    t = mean_d / math.sqrt(var_d / n)
    p = math.erfc(abs(t) / math.sqrt(2.0))
    return t, p


def _wilcoxon_manual(d: list[float]) -> float:
    """Return two-sided p approximation via normal approximation."""
    arr = [x for x in d if x != 0]
    n = len(arr)
    if n < 5: return float("nan")
    indexed = sorted(enumerate(arr), key=lambda x: abs(x[1]))
    ranks = [0.] * len(arr)
    i = 0
    while i < n:
        j = i
        while j < n - 1 and abs(indexed[j+1][1]) == abs(indexed[j][1]):
            j += 1
        avg = (i + j) / 2. + 1.
        for k in range(i, j + 1):
            ranks[indexed[k][0]] = avg
        i = j + 1
    W = min(sum(ranks[k] for k, x in enumerate(arr) if x > 0),
            sum(ranks[k] for k, x in enumerate(arr) if x < 0))
    mean_W = n * (n + 1) / 4.
    var_W = n * (n + 1) * (2*n + 1) / 24.
    if var_W <= 0: return float("nan")
    z = (W - mean_W) / math.sqrt(var_W)
    return float(math.erfc(abs(z) / math.sqrt(2.0)))


def _bootstrap_ci(d: list[float], n_boot: int = 2000) -> tuple[float, float]:
    rng = np.random.default_rng(42)
    arr = np.array(d)
    boot = np.array([float(np.mean(rng.choice(arr, size=len(arr), replace=True)))
                     for _ in range(n_boot)])
    return float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))


BONFERRONI_ALPHA = 0.05 / 6  # 6 primary comparisons


def compare(
    summaries: list[dict],
    cond_a: str,
    cond_b: str,
    metric: str = "coord_completion_rate",
) -> dict:
    a_map = {r["seed"]: r[metric] for r in summaries
             if r["condition"] == cond_a and r[metric] is not None}
    b_map = {r["seed"]: r[metric] for r in summaries
             if r["condition"] == cond_b and r[metric] is not None}
    seeds = sorted(set(a_map) & set(b_map))
    if not seeds:
        return {"error": "no paired seeds"}
    a_v = [a_map[s] for s in seeds]
    b_v = [b_map[s] for s in seeds]
    d_v = [a - b for a, b in zip(a_v, b_v)]
    n = len(d_v)
    mean_d = float(np.mean(d_v))
    std_d = float(np.std(d_v, ddof=1)) if n > 1 else 0.
    t, p_t = _paired_ttest(a_v, b_v)
    p_w = _wilcoxon_manual(d_v)
    ci_lo, ci_hi = _bootstrap_ci(d_v)
    cd = mean_d / std_d if std_d > 0 else float("nan")
    sig = not math.isnan(p_t) and p_t < BONFERRONI_ALPHA
    sig_w = not math.isnan(p_w) and p_w < BONFERRONI_ALPHA
    return {
        "cond_a": cond_a, "cond_b": cond_b, "metric": metric,
        "n": n, "seeds": seeds,
        "mean_a": round(float(np.mean(a_v)), 6),
        "mean_b": round(float(np.mean(b_v)), 6),
        "mean_diff": round(mean_d, 6),
        "std_diff": round(std_d, 6),
        "ci_95": [round(ci_lo, 6), round(ci_hi, 6)],
        "t": round(t, 4) if not math.isnan(t) else None,
        "p_ttest": round(p_t, 6) if not math.isnan(p_t) else None,
        "p_wilcoxon": round(p_w, 6) if not math.isnan(p_w) else None,
        "p_bonferroni": round(min(p_t * 6, 1.0), 6) if not math.isnan(p_t) else None,
        "cohens_d": round(cd, 4) if not math.isnan(cd) else None,
        "sig_ttest": sig,
        "sig_wilcoxon": sig_w,
        "significant": sig and sig_w,
        "direction": "a_better" if mean_d > 0 else ("no_diff" if mean_d == 0 else "b_better"),
        "bonferroni_alpha": BONFERRONI_ALPHA,
    }


def summarise(summaries: list[dict], metric: str = "coord_completion_rate") -> dict:
    out = {}
    for cond in CONDITIONS:
        vals = [r[metric] for r in summaries
                if r["condition"] == cond and r.get(metric) is not None]
        if not vals:
            out[cond] = {"n": 0}
            continue
        out[cond] = {
            "n": len(vals),
            "mean": round(float(np.mean(vals)), 6),
            "std":  round(float(np.std(vals, ddof=1)), 6) if len(vals) > 1 else 0.,
            "min":  round(float(np.min(vals)), 6),
            "max":  round(float(np.max(vals)), 6),
        }
    return out


def print_comparison_table(summaries: list[dict]) -> None:
    print(f"\n  {'condition':>18}  {'CCR mean':>9}  {'CCR std':>8}  "
          f"{'UCR mean':>9}  {'coord%':>7}")
    print("  " + "-" * 60)
    for cond in CONDITIONS:
        ccr_vals = [r["coord_completion_rate"] for r in summaries
                    if r["condition"] == cond and r["coord_completion_rate"] is not None]
        ucr_vals = [r["unnecessary_coop_rate"] for r in summaries
                    if r["condition"] == cond]
        cr_vals  = [r["coordination_rate"] for r in summaries
                    if r["condition"] == cond]
        if not ccr_vals: continue
        print(f"  {cond:>18}  {np.mean(ccr_vals):>9.4f}  "
              f"{np.std(ccr_vals,ddof=1):>8.4f}  "
              f"{np.mean(ucr_vals):>9.4f}  "
              f"{np.mean(cr_vals):>7.1%}")

    print(f"\n  Bonferroni alpha = {BONFERRONI_ALPHA:.4f}")
    comparisons = [
        ("spectral", "baseline"),
        ("spectral", "online_shuffled"),
        ("spectral", "online_delayed"),
        ("spectral", "running_mean"),
        ("precursor_only", "baseline"),
        ("feedback_only", "baseline"),
    ]
    print(f"\n  {'comparison':>36}  {'diff':>8}  {'95%CI':>18}  {'p':>8}  {'d':>7}  sig")
    print("  " + "-" * 85)
    for ca, cb in comparisons:
        r = compare(summaries, ca, cb)
        if "error" in r:
            print(f"  {ca+' vs '+cb:>36}: {r['error']}")
            continue
        ci = r["ci_95"]
        p = r.get("p_ttest")
        d = r.get("cohens_d")
        sig = "✓" if r["significant"] else "~"
        print(f"  {ca+' vs '+cb:>36}:  "
              f"{r['mean_diff']:+.4f}  [{ci[0]:+.4f},{ci[1]:+.4f}]  "
              f"{(str(round(p,4)) if p else 'n/a'):>8}  "
              f"{(str(round(d,3)) if d else 'n/a'):>7}  {sig}")


# ---------------------------------------------------------------------------
# Save helpers
# ---------------------------------------------------------------------------

def _save(obj: Any, path: str) -> None:
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)
    size_kb = os.path.getsize(path) // 1024
    print(f"  Saved → {os.path.basename(path)}  ({size_kb}KB)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="EXP3 runner")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pilot",    action="store_true")
    group.add_argument("--tau-scan", action="store_true", dest="tau_scan")
    group.add_argument("--main",     action="store_true")
    parser.add_argument("--tau",     type=float, default=2.0)
    parser.add_argument("--window",  type=int,   default=None,
                        help="Override task_window (skips pilot calibration)")
    parser.add_argument("--trials",  type=int,   default=None)
    args = parser.parse_args()

    print("\n" + "=" * 65)
    print(f"  EXP3 RUNNER")

    if args.pilot:
        print(f"  Mode: PILOT CALIBRATION")
        print("=" * 65)
        pilot = run_pilot(tau=args.tau)
        _save(pilot, os.path.join(_HERE, "exp3_pilot_results.json"))
        recommended = pilot["recommended_window"]
        print(f"\n  Recommended task_window = {recommended}")
        print(f"  Freeze this in RunConfig before running --main")

    elif args.tau_scan:
        print(f"  Mode: TAU SCAN (exploratory)")
        print("=" * 65)
        results = run_tau_scan()
        _save(results, os.path.join(_HERE, "exp3_tau_scan.json"))
        print(f"\n  Tau scan complete. Review exp3_tau_scan.json before running --main.")

    elif args.main:
        task_window = args.window if args.window else TASK_WINDOW_TICKS
        cfg = MAIN_CONFIG
        if args.tau:   cfg.tau = args.tau
        if args.trials: cfg.n_trials = args.trials
        if task_window: cfg.task_window = task_window

        print(f"  Mode: MAIN EXPERIMENT")
        print(f"  Trials:     {cfg.n_trials} per condition")
        print(f"  Conditions: {cfg.conditions}")
        print(f"  Ticks:      {cfg.n_ticks}  Tau: {cfg.tau}  Window: {cfg.task_window}")
        print(f"  Seeds:      {cfg.base_seed} … {cfg.base_seed + cfg.n_trials - 1}")
        print("=" * 65)

        prefix = "exp3_main"
        pt_path = os.path.join(_HERE, f"{prefix}_per_tick.jsonl")

        t0 = time.time()
        summaries = run_batch(cfg, per_tick_path=pt_path, verbose=True)
        elapsed = time.time() - t0
        print(f"\n  Elapsed: {elapsed:.0f}s")

        # Analysis
        print("\n--- Results ---")
        print_comparison_table(summaries)

        # Save
        _save(summaries, os.path.join(_HERE, f"{prefix}_results.json"))
        _save({
            "config": asdict(cfg),
            "summary": summarise(summaries),
            "comparisons": {
                f"{ca}_vs_{cb}": compare(summaries, ca, cb)
                for ca, cb in [
                    ("spectral", "baseline"),
                    ("spectral", "online_shuffled"),
                    ("spectral", "online_delayed"),
                    ("spectral", "running_mean"),
                    ("precursor_only", "baseline"),
                    ("feedback_only", "baseline"),
                ]
            },
        }, os.path.join(_HERE, f"{prefix}_analysis.json"))
        print(f"\n  Per-tick JSONL: {pt_path}")

    print("=" * 65)


if __name__ == "__main__":
    main()
