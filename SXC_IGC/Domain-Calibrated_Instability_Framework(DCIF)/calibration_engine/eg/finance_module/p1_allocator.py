"""
p1_allocator.py — Data-driven strategy allocator for Phase 1.

Reads phase1_strategy_matrix.csv and significance_tests.csv.
Outputs:
  - best_strategy_per_regime.csv
  - strategy_allocator_report.md
"""

import sys
import warnings
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

_HERE = Path(__file__).resolve().parent
_CE   = _HERE.parents[1]
for p in [str(_CE), str(_HERE)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from p1_checkpoint import RESULTS_DIR, mark_allocator_complete

REGIMES_5 = [
    "Deep_Incoherent",
    "Mod_Incoherent",
    "Transition",
    "Weak_Coherent",
    "Strong_Coherent",
]

MIN_TRADES = 10    # minimum trades for a cell to be considered
AVOID_THRESHOLD_PF = 0.8  # below this PF: consider avoidance
NO_TRADE_MIN_CELLS = 2    # if fewer than this many strategies qualify: recommend NO_TRADE


def _composite_score(row: pd.Series) -> float:
    """Compute composite score from a matrix row."""
    if pd.isna(row.get("profit_factor")) or row.get("trade_count", 0) < MIN_TRADES:
        return -999.0
    pf  = float(row.get("profit_factor", 0))
    sr  = float(row.get("sharpe", 0))
    wr  = float(row.get("win_rate", 0))
    exp = float(row.get("expectancy", 0))
    # Clip extremes
    pf  = min(pf, 5.0)
    sr  = np.clip(sr, -5, 5)
    wr  = np.clip(wr, 0, 1)
    # Normalise to [0,1] with typical ranges
    pf_n  = (pf - 0.5) / (2.5 - 0.5 + 1e-12)   # 0.5..2.5 → 0..1
    sr_n  = (sr + 2) / 4.0                        # -2..2 → 0..1
    wr_n  = wr
    exp_n = np.clip((exp + 0.01) / 0.02, 0, 1)
    score = 0.40 * pf_n + 0.30 * sr_n + 0.20 * wr_n + 0.10 * exp_n
    return float(np.clip(score, 0, 1))


def best_strategy_per_regime(
    matrix_df: pd.DataFrame,
    sig_df: pd.DataFrame,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    For each regime, select the best strategy based on composite score.
    Apply FDR-significance bonus.
    Recommend NO_TRADE if insufficient evidence.
    """
    # Build FDR significance map
    sig_map: dict = {}
    if sig_df is not None and len(sig_df) > 0 and "mw_reject_fdr" in sig_df.columns:
        sig_map = dict(zip(sig_df["strategy"], sig_df["mw_reject_fdr"].fillna(False)))

    results = []
    for regime in REGIMES_5:
        sub = matrix_df[matrix_df["regime"] == regime].copy()
        sub = sub[sub["trade_count"] >= MIN_TRADES].copy()

        if len(sub) < NO_TRADE_MIN_CELLS:
            results.append({
                "regime"         : regime,
                "best_strategy"  : "NO_TRADE",
                "best_family"    : "—",
                "composite_score": 0.0,
                "profit_factor"  : np.nan,
                "sharpe"         : np.nan,
                "win_rate"       : np.nan,
                "trade_count"    : 0,
                "runner_up"      : "—",
                "runner_up_score": 0.0,
                "confidence"     : "Insufficient",
                "verdict"        : "Insufficient data for this regime",
                "n_qualified"    : len(sub),
            })
            continue

        # Score each candidate
        sub = sub.copy()
        sub["score"] = sub.apply(_composite_score, axis=1)
        # FDR bonus
        sub["sig_bonus"] = sub["strategy"].map(sig_map).fillna(False).astype(float) * 0.20
        sub["score"] = sub["score"] + sub["sig_bonus"]
        sub = sub.sort_values("score", ascending=False).reset_index(drop=True)

        best = sub.iloc[0]
        runner = sub.iloc[1] if len(sub) > 1 else None

        # Confidence level
        pf    = float(best.get("profit_factor", 0) or 0)
        score = float(best["score"])
        sig   = bool(sig_map.get(best["strategy"], False))
        tc    = int(best.get("trade_count", 0))

        if sig and pf > 1.5 and tc >= 50:
            confidence = "High"
        elif pf > 1.3 and tc >= 20:
            confidence = "Moderate"
        elif pf > 1.0 and tc >= 10:
            confidence = "Weak"
        else:
            confidence = "Unsupported"

        # Should we recommend avoidance?
        all_pf = sub["profit_factor"].dropna()
        if len(all_pf) >= 2 and all_pf.max() < AVOID_THRESHOLD_PF:
            best_strat = "NO_TRADE"
            best_family = "—"
            verdict = f"All strategies below PF={AVOID_THRESHOLD_PF:.1f} — avoid trading"
            confidence = "Weak"
        else:
            best_strat  = str(best["strategy"])
            best_family = str(best.get("family", "?"))
            verdict = (f"{best_strat} ({best_family}) "
                       f"PF={pf:.3f} Sharpe={float(best.get('sharpe',0) or 0):.3f}")

        results.append({
            "regime"         : regime,
            "best_strategy"  : best_strat,
            "best_family"    : best_family,
            "composite_score": float(best["score"]),
            "profit_factor"  : float(best.get("profit_factor") or np.nan),
            "sharpe"         : float(best.get("sharpe") or np.nan),
            "win_rate"       : float(best.get("win_rate") or np.nan),
            "trade_count"    : int(best.get("trade_count") or 0),
            "runner_up"      : str(runner["strategy"]) if runner is not None else "—",
            "runner_up_score": float(runner["score"]) if runner is not None else 0.0,
            "confidence"     : confidence,
            "verdict"        : verdict,
            "n_qualified"    : len(sub),
        })

    return pd.DataFrame(results)


def build_allocator_report(
    best_df: pd.DataFrame,
    matrix_df: pd.DataFrame,
    sig_df: pd.DataFrame,
    stab_df: pd.DataFrame,
    boot_df: pd.DataFrame,
    q_quantiles: Dict,
) -> str:
    """Build the strategy_allocator_report.md text."""
    lines = [
        "# Strategy Allocator Report — Phase 1 Transport Validation (EUR/USD)",
        "",
        "## Methodology",
        "Best strategy per regime selected by composite score:",
        "  composite = 0.4×PF + 0.3×Sharpe + 0.2×WinRate + 0.1×Expectancy",
        "  All scores normalised globally. +20% bonus for FDR-significant strategies.",
        f"  Minimum {MIN_TRADES} trades required for eligibility.",
        "",
        "## Q Quantile Thresholds (global, from full dataset)",
        f"  Q05 (Deep_Incoherent boundary): {q_quantiles.get('q05',float('nan')):.6f}",
        f"  Q95 (Strong_Coherent boundary): {q_quantiles.get('q95',float('nan')):.6f}",
        f"  Total bars analysed: {q_quantiles.get('n_bars',0):,}",
        f"  Coherent fraction: {q_quantiles.get('coherent_fraction',0):.4f}",
        "",
        "## Best Strategy Per Regime",
        "",
        f"{'Regime':<22} {'Strategy':<28} {'Family':<16} {'PF':>6} {'Sharpe':>8} {'WR':>6} {'N':>5} {'Confidence'}",
        "-" * 110,
    ]
    for _, row in best_df.iterrows():
        pf_s = f"{row['profit_factor']:.3f}" if not pd.isna(row.get("profit_factor")) else "N/A"
        sr_s = f"{row['sharpe']:.3f}"        if not pd.isna(row.get("sharpe"))         else "N/A"
        wr_s = f"{row['win_rate']:.3f}"      if not pd.isna(row.get("win_rate"))        else "N/A"
        n_s  = str(int(row["trade_count"]))  if row["trade_count"] > 0 else "0"
        lines.append(
            f"{row['regime']:<22} {row['best_strategy']:<28} {row['best_family']:<16} "
            f"{pf_s:>6} {sr_s:>8} {wr_s:>6} {n_s:>5}  {row['confidence']}"
        )

    lines += ["", "## Regime Stability Summary", ""]
    if stab_df is not None and len(stab_df) > 0:
        tot_bars = stab_df["bar_count"].sum()
        entropy  = stab_df["entropy"].iloc[0] if "entropy" in stab_df.columns else np.nan
        n_ent    = stab_df["normalized_entropy"].iloc[0] if "normalized_entropy" in stab_df.columns else np.nan
        tph      = stab_df["trans_per_hour"].iloc[0] if "trans_per_hour" in stab_df.columns else np.nan
        lines += [
            f"  Total bars      : {tot_bars:,}",
            f"  Entropy         : {entropy:.4f} bits (normalised: {n_ent:.3f})",
            f"  Transitions/hr  : {tph:.4f}",
            "",
            f"  {'Regime':<22} {'Fraction':>8} {'Mean bars':>10} {'P(stay)':>8}",
            "  " + "-" * 55,
        ]
        for _, row in stab_df.iterrows():
            lines.append(
                f"  {row['regime']:<22} {row['time_fraction']:>8.4f} "
                f"{row['mean_bars']:>10.2f} {row['p_stay']:>8.4f}"
            )

    lines += ["", "## Statistical Significance", ""]
    if sig_df is not None and len(sig_df) > 0:
        lines.append(
            f"{'Strategy':<28} {'MW p (raw)':>12} {'MW p (FDR)':>12} "
            f"{'Sig':>5} {'Cohen d':>10}"
        )
        lines.append("-" * 75)
        for _, row in sig_df.sort_values("mw_pval_raw").iterrows():
            p_raw = f"{row.get('mw_pval_raw',float('nan')):.4f}" if not pd.isna(row.get("mw_pval_raw")) else "N/A"
            p_fdr = f"{row.get('mw_pval_fdr',float('nan')):.4f}" if not pd.isna(row.get("mw_pval_fdr")) else "N/A"
            sig   = "YES" if bool(row.get("mw_reject_fdr", False)) else "no"
            d     = f"{row.get('cohen_d',float('nan')):.3f}" if not pd.isna(row.get("cohen_d")) else "N/A"
            lines.append(f"{row['strategy']:<28} {p_raw:>12} {p_fdr:>12} {sig:>5} {d:>10}")

    # Conclusions
    n_sig = int(sig_df["mw_reject_fdr"].sum()) if sig_df is not None and "mw_reject_fdr" in sig_df.columns else 0
    no_trade = [r["regime"] for _, r in best_df.iterrows() if r["best_strategy"] == "NO_TRADE"]
    top_row  = best_df[best_df["best_strategy"] != "NO_TRADE"].sort_values("composite_score", ascending=False)

    lines += [
        "",
        "## Conclusions",
        "",
        f"1. {n_sig}/{len(sig_df) if sig_df is not None else 0} strategies show "
        f"statistically significant regime-dependent performance (FDR p<0.05).",
    ]
    if no_trade:
        lines.append(f"2. {len(no_trade)} regime(s) designated NO_TRADE: {', '.join(no_trade)}.")
    if len(top_row) > 0:
        r = top_row.iloc[0]
        lines.append(f"3. Top overall strategy: {r['best_strategy']} ({r['best_family']}) "
                     f"— mean score {r['composite_score']:.4f}, best in {r['regime']}.")

    return "\n".join(lines) + "\n"


def run_allocator(
    manifest: Dict,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Load matrix + statistics, compute allocations, save outputs.
    Returns best_per_regime DataFrame.
    """
    matrix_path = RESULTS_DIR / "phase1_strategy_matrix.csv"
    sig_path    = RESULTS_DIR / "significance_tests.csv"
    stab_path   = RESULTS_DIR / "regime_transition_statistics.csv"
    boot_path   = RESULTS_DIR / "bootstrap_statistics.csv"

    if not matrix_path.exists():
        raise FileNotFoundError(f"Matrix not found: {matrix_path}")

    matrix_df = pd.read_csv(matrix_path)
    sig_df    = pd.read_csv(sig_path)    if sig_path.exists()   else pd.DataFrame()
    stab_df   = pd.read_csv(stab_path)  if stab_path.exists()   else None
    boot_df   = pd.read_csv(boot_path)  if boot_path.exists()   else None

    q_quantiles = manifest.get("pipeline", {}).get("q_quantiles") or {}

    if verbose:
        print("  Computing best strategy per regime …", flush=True)
    best_df = best_strategy_per_regime(matrix_df, sig_df, verbose=verbose)

    if verbose:
        for _, row in best_df.iterrows():
            pf = f"{row['profit_factor']:.3f}" if not pd.isna(row.get("profit_factor")) else "N/A"
            print(f"    {row['regime']:<22} → {row['best_strategy']:<26} "
                  f"PF={pf}  [{row['confidence']}]")

    report_text = build_allocator_report(
        best_df, matrix_df, sig_df, stab_df, boot_df, q_quantiles
    )

    best_df.to_csv(RESULTS_DIR / "best_strategy_per_regime.csv", index=False)
    (RESULTS_DIR / "strategy_allocator_report.md").write_text(report_text, encoding="utf-8")

    mark_allocator_complete(manifest)
    if verbose:
        print("  Allocator complete.", flush=True)

    return best_df
