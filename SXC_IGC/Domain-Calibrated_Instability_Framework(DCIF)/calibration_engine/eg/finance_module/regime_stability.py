"""
regime_stability.py — Transport Regime Stability Analysis for Phase 1 Validation.

Computes for each of the 5 Q regimes:
  - Time fraction spent in each regime
  - Transition frequency (transitions per hour)
  - Average persistence (mean run-length in bars and minutes)
  - Shannon entropy of regime sequence
  - 5×5 Markov transition probability matrix
  - Steady-state distribution
  - Episode catalog with timestamps
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple

from execution_simulator import REGIMES_5, classify_q_regimes

BAR_MINUTES = 5


def _run_lengths(regimes: np.ndarray) -> Dict[str, np.ndarray]:
    runs = {r: [] for r in REGIMES_5}
    if len(regimes) == 0:
        return {r: np.array([]) for r in REGIMES_5}
    cur = regimes[0]; count = 1
    for r in regimes[1:]:
        if r == cur:
            count += 1
        else:
            runs[cur].append(count); cur = r; count = 1
    runs[cur].append(count)
    return {r: np.array(v, dtype=float) for r, v in runs.items()}


def compute_markov_matrix(regimes: np.ndarray) -> pd.DataFrame:
    idx = {r: i for i, r in enumerate(REGIMES_5)}
    trans = np.zeros((5, 5), dtype=int)
    for i in range(len(regimes) - 1):
        fi = idx.get(regimes[i], 2)
        ti = idx.get(regimes[i + 1], 2)
        trans[fi, ti] += 1
    row_sums = trans.sum(axis=1, keepdims=True)
    row_sums = np.where(row_sums == 0, 1, row_sums)
    prob = trans / row_sums
    return pd.DataFrame(prob,
        index=[f'from_{r}' for r in REGIMES_5],
        columns=[f'to_{r}'   for r in REGIMES_5])


def _steady_state(markov: pd.DataFrame) -> np.ndarray:
    P = markov.values
    vals, vecs = np.linalg.eig(P.T)
    idx = np.argmin(np.abs(vals - 1.0))
    ss  = np.abs(np.real(vecs[:, idx]))
    return ss / (ss.sum() + 1e-12)


def _entropy(regimes: np.ndarray) -> float:
    _, counts = np.unique(regimes, return_counts=True)
    p = counts / counts.sum()
    return float(-np.sum(p * np.log2(p + 1e-12)))


def regime_statistics(df: pd.DataFrame) -> dict:
    Q       = df['tr_Q'].values
    regimes = classify_q_regimes(Q)
    n       = len(regimes)

    fractions = {r: int((regimes == r).sum()) / n for r in REGIMES_5}
    counts    = {r: int((regimes == r).sum()) for r in REGIMES_5}
    run_data  = _run_lengths(regimes)

    run_stats = {}
    for r in REGIMES_5:
        arr = run_data[r]
        if len(arr) == 0:
            run_stats[r] = dict(n_episodes=0, mean_bars=0, median_bars=0,
                                std_bars=0, max_bars=0, mean_minutes=0,
                                p25_bars=0, p75_bars=0)
        else:
            run_stats[r] = dict(
                n_episodes   = len(arr),
                mean_bars    = float(arr.mean()),
                median_bars  = float(np.median(arr)),
                std_bars     = float(arr.std()),
                max_bars     = int(arr.max()),
                mean_minutes = float(arr.mean() * BAR_MINUTES),
                p25_bars     = float(np.percentile(arr, 25)),
                p75_bars     = float(np.percentile(arr, 75)),
            )

    n_trans      = sum(1 for i in range(1, n) if regimes[i] != regimes[i - 1])
    total_hours  = n * BAR_MINUTES / 60.0
    trans_per_hr = n_trans / (total_hours + 1e-12)

    markov = compute_markov_matrix(regimes)
    try:
        ss = _steady_state(markov)
    except Exception:
        ss = np.full(5, 0.2)

    entropy     = _entropy(regimes)
    norm_entropy = entropy / np.log2(5)

    persistence = {}
    for i, r in enumerate(REGIMES_5):
        p_stay = float(markov.iloc[i, i])
        geom   = 1.0 / (1.0 - p_stay + 1e-12)
        actual = run_stats[r]['mean_bars']
        persistence[r] = dict(p_stay=p_stay, geometric_null=geom,
                               actual_mean=actual,
                               persistent=actual > 1.5 * geom)

    return dict(n_bars=n, fractions=fractions, counts=counts,
                run_stats=run_stats, n_transitions=n_trans,
                trans_per_hour=float(trans_per_hr),
                entropy=float(entropy), normalized_entropy=float(norm_entropy),
                markov_matrix=markov,
                steady_state=dict(zip(REGIMES_5, ss.tolist())),
                persistence=persistence)


def regime_stability_to_csv(stats: dict) -> pd.DataFrame:
    rows = []
    for r in REGIMES_5:
        rs = stats['run_stats'][r]
        ps = stats['persistence'].get(r, {})
        rows.append(dict(
            regime           = r,
            time_fraction    = stats['fractions'].get(r, 0),
            bar_count        = stats['counts'].get(r, 0),
            n_episodes       = rs.get('n_episodes', 0),
            mean_bars        = rs.get('mean_bars', 0),
            median_bars      = rs.get('median_bars', 0),
            std_bars         = rs.get('std_bars', 0),
            max_bars         = rs.get('max_bars', 0),
            mean_minutes     = rs.get('mean_minutes', 0),
            p_stay           = ps.get('p_stay', 0),
            geometric_null   = ps.get('geometric_null', 0),
            persistent       = ps.get('persistent', False),
            entropy          = stats['entropy'],
            normalized_entropy = stats['normalized_entropy'],
            trans_per_hour   = stats['trans_per_hour'],
        ))
    return pd.DataFrame(rows)


def regime_transitions_catalog(df: pd.DataFrame) -> pd.DataFrame:
    Q       = df['tr_Q'].values
    regimes = classify_q_regimes(Q)
    episodes = []
    if len(regimes) == 0:
        return pd.DataFrame()
    start = 0; cur = regimes[0]
    for i in range(1, len(regimes)):
        if regimes[i] != cur:
            q_sl = Q[start:i]
            episodes.append(dict(
                regime=cur, start_bar=start, end_bar=i-1,
                duration=i-start, duration_min=(i-start)*BAR_MINUTES,
                start_time=df.index[start], end_time=df.index[i-1],
                mean_Q=float(np.nanmean(q_sl)),
                min_Q=float(np.nanmin(q_sl)), max_Q=float(np.nanmax(q_sl)),
            ))
            cur = regimes[i]; start = i
    q_sl = Q[start:]
    episodes.append(dict(
        regime=cur, start_bar=start, end_bar=len(regimes)-1,
        duration=len(regimes)-start,
        duration_min=(len(regimes)-start)*BAR_MINUTES,
        start_time=df.index[start], end_time=df.index[-1],
        mean_Q=float(np.nanmean(q_sl)),
        min_Q=float(np.nanmin(q_sl)), max_Q=float(np.nanmax(q_sl)),
    ))
    return pd.DataFrame(episodes)
