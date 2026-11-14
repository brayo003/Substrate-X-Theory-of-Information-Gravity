"""
phase1_validation.py — Phase 1 Transport Strategy Matrix Validation Orchestrator.

Usage:
    python phase1_validation.py [--max-files N] [--max-ticks-2025 N] [--data-dir PATH]

Runs the full pipeline:
  1. Load EUR/USD tick data (2023–2025)
  2. Build transport-augmented OHLC DataFrame via existing pipeline (immutable)
  3. Run 28 strategies under uniform execution
  4. Compute strategy × regime performance matrix
  5. Run significance tests (Mann-Whitney, permutation, bootstrap, FDR)
  6. Compute regime stability (Markov, entropy, persistence)
  7. Allocate best strategy per regime (data-driven)
  8. Generate all output files in results/phase1/

Output files:
  phase1_strategy_matrix.md
  phase1_strategy_matrix.csv
  strategy_regime_heatmap.png
  strategy_rankings.csv
  best_strategy_per_regime.csv
  regime_transition_statistics.csv
  performance_by_regime.csv
  bootstrap_statistics.csv
  significance_tests.csv
  strategy_allocator_report.md
"""

import sys
import argparse
import time
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')

_HERE = Path(__file__).resolve().parent
_CE   = _HERE.parents[1]
for p in [str(_CE), str(_HERE), str(_HERE / 'v12_validate')]:
    if p not in sys.path:
        sys.path.insert(0, p)

from v12_validate.loader              import load_all_ticks
from v12_validate.transport_integration import build_full_pipeline

from strategy_library               import get_all_strategies, get_families
from execution_simulator            import run_all_strategies, classify_q_regimes
from strategy_statistics            import (build_strategy_regime_matrix,
                                            run_significance_tests,
                                            run_bootstrap_statistics)
from regime_stability               import (regime_statistics,
                                            regime_stability_to_csv,
                                            regime_transitions_catalog,
                                            compute_markov_matrix,
                                            classify_q_regimes as _cq)
from strategy_allocator             import (best_strategy_per_regime,
                                            strategy_rankings,
                                            build_allocator_report_text,
                                            REGIMES_5)
from transport_strategy_integrator  import (build_gated_trade_log,
                                            compute_sizing_comparison,
                                            DEFAULT_TRADE_GATE,
                                            DEFAULT_SIZE_POLICY)

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns


# ─────────────────────────────────────────────────────────────────────────────
# Output directories
# ─────────────────────────────────────────────────────────────────────────────

def ensure_output_dirs(base: Path) -> Path:
    out = base / 'results' / 'phase1'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'plots').mkdir(exist_ok=True)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Heatmap
# ─────────────────────────────────────────────────────────────────────────────

def plot_heatmap(matrix_df: pd.DataFrame, out_dir: Path, metric: str = 'profit_factor'):
    sub = matrix_df[matrix_df['regime'] != 'ALL'].copy()
    sub = sub[sub['regime'] != 'Transition']

    pivot = sub.pivot_table(index='strategy', columns='regime',
                            values=metric, aggfunc='first')
    # Order columns by coherence level
    col_order = [r for r in REGIMES_5 if r in pivot.columns and r != 'Transition']
    pivot = pivot[col_order]

    # Sort rows by mean across regimes
    pivot = pivot.loc[pivot.mean(axis=1).sort_values(ascending=False).index]

    fig, ax = plt.subplots(figsize=(14, max(8, len(pivot) * 0.4)))
    cmap = sns.diverging_palette(10, 130, as_cmap=True)
    vmin = max(0, pivot.min().min() - 0.1)
    vmax = min(3.0, pivot.max().max() + 0.1)
    sns.heatmap(
        pivot, ax=ax, cmap=cmap, center=1.0,
        vmin=vmin, vmax=vmax,
        annot=True, fmt='.2f', linewidths=0.5,
        cbar_kws={'label': metric.replace('_', ' ').title()},
    )
    ax.set_title(f'Strategy × Regime Heatmap — {metric.replace("_"," ").title()}',
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Q Regime (Incoherent → Coherent)', fontsize=11)
    ax.set_ylabel('Strategy', fontsize=11)
    plt.tight_layout()
    fig.savefig(out_dir / 'plots' / 'strategy_regime_heatmap.png', dpi=150)
    plt.close(fig)
    print(f"  Saved: strategy_regime_heatmap.png")


# ─────────────────────────────────────────────────────────────────────────────
# Markdown matrix
# ─────────────────────────────────────────────────────────────────────────────

def build_matrix_markdown(matrix_df: pd.DataFrame, sig_tests: pd.DataFrame) -> str:
    sig_map = {}
    if len(sig_tests) > 0:
        sig_map = dict(zip(sig_tests['strategy'],
                           sig_tests.get('mw_reject_fdr', pd.Series(False))))

    lines = ["# Phase 1 — Strategy × Regime Performance Matrix", ""]
    lines.append("Execution: 2-pip commission + 0.5-pip slippage, "
                 "ATR(1.5x) stop, ATR(2.5x) target, max 24-bar hold.")
    lines.append("Regimes: Deep_Incoherent | Mod_Incoherent | Transition | Weak_Coherent | Strong_Coherent")
    lines.append("PF = Profit Factor | SR = Sharpe | WR = Win Rate | N = Trade Count | * = FDR significant")
    lines.append("")

    families = {}
    for _, row in matrix_df.iterrows():
        families[row['strategy']] = row.get('family', '?')

    strategies = sorted(matrix_df['strategy'].unique())

    # Header
    header = f"| {'Strategy':<28} | {'Family':<14} | "
    for r in REGIMES_5:
        short = r.replace('_', ' ')[:18]
        header += f"{'PF':>5} {'SR':>6} {'WR':>5} {'N':>4} | "
    lines.append(header.rstrip())

    sep = f"| {'-'*28} | {'-'*14} | "
    for _ in REGIMES_5:
        sep += f"{'-'*5} {'-'*6} {'-'*5} {'-'*4} | "
    lines.append(sep.rstrip())

    # Regime label row
    lbl = f"| {'':28} | {'':14} | "
    for r in REGIMES_5:
        short = r[:18].replace('_',' ')
        lbl += f"{'':>22}| "
    lines.append("")
    lines.append("**Columns per regime: PF | Sharpe | WinRate | Trades**")
    lines.append("")

    # Build a wide table
    col_map = {r: {} for r in REGIMES_5}
    for _, row in matrix_df.iterrows():
        if row['regime'] in REGIMES_5:
            col_map[row['regime']][row['strategy']] = row

    # Compact table: one row per strategy
    lines.append(f"| {'Strategy':<28} | {'Family':<14} | " +
                 " | ".join([f"{r.replace('_',' ')[:18]:<22}" for r in REGIMES_5]) + " |")
    lines.append(f"| {'-'*28} | {'-'*14} | " +
                 " | ".join(["-"*22 for _ in REGIMES_5]) + " |")

    for strat in strategies:
        sig_mark = "*" if sig_map.get(strat, False) else " "
        fam = families.get(strat, "?")
        row_str = f"| {strat+sig_mark:<28} | {fam:<14} | "
        for r in REGIMES_5:
            cell = col_map[r].get(strat)
            if cell is None or int(cell.get('trade_count', 0)) < 5:
                row_str += f"{'—':>22} | "
            else:
                pf = cell.get('profit_factor', 0)
                sh = cell.get('sharpe', 0)
                wr = cell.get('win_rate', 0)
                n  = int(cell.get('trade_count', 0))
                row_str += f"{pf:5.2f} {sh:6.2f} {wr:5.2f} {n:4d} | "
        lines.append(row_str)

    lines.append("")
    lines.append("\\* = FDR-corrected Mann-Whitney p < 0.05")
    lines.append("")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--max-files',      type=int, default=None,
                   help='Max BI5 files per year (None = all)')
    p.add_argument('--max-ticks-2025', type=int, default=2_000_000)
    p.add_argument('--data-dir',       type=str, default=str(_HERE / 'data'))
    return p.parse_args()


def main():
    args = parse_args()
    t0   = time.perf_counter()
    out  = ensure_output_dirs(_HERE)

    print("=" * 70)
    print("  Phase 1 — Transport Strategy Matrix Validation (EUR/USD)")
    print("=" * 70)

    # ── 1. Load data ──────────────────────────────────────────────────────
    print("\n[1/7] Loading tick data …")
    ticks = load_all_ticks(
        args.data_dir,
        max_files_per_year=args.max_files,
        include_2025=True,
        max_rows_2025=args.max_ticks_2025,
    )
    print(f"  Loaded {len(ticks):,} ticks  "
          f"{ticks['timestamp'].min().date()} → {ticks['timestamp'].max().date()}")

    # ── 2. Build transport-augmented DataFrame ────────────────────────────
    print("\n[2/7] Building transport pipeline …")
    df, meta = build_full_pipeline(ticks, verbose=True)
    df['year'] = df.index.year
    print(f"  {len(df):,} bars  |  coherent fraction = {(df['tr_Q']>0).mean():.3f}")

    # ── 3. Run all 28 strategies (ungated baseline) ───────────────────────
    print("\n[3/7] Running 28 strategies (ungated baseline) …")
    registry   = get_all_strategies()
    print(f"  Strategies: {len(registry)}")
    for fam, names in sorted(get_families().items()):
        print(f"    {fam}: {', '.join(names)}")

    all_trades = run_all_strategies(df, registry)
    print(f"  Total trades: {len(all_trades):,}")

    # ── 4. Strategy × Regime matrix + statistics ──────────────────────────
    print("\n[4/7] Computing performance matrix & statistics …")
    matrix_df   = build_strategy_regime_matrix(all_trades)
    sig_tests   = run_significance_tests(all_trades)
    boot_stats  = run_bootstrap_statistics(all_trades)
    print(f"  Matrix rows: {len(matrix_df)}")
    n_sig = int(sig_tests.get('mw_reject_fdr', pd.Series(False)).sum()) \
            if 'mw_reject_fdr' in sig_tests.columns else 0
    print(f"  FDR-significant strategies: {n_sig}/{len(sig_tests)}")

    # ── 5. Regime stability ───────────────────────────────────────────────
    print("\n[5/7] Regime stability analysis …")
    stab_stats  = regime_statistics(df)
    stab_csv    = regime_stability_to_csv(stab_stats)
    transitions = regime_transitions_catalog(df)
    markov_df   = stab_stats['markov_matrix']
    print(f"  Entropy: {stab_stats['entropy']:.4f} bits  "
          f"(normalised: {stab_stats['normalized_entropy']:.3f})")
    print(f"  Transitions/hr: {stab_stats['trans_per_hour']:.4f}")
    for r in REGIMES_5:
        frac = stab_stats['fractions'][r]
        mb   = stab_stats['run_stats'][r]['mean_bars']
        print(f"    {r:<22}  {frac:.3f}  mean {mb:.1f} bars")

    # ── 6. Strategy allocation ────────────────────────────────────────────
    print("\n[6/7] Strategy allocation …")
    best_per    = best_strategy_per_regime(matrix_df, sig_tests)
    rankings    = strategy_rankings(matrix_df, sig_tests)
    print("\n  Best strategy per regime:")
    for _, row in best_per.iterrows():
        print(f"    {row['regime']:<22} → {row['best_strategy']:<26}  "
              f"PF={row['profit_factor']:.3f}  confidence={row['confidence']}")

    # ── 7. Save all outputs ───────────────────────────────────────────────
    print("\n[7/7] Saving outputs …")

    # CSVs
    matrix_df.to_csv(out / 'phase1_strategy_matrix.csv', index=False)
    sig_tests.to_csv(out / 'significance_tests.csv', index=False)
    boot_stats.to_csv(out / 'bootstrap_statistics.csv', index=False)
    stab_csv.to_csv(out / 'regime_transition_statistics.csv', index=False)
    transitions.to_csv(out / 'regime_transitions_catalog.csv', index=False)
    markov_df.to_csv(out / 'markov_matrix.csv')
    best_per.to_csv(out / 'best_strategy_per_regime.csv', index=False)
    rankings.to_csv(out / 'strategy_rankings.csv', index=False)

    # performance_by_regime.csv: matrix excluding ALL row
    perf_by_regime = matrix_df[matrix_df['regime'] != 'ALL'].copy()
    perf_by_regime.to_csv(out / 'performance_by_regime.csv', index=False)

    # Trade log (too large to save in full; save summary)
    all_trades.to_csv(out / 'trade_log_full.csv', index=False)
    print(f"  Saved: phase1_strategy_matrix.csv ({len(matrix_df)} rows)")
    print(f"  Saved: significance_tests.csv ({len(sig_tests)} rows)")
    print(f"  Saved: bootstrap_statistics.csv ({len(boot_stats)} rows)")
    print(f"  Saved: regime_transition_statistics.csv")
    print(f"  Saved: best_strategy_per_regime.csv")
    print(f"  Saved: strategy_rankings.csv")

    # Heatmap
    plot_heatmap(matrix_df, out)

    # Markdown matrix
    matrix_md = build_matrix_markdown(matrix_df, sig_tests)
    (out / 'phase1_strategy_matrix.md').write_text(matrix_md, encoding='utf-8')
    print(f"  Saved: phase1_strategy_matrix.md")

    # Allocator report
    report_text = build_allocator_report_text(
        best_per, rankings, stab_stats, sig_tests
    )
    (out / 'strategy_allocator_report.md').write_text(report_text, encoding='utf-8')
    print(f"  Saved: strategy_allocator_report.md")

    # ── Summary ───────────────────────────────────────────────────────────
    elapsed = time.perf_counter() - t0
    print(f"\n{'='*70}")
    print(f"  Phase 1 complete in {elapsed:.1f}s")
    print(f"  Output directory: {out}")
    print(f"{'='*70}")

    # ── Print final answers ───────────────────────────────────────────────
    _print_conclusions(best_per, rankings, sig_tests, stab_stats)


def _print_conclusions(best_per, rankings, sig_tests, stab_stats):
    print("\n" + "=" * 70)
    print("  SCIENTIFIC CONCLUSIONS")
    print("=" * 70)

    n_sig = int(sig_tests.get('mw_reject_fdr', pd.Series(False)).sum()) \
            if 'mw_reject_fdr' in sig_tests.columns else 0

    print(f"\nQ1. Does Q consistently separate strategy families?")
    if n_sig > len(sig_tests) * 0.5:
        ans, conf = "YES", "High"
    elif n_sig > 0:
        ans, conf = "PARTIAL", "Moderate"
    else:
        ans, conf = "NOT DEMONSTRATED", "Unsupported"
    print(f"  → {ans}  ({n_sig}/{len(sig_tests)} FDR-significant)  Confidence: {conf}")

    print(f"\nQ2. Which strategy belongs to each regime?")
    for _, row in best_per.iterrows():
        print(f"  {row['regime']:<22} → {row['best_strategy']} ({row['best_family']})  "
              f"[{row['confidence']}]")

    no_trade = best_per[best_per['best_strategy'] == 'NO_TRADE']['regime'].tolist()
    print(f"\nQ3. Regime where no strategy should trade?")
    print(f"  → {', '.join(no_trade) if no_trade else 'None identified'}  Confidence: High")

    print(f"\nQ4. Does Q improve allocation vs fixed strategy?")
    top_fixed = rankings.iloc[0] if len(rankings) > 0 else None
    if top_fixed is not None and top_fixed['regime_sensitivity'] > 0.1:
        print(f"  → YES — top strategy '{top_fixed['strategy']}' shows sensitivity "
              f"{top_fixed['regime_sensitivity']:.4f} across regimes.")
        print(f"  → Confidence: Moderate")
    else:
        print(f"  → INCONCLUSIVE  Confidence: Weak")

    print(f"\nQ5. Does Q reduce drawdown through allocation?")
    print(f"  → Run transport_strategy_integrator.compute_sizing_comparison() to verify")
    print(f"    (gated vs ungated drawdown comparison requires separate run)")

    print(f"\nQ6. Can Q be interpreted as a transport operating system?")
    entropy_n = stab_stats.get('normalized_entropy', 0)
    if entropy_n < 0.85 and stab_stats.get('trans_per_hour', 99) < 2.0:
        print(f"  → YES — Q exhibits structured regime structure: "
              f"entropy={entropy_n:.3f}, transitions/hr={stab_stats['trans_per_hour']:.4f}")
        print(f"  → Confidence: Moderate")
    else:
        print(f"  → PARTIAL — regime structure present but noisy")
        print(f"  → Confidence: Weak")


if __name__ == '__main__':
    main()
