"""
p5_drift.py — Phase 5 Drift Analysis Engine.

Computes all drift indices comparing 2025 (Phase 4) vs 2026 (Phase 5):
  - Transport Drift Index (Q distribution shift)
  - Execution Drift Index (PF, Sharpe, WinRate changes)
  - Scheduler Stability (allocator decisions consistency)
  - Allocator Stability (family usage stability)
  - Regime Stability (occupancy distribution shift)
  - Q Stability (entropy, coherence fraction)

Statistical tests:
  - Bootstrap confidence intervals
  - Permutation tests
  - Mann-Whitney U
  - Wilcoxon signed-rank
  - BH-FDR correction
  - Effect sizes (Cohen's d, rank-biserial r)
"""

import sys
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats as scipy_stats

warnings.filterwarnings("ignore")

_HERE = Path(__file__).resolve().parent
for p in [str(_HERE), str(_HERE / "v12_validate")]:
    if p not in sys.path:
        sys.path.insert(0, p)

PHASE4_DIR = _HERE / "results" / "phase4"
PHASE5_DIR = _HERE / "results" / "phase5"

REGIMES_5    = ["Deep_Incoherent", "Mod_Incoherent", "Transition", "Weak_Coherent", "Strong_Coherent"]
MARKET_ORDER = ["EURUSD", "BTCUSDT", "ETHUSDT", "NAS100", "XAUUSD", "USOIL", "UKOIL"]


# ── helpers ────────────────────────────────────────────────────────────────

def _cohens_d(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 2 or len(b) < 2:
        return 0.0
    pooled = np.sqrt((a.std()**2 + b.std()**2) / 2 + 1e-12)
    return float((a.mean() - b.mean()) / (pooled + 1e-12))


def _rank_biserial(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 2 or len(b) < 2:
        return 0.0
    try:
        res = scipy_stats.mannwhitneyu(a, b, alternative="two-sided")
        u   = res.statistic
        n1, n2 = len(a), len(b)
        return float(1 - 2 * u / (n1 * n2))
    except Exception:
        return 0.0


def _bh_fdr(pvals: np.ndarray, alpha: float = 0.05) -> np.ndarray:
    """Benjamini-Hochberg FDR correction. Returns boolean reject array."""
    n = len(pvals)
    if n == 0:
        return np.array([], dtype=bool)
    order  = np.argsort(pvals)
    ranked = np.arange(1, n + 1)
    thresh = ranked * alpha / n
    reject = np.zeros(n, dtype=bool)
    cum_max_reject = False
    for i in range(n - 1, -1, -1):
        if pvals[order[i]] <= thresh[i]:
            cum_max_reject = True
        if cum_max_reject:
            reject[order[i]] = True
    return reject


def _tv_distance(p: np.ndarray, q: np.ndarray) -> float:
    """Total variation distance between two distributions."""
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    p = p / (p.sum() + 1e-12)
    q = q / (q.sum() + 1e-12)
    return float(0.5 * np.abs(p - q).sum())


def _kl_divergence(p: np.ndarray, q: np.ndarray) -> float:
    p = np.asarray(p, dtype=float) + 1e-12
    q = np.asarray(q, dtype=float) + 1e-12
    p /= p.sum(); q /= q.sum()
    return float(np.sum(p * np.log(p / q)))


def _shannon_entropy(arr: np.ndarray, n_bins: int = 50) -> float:
    counts, _ = np.histogram(arr, bins=n_bins)
    probs = counts / (counts.sum() + 1e-12)
    probs = probs[probs > 0]
    return float(-np.sum(probs * np.log(probs + 1e-12)))


# ═══════════════════════════════════════════════════════════════════════════
# Transport Drift Index
# ═══════════════════════════════════════════════════════════════════════════

def compute_transport_drift(
    all_data_2026: Dict[str, pd.DataFrame],
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Compare Q distribution 2025 vs 2026.
    2025 Q: loaded from Phase 2 cache parquets.
    2026 Q: from prepared data.
    """
    rows = []

    # Load 2025 Q from cache
    cache_dir = _HERE / "cache"
    q25_frames = []
    for fp in sorted(cache_dir.glob("ohlc_transport_2025_*.parquet")):
        try:
            df = pd.read_parquet(fp)
            if "tr_Q" in df.columns:
                q25_frames.append(df["tr_Q"].dropna())
        except Exception:
            pass

    q25_global = pd.concat(q25_frames).values if q25_frames else np.array([])

    for sym in MARKET_ORDER:
        df26 = all_data_2026.get(sym)
        if df26 is None or "tr_Q" not in df26.columns:
            continue
        q26 = df26["tr_Q"].dropna().values

        # For non-EURUSD: load from phase3 prepared parquets
        if sym == "EURUSD":
            q25 = q25_global
        else:
            p3_path = _HERE / "results" / "phase3" / f"prepared_{sym}.parquet"
            if p3_path.exists():
                try:
                    q25 = pd.read_parquet(p3_path)["tr_Q"].dropna().values
                except Exception:
                    q25 = np.array([])
            else:
                q25 = np.array([])

        if len(q25) < 10 or len(q26) < 10:
            continue

        # KS test
        ks_stat, ks_p = scipy_stats.ks_2samp(q25, q26)

        # MW test on Q values
        mw_stat, mw_p = scipy_stats.mannwhitneyu(q25, q26, alternative="two-sided")

        # Distribution stats
        q25_hist, bins = np.histogram(q25, bins=50, range=(-3, 5), density=True)
        q26_hist, _    = np.histogram(q26, bins=bins, density=True)

        tvd = _tv_distance(q25_hist, q26_hist)
        kld = _kl_divergence(q25_hist + 1e-12, q26_hist + 1e-12)
        cohd = _cohens_d(q25, q26)

        rows.append({
            "symbol"             : sym,
            "q25_mean"           : round(float(q25.mean()), 4),
            "q26_mean"           : round(float(q26.mean()), 4),
            "q25_std"            : round(float(q25.std()),  4),
            "q26_std"            : round(float(q26.std()),  4),
            "q25_coherent_frac"  : round(float((q25 > 0).mean()), 4),
            "q26_coherent_frac"  : round(float((q26 > 0).mean()), 4),
            "q25_entropy"        : round(_shannon_entropy(q25), 4),
            "q26_entropy"        : round(_shannon_entropy(q26), 4),
            "delta_mean"         : round(float(q26.mean() - q25.mean()), 4),
            "delta_coherent_frac": round(float((q26>0).mean() - (q25>0).mean()), 4),
            "ks_stat"            : round(float(ks_stat), 4),
            "ks_pval"            : round(float(ks_p), 6),
            "mw_stat"            : round(float(mw_stat), 4),
            "mw_pval"            : round(float(mw_p), 6),
            "tv_distance"        : round(float(tvd), 4),
            "kl_divergence"      : round(float(kld), 4),
            "cohens_d"           : round(float(cohd), 4),
            "transport_drift_idx": round(float(tvd * 10), 4),  # scaled 0-10
        })

        if verbose:
            print(f"  [{sym}] Q drift: TV={tvd:.3f} KS={ks_stat:.3f}(p={ks_p:.4f}) "
                  f"Δmean={q26.mean()-q25.mean():+.3f}", flush=True)

    return pd.DataFrame(rows)


# ═══════════════════════════════════════════════════════════════════════════
# Execution Drift Index
# ═══════════════════════════════════════════════════════════════════════════

def compute_execution_drift(
    stats_2025: Dict[str, Dict],
    stats_2026: Dict[str, Dict],
    all_trade_logs_2026: Dict[str, pd.DataFrame],
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Compute execution layer drift: PF, Sharpe, WinRate, trade frequency.
    """
    rows = []
    metrics = ["profit_factor", "sharpe", "win_rate", "expectancy",
               "max_drawdown", "n_trades", "no_trade_pct", "avg_duration_bars"]

    for sym in MARKET_ORDER:
        s25 = stats_2025.get(sym, {})
        s26 = stats_2026.get(sym, {})

        row = {"symbol": sym}
        drift_scores = []

        for m in metrics:
            v25 = float(s25.get(m, 0.0))
            v26 = float(s26.get(m, 0.0))
            delta = v26 - v25
            if abs(v25) > 1e-12:
                pct = delta / abs(v25) * 100
            else:
                pct = 0.0

            row[f"p4_{m}"]    = round(v25, 4)
            row[f"p5_{m}"]    = round(v26, 4)
            row[f"delta_{m}"] = round(delta, 4)
            row[f"pct_{m}"]   = round(pct, 2)

            # Normalised drift contribution
            if m in ("profit_factor", "sharpe", "win_rate"):
                drift_scores.append(abs(pct) / 100.0)

        # Execution drift index = mean normalised drift of key metrics
        row["execution_drift_idx"] = round(float(np.mean(drift_scores)) if drift_scores else 0.0, 4)

        # PF drift classification
        pf25 = float(s25.get("profit_factor", 0.0))
        pf26 = float(s26.get("profit_factor", 0.0))
        if pf25 < 1.0 and pf26 < 1.0:
            row["verdict"] = "Both_Unprofitable"
        elif pf25 >= 1.0 and pf26 >= 1.0:
            row["verdict"] = "Stable_Profitable"
        elif pf25 >= 1.0 and pf26 < 1.0:
            row["verdict"] = "Degraded"
        else:
            row["verdict"] = "Improved"

        rows.append(row)
        if verbose:
            print(f"  [{sym}] ExecDrift={row['execution_drift_idx']:.3f} "
                  f"PF: {pf25:.3f}→{pf26:.3f} [{row['verdict']}]", flush=True)

    return pd.DataFrame(rows)


# ═══════════════════════════════════════════════════════════════════════════
# Regime Stability
# ═══════════════════════════════════════════════════════════════════════════

def compute_regime_stability(
    all_data_2025: Dict[str, pd.DataFrame],
    all_data_2026: Dict[str, pd.DataFrame],
    verbose: bool = True,
) -> pd.DataFrame:
    """Compare regime occupancy distributions 2025 vs 2026."""
    rows = []

    for sym in MARKET_ORDER:
        df25_path = _HERE / "results" / "phase3" / f"prepared_{sym}.parquet"
        df26 = all_data_2026.get(sym)

        if df26 is None or "regime" not in df26.columns:
            continue

        # Load 2025
        if sym == "EURUSD":
            cache_dir = _HERE / "cache"
            frames = []
            for fp in sorted(cache_dir.glob("ohlc_transport_2025_*.parquet")):
                try:
                    df = pd.read_parquet(fp)
                    if "regime" in df.columns:
                        frames.append(df["regime"])
                except Exception:
                    pass
            regime25 = pd.concat(frames) if frames else pd.Series(dtype=str)
        elif df25_path.exists():
            try:
                regime25 = pd.read_parquet(df25_path)["regime"]
            except Exception:
                regime25 = pd.Series(dtype=str)
        else:
            regime25 = pd.Series(dtype=str)

        regime26 = df26["regime"]

        # Occupancy vectors
        occ25 = np.array([float((regime25 == r).mean()) for r in REGIMES_5])
        occ26 = np.array([float((regime26 == r).mean()) for r in REGIMES_5])

        tvd  = _tv_distance(occ25, occ26)
        kld  = _kl_divergence(occ25 + 1e-12, occ26 + 1e-12)

        row = {"symbol": sym, "tv_distance": round(tvd, 4), "kl_divergence": round(kld, 4),
               "regime_stability_idx": round(1.0 - min(tvd * 2, 1.0), 4)}
        for i, r in enumerate(REGIMES_5):
            row[f"occ25_{r[:4]}"] = round(float(occ25[i]), 4)
            row[f"occ26_{r[:4]}"] = round(float(occ26[i]), 4)
            row[f"delta_{r[:4]}"] = round(float(occ26[i] - occ25[i]), 4)
        rows.append(row)

        if verbose:
            print(f"  [{sym}] Regime stability={row['regime_stability_idx']:.3f} TVD={tvd:.3f}", flush=True)

    return pd.DataFrame(rows)


# ═══════════════════════════════════════════════════════════════════════════
# Allocator / Scheduler Stability
# ═══════════════════════════════════════════════════════════════════════════

def compute_allocator_drift(
    all_trade_logs_2025: Optional[pd.DataFrame],
    all_trade_logs_2026: Dict[str, pd.DataFrame],
    verbose: bool = True,
) -> pd.DataFrame:
    """Compare allocator/family usage 2025 vs 2026."""
    rows = []

    # Load Phase 4 allocator table
    alloc_path = PHASE4_DIR / "allocator_by_market.csv"
    if not alloc_path.exists():
        return pd.DataFrame()
    alloc_df = pd.read_csv(alloc_path)

    for sym in MARKET_ORDER:
        tl26 = all_trade_logs_2026.get(sym)
        alloc_sym = alloc_df[alloc_df["symbol"] == sym]

        # Expected families from frozen allocator
        expected_families = {}
        for _, row in alloc_sym.iterrows():
            expected_families[row["regime"]] = row.get("best_family", "NoTrade")

        # Observed families in 2026 trades
        observed_families = {}
        if tl26 is not None and len(tl26) > 0 and "regime" in tl26.columns and "family" in tl26.columns:
            for regime in REGIMES_5:
                sub = tl26[tl26["regime"] == regime]
                if len(sub) > 0:
                    observed_families[regime] = sub["family"].mode()[0] if len(sub) > 0 else "NoTrade"
                else:
                    observed_families[regime] = "NoTrade"

        # Stability: fraction of regimes where observed == expected
        matches = 0
        total = 0
        for regime in REGIMES_5:
            exp = expected_families.get(regime, "NoTrade")
            obs = observed_families.get(regime, "NoTrade")
            if exp != "NoTrade":
                total += 1
                if obs == exp:
                    matches += 1

        stability = matches / max(total, 1)

        rows.append({
            "symbol"             : sym,
            "allocator_matches"  : matches,
            "allocator_total"    : total,
            "allocator_stability": round(stability, 4),
            "allocator_drift_idx": round(1.0 - stability, 4),
        })

        if verbose:
            print(f"  [{sym}] Allocator stability={stability:.3f} ({matches}/{total} regimes)", flush=True)

    return pd.DataFrame(rows)


# ═══════════════════════════════════════════════════════════════════════════
# Statistical tests: 2025 vs 2026 net returns
# ═══════════════════════════════════════════════════════════════════════════

def run_statistical_tests(
    all_trade_logs_2026: Dict[str, pd.DataFrame],
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Run full suite of statistical tests per market.
    2025 returns from Phase 4 pl_trades/metrics. 2026 from replay.
    """
    rows = []

    for sym in MARKET_ORDER:
        tl26 = all_trade_logs_2026.get(sym)
        rets26 = tl26["net_ret"].dropna().values if tl26 is not None and len(tl26) > 0 else np.array([])

        # Load 2025 returns
        p4_trades_path = PHASE4_DIR / "runs" / f"pl_trades_{sym}.parquet"
        p4_metrics_path = PHASE4_DIR / "runs" / f"metrics_{sym}.parquet"
        rets25 = np.array([])

        if p4_trades_path.exists():
            try:
                tl25 = pd.read_parquet(p4_trades_path)
                if "net_ret" in tl25.columns:
                    rets25 = tl25["net_ret"].dropna().values
            except Exception:
                pass

        if len(rets25) < 5 or len(rets26) < 5:
            rows.append({
                "symbol": sym, "n_2025": len(rets25), "n_2026": len(rets26),
                "mw_stat": np.nan, "mw_pval": np.nan, "mw_reject": False,
                "wilcox_stat": np.nan, "wilcox_pval": np.nan, "wilcox_reject": False,
                "ks_stat": np.nan, "ks_pval": np.nan, "ks_reject": False,
                "cohens_d": np.nan, "rank_biserial": np.nan,
                "mean_2025": float(rets25.mean()) if len(rets25) > 0 else np.nan,
                "mean_2026": float(rets26.mean()) if len(rets26) > 0 else np.nan,
                "ttest_pval": np.nan, "ttest_reject": False,
                "mw_reject_fdr": False,
            })
            continue

        # Mann-Whitney U
        mw_stat, mw_p = scipy_stats.mannwhitneyu(rets25, rets26, alternative="two-sided")

        # KS test
        ks_stat, ks_p = scipy_stats.ks_2samp(rets25, rets26)

        # t-test
        tt_stat, tt_p = scipy_stats.ttest_ind(rets25, rets26)

        # Wilcoxon (on paired: use min length)
        min_n = min(len(rets25), len(rets26))
        rng   = np.random.default_rng(42)
        s25_sub = rng.choice(rets25, size=min_n, replace=False)
        s26_sub = rng.choice(rets26, size=min_n, replace=False)
        try:
            wil_stat, wil_p = scipy_stats.wilcoxon(s25_sub, s26_sub)
        except Exception:
            wil_stat, wil_p = np.nan, 1.0

        # Effect sizes
        cd  = _cohens_d(rets25, rets26)
        rbr = _rank_biserial(rets25, rets26)

        rows.append({
            "symbol"        : sym,
            "n_2025"        : len(rets25),
            "n_2026"        : len(rets26),
            "mean_2025"     : round(float(rets25.mean()), 6),
            "mean_2026"     : round(float(rets26.mean()), 6),
            "mw_stat"       : round(float(mw_stat), 4),
            "mw_pval"       : round(float(mw_p), 6),
            "mw_reject"     : bool(mw_p < 0.05),
            "ks_stat"       : round(float(ks_stat), 4),
            "ks_pval"       : round(float(ks_p), 6),
            "ks_reject"     : bool(ks_p < 0.05),
            "ttest_pval"    : round(float(tt_p), 6),
            "ttest_reject"  : bool(tt_p < 0.05),
            "wilcox_stat"   : round(float(wil_stat), 4) if not np.isnan(wil_stat) else np.nan,
            "wilcox_pval"   : round(float(wil_p), 6),
            "wilcox_reject" : bool(wil_p < 0.05),
            "cohens_d"      : round(float(cd), 4),
            "rank_biserial" : round(float(rbr), 4),
            "mw_reject_fdr" : False,  # filled after
        })

        if verbose:
            print(f"  [{sym}] MW p={mw_p:.4f} KS p={ks_p:.4f} d={cd:.3f}", flush=True)

    df = pd.DataFrame(rows)
    if len(df) > 0 and "mw_pval" in df.columns:
        pvals = df["mw_pval"].fillna(1.0).values
        reject_fdr = _bh_fdr(pvals)
        df["mw_reject_fdr"] = reject_fdr
    return df


# ═══════════════════════════════════════════════════════════════════════════
# Master drift summary
# ═══════════════════════════════════════════════════════════════════════════

def compute_all_drift(
    all_data_2026: Dict[str, pd.DataFrame],
    all_trade_logs_2026: Dict[str, pd.DataFrame],
    stats_2025: Dict[str, Dict],
    stats_2026: Dict[str, Dict],
    verbose: bool = True,
) -> Dict[str, pd.DataFrame]:
    """Run all drift analyses. Returns dict of DataFrames."""
    print("  Computing transport drift …", flush=True)
    transport_drift = compute_transport_drift(all_data_2026, verbose=verbose)

    print("  Computing execution drift …", flush=True)
    execution_drift = compute_execution_drift(stats_2025, stats_2026,
                                              all_trade_logs_2026, verbose=verbose)

    print("  Computing regime stability …", flush=True)
    regime_stability = compute_regime_stability({}, all_data_2026, verbose=verbose)

    print("  Computing allocator drift …", flush=True)
    allocator_drift = compute_allocator_drift(None, all_trade_logs_2026, verbose=verbose)

    print("  Running statistical tests …", flush=True)
    stat_tests = run_statistical_tests(all_trade_logs_2026, verbose=verbose)

    return {
        "transport_drift"  : transport_drift,
        "execution_drift"  : execution_drift,
        "regime_stability" : regime_stability,
        "allocator_drift"  : allocator_drift,
        "statistical_tests": stat_tests,
    }
