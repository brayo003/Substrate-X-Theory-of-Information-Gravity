"""
p1_regime_analysis.py — Regime analysis for Phase 1 Transport Strategy Matrix.

Reads the cached Q series parquet (built by p1_data_stream.build_q_series).
Outputs:
  - regime_transition_statistics.csv  (persistence, entropy per regime)
  - markov_matrix.csv                 (5×5 transition probability matrix)
  - regime_transitions_catalog.csv    (every regime episode)
"""

import sys
import warnings
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

_HERE = Path(__file__).resolve().parent
_CE   = _HERE.parents[1]
for p in [str(_CE), str(_HERE)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from p1_checkpoint import (
    RESULTS_DIR, q_series_path,
    mark_regime_analysis_complete,
)
from p1_data_stream import classify_q_global

REGIMES_5 = [
    "Deep_Incoherent",
    "Mod_Incoherent",
    "Transition",
    "Weak_Coherent",
    "Strong_Coherent",
]

REGIME_IDX = {r: i for i, r in enumerate(REGIMES_5)}


# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════

def _shannon_entropy(counts: np.ndarray) -> float:
    """Shannon entropy in bits from counts array."""
    total = counts.sum()
    if total == 0:
        return 0.0
    probs = counts / total
    probs = probs[probs > 0]
    return float(-np.sum(probs * np.log2(probs)))


def _run_lengths(labels: np.ndarray) -> dict:
    """Return dict of {regime: array_of_run_lengths}."""
    runs: dict = {r: [] for r in REGIMES_5}
    if len(labels) == 0:
        return runs
    cur = labels[0]
    length = 1
    for v in labels[1:]:
        if v == cur:
            length += 1
        else:
            runs[cur].append(length)
            cur = v
            length = 1
    runs[cur].append(length)
    return {r: np.array(v, dtype=float) for r, v in runs.items()}


# ═══════════════════════════════════════════════════════════════════════════
# Markov transition matrix (5×5)
# ═══════════════════════════════════════════════════════════════════════════

def _build_markov_matrix(labels: np.ndarray) -> pd.DataFrame:
    """Build 5×5 Markov transition probability matrix."""
    n_r = len(REGIMES_5)
    counts = np.zeros((n_r, n_r), dtype=int)
    for i in range(len(labels) - 1):
        fr = REGIME_IDX.get(labels[i])
        to = REGIME_IDX.get(labels[i + 1])
        if fr is not None and to is not None:
            counts[fr, to] += 1
    row_sums = counts.sum(axis=1, keepdims=True)
    row_sums = np.where(row_sums == 0, 1, row_sums)
    prob = counts / row_sums
    return pd.DataFrame(
        prob,
        index=[f"from_{r}" for r in REGIMES_5],
        columns=[f"to_{r}" for r in REGIMES_5],
    )


# ═══════════════════════════════════════════════════════════════════════════
# Transition catalog (every regime episode)
# ═══════════════════════════════════════════════════════════════════════════

def _build_transition_catalog(labels: np.ndarray, index: pd.DatetimeIndex,
                               Q_arr: np.ndarray) -> pd.DataFrame:
    """Build a DataFrame of every regime episode."""
    episodes = []
    if len(labels) == 0:
        return pd.DataFrame()
    cur = labels[0]
    start = 0
    for i in range(1, len(labels)):
        if labels[i] != cur:
            ep_Q = Q_arr[start:i]
            episodes.append({
                "regime"     : cur,
                "start_bar"  : start,
                "end_bar"    : i - 1,
                "duration"   : i - start,
                "start_time" : index[start],
                "end_time"   : index[i - 1],
                "mean_Q"     : float(np.nanmean(ep_Q)),
                "std_Q"      : float(np.nanstd(ep_Q)),
                "next_regime": labels[i],
            })
            cur = labels[i]
            start = i
    # Final episode
    ep_Q = Q_arr[start:]
    episodes.append({
        "regime"     : cur,
        "start_bar"  : start,
        "end_bar"    : len(labels) - 1,
        "duration"   : len(labels) - start,
        "start_time" : index[start],
        "end_time"   : index[-1],
        "mean_Q"     : float(np.nanmean(ep_Q)),
        "std_Q"      : float(np.nanstd(ep_Q)),
        "next_regime": "—",
    })
    return pd.DataFrame(episodes)


# ═══════════════════════════════════════════════════════════════════════════
# Main analysis
# ═══════════════════════════════════════════════════════════════════════════

def run_regime_analysis(
    q_quantiles: Dict,
    manifest: Dict,
    verbose: bool = True,
) -> tuple:
    """
    Load Q series, classify into 5 regimes, compute all statistics.
    Returns (transition_stats_df, markov_df, catalog_df).
    """
    q_path = q_series_path()
    if not q_path.exists():
        raise FileNotFoundError(f"Q series not found: {q_path}")

    if verbose:
        print("  Loading Q series …", flush=True)
    q_series = pd.read_parquet(q_path)
    q_series.sort_index(inplace=True)

    Q_arr = q_series["Q"].values
    idx   = q_series.index

    if verbose:
        print(f"  Q series: {len(Q_arr):,} bars", flush=True)

    # Classify with global thresholds
    q05 = q_quantiles["q05"]
    q95 = q_quantiles["q95"]
    labels = classify_q_global(Q_arr, q05=q05, q95=q95)

    if verbose:
        for r in REGIMES_5:
            frac = (labels == r).mean()
            print(f"    {r:<22} {frac:.4f}", flush=True)

    # ── Run lengths / persistence ──────────────────────────────────────────
    runs = _run_lengths(labels)

    # Counts
    counts = np.array([(labels == r).sum() for r in REGIMES_5])
    total  = len(labels)
    entropy = _shannon_entropy(counts)
    max_entropy = np.log2(len(REGIMES_5))  # uniform
    norm_entropy = entropy / max_entropy if max_entropy > 0 else 0.0

    # Transition rate (transitions per bar)
    n_trans = int(np.sum(labels[:-1] != labels[1:]))
    trans_per_bar  = n_trans / max(total - 1, 1)
    bars_per_hour  = 60 / 5  # 5-min bars
    trans_per_hour = trans_per_bar * bars_per_hour

    # ── Regime statistics table ────────────────────────────────────────────
    stab_rows = []
    for r in REGIMES_5:
        r_runs = runs[r]
        n_bars  = int((labels == r).sum())
        n_ep    = int(len(r_runs))
        frac    = float(n_bars) / total

        mean_b  = float(r_runs.mean())   if n_ep > 0 else 0.0
        median_b= float(np.median(r_runs)) if n_ep > 0 else 0.0
        std_b   = float(r_runs.std())    if n_ep > 0 else 0.0
        max_b   = int(r_runs.max())      if n_ep > 0 else 0
        mean_m  = mean_b * 5.0

        # P(stay) from Markov diagonal
        if n_ep > 0 and n_bars > 0:
            # Count self-transitions
            idx_r   = REGIME_IDX[r]
            n_self  = int(np.sum((labels[:-1] == r) & (labels[1:] == r)))
            n_leave = int(np.sum((labels[:-1] == r) & (labels[1:] != r)))
            p_stay  = n_self / max(n_self + n_leave, 1)
        else:
            p_stay = 0.0

        # Geometric null: E[run] = 1 / p_switch
        p_switch = 1.0 - p_stay
        geo_null = 1.0 / (p_switch + 1e-12)
        persistent = bool(mean_b > 1.5 * geo_null) or bool(p_stay > 0.7)

        stab_rows.append({
            "regime"           : r,
            "time_fraction"    : frac,
            "bar_count"        : n_bars,
            "n_episodes"       : n_ep,
            "mean_bars"        : mean_b,
            "median_bars"      : median_b,
            "std_bars"         : std_b,
            "max_bars"         : max_b,
            "mean_minutes"     : mean_m,
            "p_stay"           : p_stay,
            "geometric_null"   : geo_null,
            "persistent"       : persistent,
            "entropy"          : entropy,
            "normalized_entropy": norm_entropy,
            "trans_per_hour"   : trans_per_hour,
        })

    stab_df = pd.DataFrame(stab_rows)

    # ── Markov matrix ──────────────────────────────────────────────────────
    markov_df = _build_markov_matrix(labels)

    # ── Transition catalog ─────────────────────────────────────────────────
    if verbose:
        print("  Building transition catalog …", flush=True)
    catalog_df = _build_transition_catalog(labels, idx, Q_arr)

    if verbose:
        print(f"  Entropy: {entropy:.4f} bits (norm: {norm_entropy:.3f})")
        print(f"  Transitions/hr: {trans_per_hour:.4f}")
        print(f"  Catalog entries: {len(catalog_df)}", flush=True)

    # ── Save outputs ───────────────────────────────────────────────────────
    stab_df.to_csv(RESULTS_DIR / "regime_transition_statistics.csv", index=False)
    markov_df.to_csv(RESULTS_DIR / "markov_matrix.csv")
    catalog_df.to_csv(RESULTS_DIR / "regime_transitions_catalog.csv", index=False)

    mark_regime_analysis_complete(manifest)
    if verbose:
        print("  Regime analysis complete.", flush=True)

    return stab_df, markov_df, catalog_df
