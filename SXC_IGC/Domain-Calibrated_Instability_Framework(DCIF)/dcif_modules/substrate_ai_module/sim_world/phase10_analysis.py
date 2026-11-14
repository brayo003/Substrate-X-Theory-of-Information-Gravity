"""
Phase 10 Statistical Analysis
==============================

Loads phase10_raw_trials.json and computes:
  - Per-condition, per-scenario summary statistics
  - Paired comparisons (spectral vs baseline, legacy_q, ablation)
  - Paired t-test, Wilcoxon signed-rank, bootstrap CI, Cohen's d
  - Bonferroni correction (alpha = 0.05 / 3 = 0.0167)
  - Tau scan analysis
  - Saves full results to phase10_analysis_results.json

Primary metric: mean_final_hunger (lower = better).
Positive paired difference (spectral - other) means spectral is WORSE.
Negative paired difference means spectral is BETTER.

Usage:
    python phase10_analysis.py
    python phase10_analysis.py --input phase10_raw_trials.json
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from typing import Any

_HERE = os.path.dirname(os.path.abspath(__file__))

import numpy as np

try:
    from scipy import stats as _scipy_stats
    _HAS_SCIPY = True
except ImportError:
    _HAS_SCIPY = False
    print("  [INFO] scipy not available — using manual t-test and Wilcoxon implementations")


# ---------------------------------------------------------------------------
# Statistical primitives
# ---------------------------------------------------------------------------

def _regularized_incomplete_beta(x: float, a: float, b: float,
                                   max_iter: int = 200) -> float:
    """Regularized incomplete beta function I_x(a,b) via continued fraction."""
    import math
    if x < 0 or x > 1:
        return float("nan")
    if x == 0:
        return 0.0
    if x == 1:
        return 1.0
    lbeta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    front = math.exp(math.log(x) * a + math.log(1 - x) * b - lbeta) / a
    # Lentz's method for continued fraction
    f = 1.0; c = 1.0; d = 1.0 - (a + b) * x / (a + 1)
    if abs(d) < 1e-30: d = 1e-30
    d = 1.0 / d; f = d
    for m in range(1, max_iter + 1):
        # Even step
        num = m * (b - m) * x / ((a + 2*m - 1) * (a + 2*m))
        d = 1.0 + num * d
        if abs(d) < 1e-30: d = 1e-30
        c = 1.0 + num / c
        if abs(c) < 1e-30: c = 1e-30
        d = 1.0 / d
        delta = c * d
        f *= delta
        # Odd step
        num = -(a + m) * (a + b + m) * x / ((a + 2*m) * (a + 2*m + 1))
        d = 1.0 + num * d
        if abs(d) < 1e-30: d = 1e-30
        c = 1.0 + num / c
        if abs(c) < 1e-30: c = 1e-30
        d = 1.0 / d
        delta = c * d
        f *= delta
        if abs(delta - 1.0) < 1e-10:
            break
    return front * f


def _t_cdf(t: float, df: int) -> float:
    """CDF of t-distribution at t with df degrees of freedom."""
    import math
    x = df / (df + t * t)
    p = 0.5 * _regularized_incomplete_beta(x, df / 2.0, 0.5)
    if t > 0:
        return 1.0 - p
    return p


def _t_pvalue_twosided(t: float, df: int) -> float:
    """Two-sided p-value from t-statistic."""
    import math
    if math.isnan(t):
        return float("nan")
    return float(2.0 * min(_t_cdf(abs(t), df), 1.0 - _t_cdf(abs(t), df)))


def _wilcoxon_manual(d: list[float]) -> tuple[float, float]:
    """
    Wilcoxon signed-rank test (manual implementation).
    Uses normal approximation for n >= 10.
    Returns (W, p_two_sided).
    """
    import math
    arr = [x for x in d if x != 0]  # exclude ties with zero
    n = len(arr)
    if n < 5:
        return float("nan"), float("nan")
    # Rank by absolute value
    indexed = sorted(enumerate(arr), key=lambda x: abs(x[1]))
    ranks = [0.0] * len(arr)
    i = 0
    while i < n:
        j = i
        while j < n - 1 and abs(indexed[j+1][1]) == abs(indexed[j][1]):
            j += 1
        avg_rank = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[indexed[k][0]] = avg_rank
        i = j + 1
    W_plus  = sum(ranks[k] for k, x in enumerate(arr) if x > 0)
    W_minus = sum(ranks[k] for k, x in enumerate(arr) if x < 0)
    W = min(W_plus, W_minus)
    # Normal approximation
    mean_W = n * (n + 1) / 4.0
    var_W  = n * (n + 1) * (2 * n + 1) / 24.0
    if var_W <= 0:
        return W, float("nan")
    z = (W - mean_W) / math.sqrt(var_W)
    # Two-sided p from normal CDF
    p = 2.0 * (1.0 - _normal_cdf(abs(z)))
    return float(W), float(p)


def _normal_cdf(z: float) -> float:
    """Standard normal CDF via math.erfc."""
    import math
    return 0.5 * math.erfc(-z / math.sqrt(2.0))


def _paired_ttest(a: list[float], b: list[float]) -> tuple[float, float]:
    """Paired t-test: H0: mean(a-b)=0. Returns (t, p_two_sided)."""
    import math
    d = [ai - bi for ai, bi in zip(a, b)]
    n = len(d)
    if n < 2:
        return float("nan"), float("nan")
    if _HAS_SCIPY:
        result = _scipy_stats.ttest_rel(a, b)
        return float(result.statistic), float(result.pvalue)
    mean_d = sum(d) / n
    var_d  = sum((x - mean_d)**2 for x in d) / (n - 1)
    if var_d == 0:
        return float("nan"), float("nan")
    t = mean_d / math.sqrt(var_d / n)
    p = _t_pvalue_twosided(t, n - 1)
    return float(t), float(p)


def _wilcoxon(d: list[float]) -> tuple[float, float]:
    """Wilcoxon signed-rank test on paired differences."""
    if _HAS_SCIPY:
        import numpy as _np
        arr = _np.array(d)
        if _np.all(arr == 0):
            return float("nan"), 1.0
        try:
            result = _scipy_stats.wilcoxon(arr)
            return float(result.statistic), float(result.pvalue)
        except Exception:
            return float("nan"), float("nan")
    return _wilcoxon_manual(d)


def _bootstrap_ci(d: list[float], n_boot: int = 1000,
                  alpha: float = 0.05) -> tuple[float, float]:
    """Bootstrap percentile 95% CI on mean of paired differences."""
    rng = np.random.default_rng(42)
    arr = np.array(d)
    boot_means = np.array([
        float(np.mean(rng.choice(arr, size=len(arr), replace=True)))
        for _ in range(n_boot)
    ])
    lo = float(np.percentile(boot_means, 100 * alpha / 2))
    hi = float(np.percentile(boot_means, 100 * (1 - alpha / 2)))
    return lo, hi


def _cohens_d(d: list[float]) -> float:
    """Cohen's d for one-sample (paired differences): mean(d)/std(d)."""
    arr = np.array(d)
    std = float(np.std(arr, ddof=1))
    if std == 0:
        return float("nan")
    return float(np.mean(arr) / std)


# ---------------------------------------------------------------------------
# Paired comparison
# ---------------------------------------------------------------------------

BONFERRONI_ALPHA = 0.05 / 3  # 0.0167

def paired_comparison(
    trials: list[dict],
    condition_a: str,     # "spectral"
    condition_b: str,     # e.g. "baseline"
    scenario: str,
    metric: str = "mean_final_hunger",
    n_boot: int = 1000,
) -> dict[str, Any]:
    """
    Compute paired statistics for condition_a vs condition_b within a scenario.

    Pairs are matched by seed. Positive diff = condition_a is WORSE (for hunger).
    """
    # Build seed-indexed dicts
    a_map = {t["seed"]: t[metric] for t in trials
             if t["condition"] == condition_a and t["scenario"] == scenario
             and t.get("valid", True)}
    b_map = {t["seed"]: t[metric] for t in trials
             if t["condition"] == condition_b and t["scenario"] == scenario
             and t.get("valid", True)}

    shared_seeds = sorted(set(a_map) & set(b_map))
    if not shared_seeds:
        return {"error": "no paired trials found", "n": 0}

    a_vals = [a_map[s] for s in shared_seeds]
    b_vals = [b_map[s] for s in shared_seeds]
    d_vals = [a - b for a, b in zip(a_vals, b_vals)]  # positive = a worse

    n = len(d_vals)
    mean_d = float(np.mean(d_vals))
    std_d  = float(np.std(d_vals, ddof=1)) if n > 1 else 0.0
    se_d   = std_d / math.sqrt(n) if n > 0 else 0.0

    t_stat, p_ttest = _paired_ttest(a_vals, b_vals)
    w_stat, p_wilcoxon = _wilcoxon(d_vals)
    boot_lo, boot_hi = _bootstrap_ci(d_vals, n_boot=n_boot)
    analytical_lo = mean_d - 1.96 * se_d
    analytical_hi = mean_d + 1.96 * se_d
    cohens_d = _cohens_d(d_vals)

    sig_ttest    = (not math.isnan(p_ttest)) and p_ttest < BONFERRONI_ALPHA
    sig_wilcoxon = (not math.isnan(p_wilcoxon)) and p_wilcoxon < BONFERRONI_ALPHA
    significant  = sig_ttest and sig_wilcoxon

    # Practical significance: |Cohen's d| >= 0.2 (small effect)
    practical = (not math.isnan(cohens_d)) and abs(cohens_d) >= 0.2

    # Direction: negative mean_d means condition_a (spectral) has lower hunger = BETTER
    if not math.isnan(mean_d):
        direction = "spectral_better" if mean_d < 0 else ("no_difference" if mean_d == 0 else "spectral_worse")
    else:
        direction = "unknown"

    return {
        "condition_a": condition_a,
        "condition_b": condition_b,
        "scenario":    scenario,
        "metric":      metric,
        "n_pairs":     n,
        "shared_seeds": shared_seeds,
        "mean_a":      round(float(np.mean(a_vals)), 6),
        "std_a":       round(float(np.std(a_vals, ddof=1)) if n > 1 else 0.0, 6),
        "mean_b":      round(float(np.mean(b_vals)), 6),
        "std_b":       round(float(np.std(b_vals, ddof=1)) if n > 1 else 0.0, 6),
        "mean_diff":   round(mean_d, 6),     # a - b; negative = a better
        "std_diff":    round(std_d, 6),
        "ci_95_analytical": [round(analytical_lo, 6), round(analytical_hi, 6)],
        "ci_95_bootstrap":  [round(boot_lo, 6), round(boot_hi, 6)],
        "t_statistic":      round(t_stat, 4) if not math.isnan(t_stat) else None,
        "p_ttest_raw":      round(p_ttest, 6) if not math.isnan(p_ttest) else None,
        "p_ttest_bonferroni_corrected": round(min(p_ttest * 3, 1.0), 6) if not math.isnan(p_ttest) else None,
        "w_statistic":      round(w_stat, 4) if not math.isnan(w_stat) else None,
        "p_wilcoxon_raw":   round(p_wilcoxon, 6) if not math.isnan(p_wilcoxon) else None,
        "p_wilcoxon_bonferroni_corrected": round(min(p_wilcoxon * 3, 1.0), 6) if not math.isnan(p_wilcoxon) else None,
        "cohens_d":         round(cohens_d, 4) if not math.isnan(cohens_d) else None,
        "significant_both_tests": significant,
        "practically_significant": practical,
        "direction":        direction,
        "bonferroni_alpha": BONFERRONI_ALPHA,
        "scipy_available":  _HAS_SCIPY,
    }


# ---------------------------------------------------------------------------
# Tau scan analysis
# ---------------------------------------------------------------------------

def analyse_tau_scan(trials: list[dict]) -> dict[str, Any]:
    tau_vals = sorted(set(t["tau"] for t in trials if t.get("condition") == "spectral"))
    result = {}
    for tau in tau_vals:
        t_list = [t for t in trials
                  if t.get("condition") == "spectral"
                  and t.get("tau") == tau
                  and t.get("valid", True)]
        if not t_list:
            continue
        h = [t["mean_final_hunger"] for t in t_list]
        c = [t["coordination_rate"] for t in t_list]
        ts = [t["task_success_rate"] for t in t_list]
        result[str(tau)] = {
            "n":              len(h),
            "mean_hunger":    round(float(np.mean(h)), 6),
            "std_hunger":     round(float(np.std(h, ddof=1)) if len(h) > 1 else 0.0, 6),
            "mean_coord":     round(float(np.mean(c)), 6),
            "std_coord":      round(float(np.std(c, ddof=1)) if len(c) > 1 else 0.0, 6),
            "mean_task_succ": round(float(np.mean(ts)), 6),
        }
    return result


# ---------------------------------------------------------------------------
# Trade-off analysis
# ---------------------------------------------------------------------------

def coordination_hunger_tradeoff(trials: list[dict],
                                  scenario: str) -> list[dict]:
    rows = []
    for cond in ["baseline", "legacy_q", "spectral", "ablation"]:
        t_list = [t for t in trials
                  if t["condition"] == cond and t["scenario"] == scenario
                  and t.get("valid", True)]
        if not t_list:
            continue
        rows.append({
            "condition":   cond,
            "mean_coord":  round(float(np.mean([t["coordination_rate"] for t in t_list])), 4),
            "mean_hunger": round(float(np.mean([t["mean_final_hunger"] for t in t_list])), 4),
            "mean_task_success": round(float(np.mean([t["task_success_rate"] for t in t_list])), 4),
        })
    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_analysis(input_path: str) -> dict[str, Any]:
    with open(input_path) as f:
        trials = json.load(f)

    print(f"  Loaded {len(trials)} trial records")
    n_invalid = sum(1 for t in trials if not t.get("valid", True))
    if n_invalid:
        print(f"  [WARN] {n_invalid} invalid trials excluded")

    scenarios = sorted(set(t["scenario"] for t in trials
                           if t.get("scenario") in ("stable", "dynamic", "disrupted")))
    comparisons = ["baseline", "legacy_q", "ablation"]

    all_comparisons: dict[str, Any] = {}
    for scenario in scenarios:
        all_comparisons[scenario] = {}
        for comp in comparisons:
            key = f"spectral_vs_{comp}"
            all_comparisons[scenario][key] = paired_comparison(
                trials, "spectral", comp, scenario
            )

    tau_analysis = analyse_tau_scan(trials)
    tradeoffs    = {s: coordination_hunger_tradeoff(trials, s) for s in scenarios}

    results = {
        "n_trials_loaded":  len(trials),
        "n_invalid":        n_invalid,
        "bonferroni_alpha": BONFERRONI_ALPHA,
        "scipy_available":  _HAS_SCIPY,
        "primary_metric":   "mean_final_hunger",
        "metric_direction": "lower_is_better",
        "comparisons":      all_comparisons,
        "tau_scan":         tau_analysis,
        "tradeoffs":        tradeoffs,
    }

    # Print summary
    print(f"\n  Bonferroni alpha = {BONFERRONI_ALPHA:.4f}")
    print(f"  Scipy: {'available' if _HAS_SCIPY else 'NOT available'}\n")

    for scenario in scenarios:
        print(f"  === Scenario: {scenario} ===")
        for comp in comparisons:
            key = f"spectral_vs_{comp}"
            r = all_comparisons[scenario][key]
            if "error" in r:
                print(f"    spectral vs {comp}: {r['error']}")
                continue
            sig = "✓ SIG" if r["significant_both_tests"] else "~ n.s."
            prac = "PRACTICAL" if r["practically_significant"] else "small"
            dir_ = r["direction"]
            d = r["cohens_d"]
            md = r["mean_diff"]
            ci = r["ci_95_bootstrap"]
            pt = r["p_ttest_raw"]
            print(f"    spectral vs {comp:>8}: mean_diff={md:+.4f} "
                  f"[{ci[0]:+.4f},{ci[1]:+.4f}]  "
                  f"d={d:+.3f}  p={pt:.4f}  {sig}  {prac}  {dir_}")
        print()

    print("  === Tau Scan ===")
    print(f"  {'tau':>6}  {'n':>4}  {'hunger(mean)':>12}  {'hunger(std)':>11}  {'coord%':>7}")
    for tau_str, v in sorted(tau_analysis.items(), key=lambda x: float(x[0])):
        print(f"  {float(tau_str):>6.2f}  {v['n']:>4}  "
              f"{v['mean_hunger']:>12.4f}  {v['std_hunger']:>11.4f}  "
              f"{v['mean_coord']:>7.1%}")

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="phase10_raw_trials.json")
    args = parser.parse_args()

    input_path = os.path.join(_HERE, args.input)
    if not os.path.exists(input_path):
        print(f"  ERROR: {input_path} not found. Run experiment_runner.py first.")
        sys.exit(1)

    print(f"\n--- Phase 10 Statistical Analysis ---")
    results = run_analysis(input_path)

    out_path = os.path.join(_HERE, "phase10_analysis_results.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Analysis saved → {out_path}")


if __name__ == "__main__":
    main()
