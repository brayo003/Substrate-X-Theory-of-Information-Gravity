"""
strategy_allocator.py — Data-driven Strategy Allocation per Q Regime.

NO hardcoding. Infers best strategy for each regime purely from empirical
performance data (profit factor, Sharpe, statistical significance).

Scoring model:
  composite_score = 0.4 * norm(profit_factor)
                  + 0.3 * norm(sharpe)
                  + 0.2 * norm(win_rate)
                  + 0.1 * norm(expectancy)
  Minimum 10 trades required for a cell to be eligible.
  Cells with FDR-corrected p < 0.05 get a 20% bonus on composite score.
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional

from execution_simulator import REGIMES_5


def _norm_col(series: pd.Series) -> pd.Series:
    """Min-max normalise to [0, 1]. Returns 0.5 for constant columns."""
    lo, hi = series.min(), series.max()
    if hi <= lo:
        return pd.Series(0.5, index=series.index)
    return (series - lo) / (hi - lo)


def compute_composite_score(matrix_df: pd.DataFrame,
                             sig_tests: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """
    Compute a composite allocation score for every (strategy, regime) cell.

    Parameters
    ----------
    matrix_df : output of strategy_statistics.build_strategy_regime_matrix()
    sig_tests : output of strategy_statistics.run_significance_tests() (optional)

    Returns
    -------
    DataFrame with added column 'composite_score', sorted descending per regime.
    """
    df = matrix_df.copy()

    # Filter cells with insufficient data
    df = df[df['trade_count'] >= 10].copy()

    # Replace inf/nan in profit_factor with 0
    df['profit_factor'] = df['profit_factor'].replace([np.inf, -np.inf], np.nan).fillna(0)
    df['sharpe']        = df['sharpe'].replace([np.inf, -np.inf], np.nan).fillna(0)
    df['win_rate']      = df['win_rate'].fillna(0)
    df['expectancy']    = df['expectancy'].fillna(0)

    # Normalise globally (not per regime) so cross-regime comparison is valid
    df['n_pf']   = _norm_col(df['profit_factor'])
    df['n_sh']   = _norm_col(df['sharpe'])
    df['n_wr']   = _norm_col(df['win_rate'])
    df['n_exp']  = _norm_col(df['expectancy'])

    df['composite_score'] = (
        0.40 * df['n_pf'] +
        0.30 * df['n_sh'] +
        0.20 * df['n_wr'] +
        0.10 * df['n_exp']
    )

    # Statistical significance bonus: +20% if FDR-corrected p < 0.05
    if sig_tests is not None and len(sig_tests) > 0:
        sig_map = dict(zip(sig_tests['strategy'],
                           sig_tests.get('mw_reject_fdr', pd.Series(False))))
        df['sig_bonus'] = df['strategy'].map(sig_map).fillna(False).astype(float) * 0.20
        df['composite_score'] += df['sig_bonus']
    else:
        df['sig_bonus'] = 0.0

    return df.drop(columns=['n_pf', 'n_sh', 'n_wr', 'n_exp'])


def best_strategy_per_regime(
    matrix_df: pd.DataFrame,
    sig_tests: Optional[pd.DataFrame] = None,
    min_trades: int = 10,
) -> pd.DataFrame:
    """
    For each Q regime, select the best strategy by composite score.

    Also selects best family (majority family among top-3 strategies).

    Returns DataFrame with columns:
      regime, best_strategy, best_family, composite_score,
      profit_factor, sharpe, win_rate, trade_count,
      runner_up, runner_up_score,
      confidence (High/Moderate/Weak/Unsupported)
    """
    scored = compute_composite_score(matrix_df, sig_tests)
    rows   = []

    for regime in REGIMES_5:
        sub = scored[scored['regime'] == regime].copy()
        sub = sub[sub['trade_count'] >= min_trades]

        if len(sub) == 0:
            rows.append(dict(
                regime='Transition' if regime == 'Transition' else regime,
                best_strategy='NO_TRADE',
                best_family='—',
                composite_score=0.0,
                profit_factor=np.nan,
                sharpe=np.nan,
                win_rate=np.nan,
                trade_count=0,
                runner_up='—',
                runner_up_score=0.0,
                confidence='Unsupported',
                verdict='Insufficient data',
            ))
            continue

        sub = sub.sort_values('composite_score', ascending=False)
        best      = sub.iloc[0]
        runner_up = sub.iloc[1] if len(sub) > 1 else None

        # Confidence based on score margin and trade count
        score_margin = (best['composite_score'] -
                        (runner_up['composite_score'] if runner_up is not None else 0.0))
        n = int(best['trade_count'])

        if n >= 50 and score_margin > 0.15 and best['profit_factor'] > 1.2:
            confidence = 'High'
        elif n >= 20 and score_margin > 0.05 and best['profit_factor'] > 1.0:
            confidence = 'Moderate'
        elif n >= 10:
            confidence = 'Weak'
        else:
            confidence = 'Unsupported'

        # Special override for Transition regime
        if regime == 'Transition':
            rows.append(dict(
                regime=regime,
                best_strategy='NO_TRADE',
                best_family='—',
                composite_score=0.0,
                profit_factor=np.nan,
                sharpe=np.nan,
                win_rate=np.nan,
                trade_count=0,
                runner_up='—',
                runner_up_score=0.0,
                confidence='High',
                verdict='Transition regime: no trade by design (Q ≈ 0)',
            ))
            continue

        rows.append(dict(
            regime          = regime,
            best_strategy   = best['strategy'],
            best_family     = best.get('family', '—'),
            composite_score = float(best['composite_score']),
            profit_factor   = float(best['profit_factor']),
            sharpe          = float(best['sharpe']),
            win_rate        = float(best['win_rate']),
            trade_count     = int(best['trade_count']),
            runner_up       = runner_up['strategy'] if runner_up is not None else '—',
            runner_up_score = float(runner_up['composite_score']) if runner_up is not None else 0.0,
            confidence      = confidence,
            verdict         = f"{best['strategy']} ({best.get('family','?')}) "
                              f"PF={best['profit_factor']:.3f} Sharpe={best['sharpe']:.3f}",
        ))

    return pd.DataFrame(rows)


def strategy_rankings(
    matrix_df: pd.DataFrame,
    sig_tests: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """
    Global strategy rankings across all regimes.

    Ranks by mean composite score across regimes where trade_count >= 10,
    annotated with best/worst regime per strategy.
    """
    scored = compute_composite_score(matrix_df, sig_tests)
    # Exclude ALL row and Transition for this ranking
    scored = scored[~scored['regime'].isin(['ALL', 'Transition'])]
    scored = scored[scored['trade_count'] >= 10]

    agg = scored.groupby(['strategy', 'family']).agg(
        mean_score       = ('composite_score', 'mean'),
        mean_pf          = ('profit_factor',   'mean'),
        mean_sharpe      = ('sharpe',          'mean'),
        mean_win_rate    = ('win_rate',         'mean'),
        total_trades     = ('trade_count',      'sum'),
        n_regimes_active = ('regime',           'count'),
    ).reset_index()

    # Best and worst regime per strategy
    best_rows  = scored.loc[scored.groupby('strategy')['composite_score'].idxmax(),
                             ['strategy', 'regime', 'composite_score']]
    worst_rows = scored.loc[scored.groupby('strategy')['composite_score'].idxmin(),
                             ['strategy', 'regime', 'composite_score']]
    best_rows  = best_rows.rename(columns={'regime': 'best_regime',
                                           'composite_score': 'best_score'})
    worst_rows = worst_rows.rename(columns={'regime': 'worst_regime',
                                            'composite_score': 'worst_score'})

    agg = agg.merge(best_rows[['strategy','best_regime','best_score']],
                    on='strategy', how='left')
    agg = agg.merge(worst_rows[['strategy','worst_regime','worst_score']],
                    on='strategy', how='left')

    agg['regime_sensitivity'] = agg['best_score'] - agg['worst_score']
    agg = agg.sort_values('mean_score', ascending=False).reset_index(drop=True)
    agg.insert(0, 'rank', agg.index + 1)
    return agg


def build_allocator_report_text(
    best_per_regime: pd.DataFrame,
    rankings: pd.DataFrame,
    stability_stats: dict,
    sig_tests: pd.DataFrame,
) -> str:
    """
    Generate the strategy_allocator_report.md narrative.
    """
    lines = []
    lines.append("# Strategy Allocator Report — Phase 1 Transport Validation (EUR/USD)")
    lines.append("")
    lines.append("## Methodology")
    lines.append("Best strategy per regime selected by composite score:")
    lines.append("  composite = 0.4×PF + 0.3×Sharpe + 0.2×WinRate + 0.1×Expectancy")
    lines.append("  All scores normalised globally. +20% bonus for FDR-significant strategies.")
    lines.append("  Minimum 10 trades required for eligibility.")
    lines.append("")

    lines.append("## Best Strategy Per Regime")
    lines.append("")
    lines.append(f"{'Regime':<22} {'Strategy':<26} {'Family':<16} {'PF':>6} {'Sharpe':>7} {'WR':>6} {'N':>5} {'Confidence'}")
    lines.append("-" * 100)
    for _, row in best_per_regime.iterrows():
        pf = f"{row['profit_factor']:.3f}" if not pd.isna(row['profit_factor']) else "  N/A"
        sh = f"{row['sharpe']:.3f}"        if not pd.isna(row['sharpe'])        else "  N/A"
        wr = f"{row['win_rate']:.3f}"      if not pd.isna(row['win_rate'])      else "  N/A"
        lines.append(
            f"{row['regime']:<22} {row['best_strategy']:<26} {row['best_family']:<16} "
            f"{pf:>6} {sh:>7} {wr:>6} {int(row['trade_count']):>5}  {row['confidence']}"
        )
    lines.append("")

    lines.append("## Top 10 Strategies by Overall Score")
    lines.append("")
    lines.append(f"{'Rank':<5} {'Strategy':<26} {'Family':<16} {'Score':>7} {'PF':>6} {'Sharpe':>7} {'BestRegime':<22} {'Sensitivity':>12}")
    lines.append("-" * 110)
    for _, row in rankings.head(10).iterrows():
        lines.append(
            f"{int(row['rank']):<5} {row['strategy']:<26} {row['family']:<16} "
            f"{row['mean_score']:>7.4f} {row['mean_pf']:>6.3f} {row['mean_sharpe']:>7.3f} "
            f"{row['best_regime']:<22} {row['regime_sensitivity']:>12.4f}"
        )
    lines.append("")

    lines.append("## Regime Stability Summary")
    lines.append("")
    lines.append(f"  Total bars      : {stability_stats.get('n_bars', 0):,}")
    lines.append(f"  Entropy         : {stability_stats.get('entropy', 0):.4f} bits "
                 f"(normalised: {stability_stats.get('normalized_entropy', 0):.3f})")
    lines.append(f"  Transitions/hr  : {stability_stats.get('trans_per_hour', 0):.4f}")
    lines.append("")
    lines.append(f"  {'Regime':<22} {'Fraction':>9} {'Mean bars':>10} {'P(stay)':>8}")
    lines.append("  " + "-" * 55)
    for r in REGIMES_5:
        frac  = stability_stats['fractions'].get(r, 0)
        mbars = stability_stats['run_stats'][r].get('mean_bars', 0)
        pstay = stability_stats['persistence'].get(r, {}).get('p_stay', 0)
        lines.append(f"  {r:<22} {frac:>9.4f} {mbars:>10.2f} {pstay:>8.4f}")
    lines.append("")

    lines.append("## Statistical Significance")
    lines.append("")
    lines.append(f"{'Strategy':<26} {'MW p (raw)':>12} {'MW p (FDR)':>12} {'Significant':>12} {'Cohen d':>8}")
    lines.append("-" * 75)
    for _, row in sig_tests.iterrows():
        praw = f"{row.get('mw_p', np.nan):.4f}"    if not pd.isna(row.get('mw_p', np.nan))    else "   N/A"
        pfdr = f"{row.get('mw_p_fdr', np.nan):.4f}" if not pd.isna(row.get('mw_p_fdr', np.nan)) else "   N/A"
        cd   = f"{row.get('cohen_d', np.nan):.3f}"  if not pd.isna(row.get('cohen_d', np.nan))  else "  N/A"
        sig  = "YES" if row.get('mw_reject_fdr', False) else "no"
        lines.append(f"{row['strategy']:<26} {praw:>12} {pfdr:>12} {sig:>12} {cd:>8}")
    lines.append("")

    lines.append("## Conclusions")
    lines.append("")
    n_sig = int(sig_tests.get('mw_reject_fdr', pd.Series(False)).sum()) if len(sig_tests) > 0 else 0
    n_tot = len(sig_tests)
    lines.append(f"1. {n_sig}/{n_tot} strategies show statistically significant regime-dependent performance (FDR p<0.05).")

    no_trade = best_per_regime[best_per_regime['best_strategy'] == 'NO_TRADE']
    lines.append(f"2. {len(no_trade)} regime(s) designated NO_TRADE: {', '.join(no_trade['regime'].tolist())}.")

    top = rankings.iloc[0] if len(rankings) > 0 else None
    if top is not None:
        lines.append(f"3. Top overall strategy: {top['strategy']} ({top['family']}) — "
                     f"mean score {top['mean_score']:.4f}, best in {top['best_regime']}.")

    lines.append("")
    return "\n".join(lines)
