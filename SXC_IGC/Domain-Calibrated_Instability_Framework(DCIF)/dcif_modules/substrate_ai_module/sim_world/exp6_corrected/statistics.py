"""Paired statistical procedures for corrected Task 6 (Gate G10)."""
from __future__ import annotations

import math
from typing import Any

import numpy as np

try:
    from scipy import stats as _scipy_stats
except ImportError:  # pragma: no cover — venv may lack scipy
    _scipy_stats = None


def _ttest_rel(b: np.ndarray, a: np.ndarray) -> tuple[float, float]:
    """Paired t-test of b − a. Returns (t_statistic, two-sided p-value)."""
    if _scipy_stats is not None:
        res = _scipy_stats.ttest_rel(b, a)
        return float(res.statistic), float(res.pvalue)
    diffs = np.asarray(b, dtype=float) - np.asarray(a, dtype=float)
    n = len(diffs)
    if n < 2:
        return float("nan"), 1.0
    mean_d = float(np.mean(diffs))
    sd_d = float(np.std(diffs, ddof=1))
    if sd_d < 1e-15:
        if abs(mean_d) < 1e-15:
            return 0.0, 1.0
        return float("inf"), 0.0
    t_stat = mean_d / (sd_d / math.sqrt(n))
    df = n - 1
    # Two-sided p from Student-t CDF via regularized incomplete beta (numpy-only).
    x = df / (df + t_stat * t_stat)
    # I_x(df/2, 1/2) ≈ incomplete beta; use continued series / scipy-free approx via
    # relationship P(|T|>|t|) = betainc(df/2, 0.5, x). Implement via numpy if available
    # through math.erf for large df, else incomplete-beta continued fraction.
    p = _student_t_sf_two_sided(abs(t_stat), df)
    return float(t_stat), float(p)


def _betainc_contfrac(a: float, b: float, x: float, max_iter: int = 200) -> float:
    """Regularized incomplete beta I_x(a,b) via Lentz continued fraction."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    # Use symmetry if needed for faster convergence
    if x > (a + 1.0) / (a + b + 2.0):
        return 1.0 - _betainc_contfrac(b, a, 1.0 - x, max_iter=max_iter)
    # Front factor: x^a (1-x)^b / (a B(a,b)) * contfrac
    lbeta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    front = math.exp(a * math.log(x) + b * math.log1p(-x) - lbeta) / a
    # Modified Lentz
    tiny = 1e-30
    f = tiny
    c = tiny
    d = 0.0
    for m in range(1, max_iter + 1):
        # odd / even numerators of continued fraction for incomplete beta
        if m % 2 == 0:
            m2 = m // 2
            num = (m2 * (b - m2) * x) / ((a + 2 * m2 - 1) * (a + 2 * m2))
        else:
            m2 = (m - 1) // 2
            num = -((a + m2) * (a + b + m2) * x) / ((a + 2 * m2) * (a + 2 * m2 + 1))
        d = 1.0 + num * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + num / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = c * d
        f *= delta
        if abs(delta - 1.0) < 1e-12:
            break
    return front * f


def _student_t_sf_two_sided(t_abs: float, df: float) -> float:
    """Two-sided survival function for Student-t."""
    if not math.isfinite(t_abs):
        return 0.0
    if t_abs == 0.0:
        return 1.0
    x = df / (df + t_abs * t_abs)
    # P(|T| > t) = I_x(df/2, 1/2)
    return float(_betainc_contfrac(0.5 * df, 0.5, x))


def paired_mean_diff_ci(diffs: np.ndarray, alpha: float = 0.05) -> tuple[float, float]:
    """Bootstrap 95% CI for mean of paired differences."""
    diffs = np.asarray(diffs, dtype=float)
    n = len(diffs)
    if n < 2:
        m = float(diffs[0]) if n == 1 else 0.0
        return m, m
    rng = np.random.default_rng(42)
    boots = np.array([np.mean(rng.choice(diffs, size=n, replace=True)) for _ in range(2000)])
    return float(np.percentile(boots, 100 * alpha / 2)), float(np.percentile(boots, 100 * (1 - alpha / 2)))


def paired_analysis(a: list[float], b: list[float], alpha: float = 0.05) -> dict[str, Any]:
    """
    Paired comparison of b − a (same seeds).

    Effect size is paired d_z = mean(diff) / sd(diff), NOT unpaired Cohen's d.
    """
    a_arr = np.asarray(a, dtype=float)
    b_arr = np.asarray(b, dtype=float)
    if len(a_arr) != len(b_arr):
        raise ValueError("paired_analysis requires equal-length seed-matched vectors")
    diffs = b_arr - a_arr
    n = len(diffs)
    mean_diff = float(np.mean(diffs)) if n else 0.0
    sd_diff = float(np.std(diffs, ddof=1)) if n > 1 else 0.0
    d_z = mean_diff / sd_diff if sd_diff > 1e-15 else (0.0 if abs(mean_diff) < 1e-15 else float("inf"))
    if n >= 2 and sd_diff > 1e-15:
        t_stat, p_value = _ttest_rel(b_arr, a_arr)
    elif n >= 2 and abs(mean_diff) < 1e-15:
        t_stat, p_value = 0.0, 1.0
    elif n >= 2:
        t_stat, p_value = float("inf"), 0.0
    else:
        t_stat, p_value = float("nan"), 1.0

    # Paired permutation p-value (two-sided) as robustness check
    if n >= 2:
        rng = np.random.default_rng(123)
        obs = abs(mean_diff)
        signs = rng.choice([-1.0, 1.0], size=(5000, n))
        null = np.abs(np.mean(signs * diffs, axis=1))
        p_perm = float((np.sum(null >= obs) + 1) / (len(null) + 1))
    else:
        p_perm = 1.0

    lo, hi = paired_mean_diff_ci(diffs, alpha=alpha)
    return {
        "n": n,
        "mean_a": float(np.mean(a_arr)) if n else 0.0,
        "mean_b": float(np.mean(b_arr)) if n else 0.0,
        "mean_diff": mean_diff,
        "sd_diff": sd_diff,
        "d_z": float(d_z) if math.isfinite(d_z) else None,
        "t_statistic": t_stat if math.isfinite(t_stat) else None,
        "p_value": p_value,
        "p_permutation": p_perm,
        "diff_ci95": [lo, hi],
        "scipy_available": _scipy_stats is not None,
    }


def bonferroni_adjust(p_values: list[float], n_comparisons: int) -> list[float]:
    return [min(1.0, float(p) * n_comparisons) for p in p_values]


def classification_metrics(y_true: list[int], y_pred: list[int],
                           positive: int = 1) -> dict[str, float]:
    yt = np.asarray(y_true)
    yp = np.asarray(y_pred)
    tp = int(np.sum((yt == positive) & (yp == positive)))
    fp = int(np.sum((yt != positive) & (yp == positive)))
    fn = int(np.sum((yt == positive) & (yp != positive)))
    tn = int(np.sum((yt != positive) & (yp != positive)))
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return {
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "precision": prec, "recall": rec, "f1": f1,
        "fpr": fp / (fp + tn) if (fp + tn) else 0.0,
        "fnr": fn / (fn + tp) if (fn + tp) else 0.0,
        "accuracy": float(np.mean(yt == yp)) if len(yt) else 0.0,
    }
