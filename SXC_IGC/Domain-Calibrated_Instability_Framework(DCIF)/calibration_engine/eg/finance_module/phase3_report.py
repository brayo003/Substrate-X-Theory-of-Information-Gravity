"""
phase3_report.py — Report generator for Phase 3 Transport Universality Analysis.

Generates:
  - results/phase3/transport_universality_report.md  (full scientific report)
  - results/phase3/phase3_summary.md                 (executive summary)
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

_HERE = Path(__file__).resolve().parent
PHASE3_DIR = _HERE / "results" / "phase3"

MARKET_ORDER = ["EURUSD", "BTCUSDT", "ETHUSDT", "XAUUSD", "NAS100", "USOIL", "UKOIL"]
REGIMES_5 = ["Deep_Incoherent", "Mod_Incoherent", "Transition", "Weak_Coherent", "Strong_Coherent"]


def _fmt(v, decimals=4):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    if isinstance(v, bool):
        return "YES" if v else "NO"
    if isinstance(v, float):
        return f"{v:.{decimals}f}"
    return str(v)


def _df_to_md(df: pd.DataFrame, float_fmt: int = 4) -> str:
    """Convert DataFrame to Markdown table string."""
    if df is None or len(df) == 0:
        return "_No data_\n"
    lines = []
    header = "| " + " | ".join(str(c) for c in df.columns) + " |"
    sep    = "| " + " | ".join("---" for _ in df.columns) + " |"
    lines.append(header)
    lines.append(sep)
    for _, row in df.iterrows():
        cells = []
        for v in row:
            if isinstance(v, float):
                cells.append(f"{v:.{float_fmt}f}")
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def write_full_report(
    market_summary:     pd.DataFrame,
    regime_dist:        pd.DataFrame,
    allocator_table:    pd.DataFrame,
    universality_matrix: pd.DataFrame,
    universality_scores: pd.DataFrame,
    stat_tests:         pd.DataFrame,
    bootstrap_df:       pd.DataFrame,
    scientific_qa:      List[dict],
    overall_confidence: dict,
    all_regime_stats:   Dict[str, dict],
    all_trade_metrics:  Dict[str, dict],
    all_alloc_metrics:  Dict[str, dict],
    elapsed_s:          float = 0.0,
    verbose: bool = True,
) -> str:
    """Generate the full transport universality report in Markdown."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    minutes = elapsed_s / 60

    lines = []

    lines.append("# Phase 3 — Transport Universality Report")
    lines.append("## Cross-Market Transport Operating System Validation")
    lines.append("")
    lines.append(f"**Generated:** {ts}  ")
    lines.append(f"**Elapsed:** {elapsed_s:.1f}s ({minutes:.1f} min)  ")
    lines.append(f"**Overall universality confidence:** {overall_confidence.get('overall_confidence','—')}  ")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Transport OS Configuration (IMMUTABLE) ────────────────────────────
    lines.append("## Transport OS Configuration (IMMUTABLE — Phase 2 validated)")
    lines.append("")
    lines.append("| Parameter | Value |")
    lines.append("| --- | --- |")
    lines.append("| Q05 threshold | -1.0 |")
    lines.append("| Q95 threshold | 1.73 |")
    lines.append("| Commission RT | 0.00030 |")
    lines.append("| Base risk pct | 1.0% |")
    lines.append("| Hold bars | 24 |")
    lines.append("| ATR stop (Strong_Coherent) | 1.88× |")
    lines.append("| ATR target (Strong_Coherent) | 2.50× |")
    lines.append("| Allocated strategy (SC) | NY_Continuation |")
    lines.append("| No-trade regimes | Deep, Mod, Transition, Weak |")
    lines.append("")
    lines.append("**Parameters changed for Phase 3: NONE**  ")
    lines.append("Every market receives the identical operating system.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Market × Metric table ─────────────────────────────────────────────
    lines.append("## Market × Performance Metrics")
    lines.append("")
    if market_summary is not None and len(market_summary) > 0:
        display_cols = ["Market", "PF", "Sharpe", "Sortino", "MaxDD", "WinRate",
                        "Trades", "NoTrade_pct", "CoherentFrac", "TotalBars"]
        disp = market_summary[[c for c in display_cols if c in market_summary.columns]]
        lines.append(_df_to_md(disp, float_fmt=4))
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Market × Regime Distribution ──────────────────────────────────────
    lines.append("## Market × Regime Distribution")
    lines.append("")
    lines.append("Fraction of total bars in each regime (Q thresholds IMMUTABLE):")
    lines.append("")
    # Build compact regime table
    reg_rows = []
    for sym in MARKET_ORDER:
        rs = all_regime_stats.get(sym, {})
        fracs = rs.get("regime_fractions", {})
        row = {
            "Market"           : sym,
            "Deep_Incoherent"  : f"{fracs.get('Deep_Incoherent',0)*100:.2f}%",
            "Mod_Incoherent"   : f"{fracs.get('Mod_Incoherent',0)*100:.2f}%",
            "Transition"       : f"{fracs.get('Transition',0)*100:.2f}%",
            "Weak_Coherent"    : f"{fracs.get('Weak_Coherent',0)*100:.2f}%",
            "Strong_Coherent"  : f"{fracs.get('Strong_Coherent',0)*100:.2f}%",
            "CoherentTotal"    : f"{rs.get('coherent_frac',0)*100:.2f}%",
            "Entropy(norm)"    : f"{rs.get('norm_entropy',0):.4f}",
        }
        reg_rows.append(row)
    lines.append(_df_to_md(pd.DataFrame(reg_rows), float_fmt=4))
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Market × Allocator ────────────────────────────────────────────────
    lines.append("## Market × Allocator Behaviour")
    lines.append("")
    alloc_rows = []
    for sym in MARKET_ORDER:
        am = all_alloc_metrics.get(sym, {})
        strat_time = am.get("strategy_time", {})
        dominant = max(strat_time, key=strat_time.get) if strat_time else "NO_TRADE"
        row = {
            "Market"          : sym,
            "Deep → "         : "NO_TRADE",
            "Mod → "          : "NO_TRADE",
            "Transition → "   : "NO_TRADE",
            "Weak → "         : "NO_TRADE",
            "Strong → "       : dominant if dominant != "NO_TRADE" else "NO_TRADE",
            "NoTrade%"        : f"{am.get('no_trade_fraction',1.0)*100:.2f}%",
            "Switches"        : int(am.get("strategy_switch_count", 0)),
        }
        alloc_rows.append(row)
    lines.append(_df_to_md(pd.DataFrame(alloc_rows)))
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Universality Tests ────────────────────────────────────────────────
    lines.append("## Universality Tests")
    lines.append("")
    lines.append("### Universality Matrix (Market × Criteria)")
    lines.append("")
    if universality_matrix is not None and len(universality_matrix) > 0:
        lines.append(_df_to_md(universality_matrix))
    lines.append("")
    lines.append("### Universality Scores")
    lines.append("")
    if universality_scores is not None and len(universality_scores) > 0:
        lines.append(_df_to_md(universality_scores))
    lines.append("")
    lines.append(f"**Overall Transport Universality Confidence: {overall_confidence.get('overall_confidence','—')}**  ")
    lines.append(f"- High: {overall_confidence.get('n_high',0)}  ")
    lines.append(f"- Moderate: {overall_confidence.get('n_moderate',0)}  ")
    lines.append(f"- Weak: {overall_confidence.get('n_weak',0)}  ")
    lines.append(f"- Unsupported: {overall_confidence.get('n_unsupported',0)}  ")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Statistical Tests ─────────────────────────────────────────────────
    lines.append("## Statistical Tests (vs EUR/USD Baseline)")
    lines.append("")
    lines.append("Tests: Mann-Whitney U, Permutation (500 iterations), BH FDR correction, Cohen's d")
    lines.append("")
    if stat_tests is not None and len(stat_tests) > 0:
        lines.append(_df_to_md(stat_tests))
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Scientific Questions ──────────────────────────────────────────────
    lines.append("## Scientific Questions — Evidence-Based Answers")
    lines.append("")
    for qa in scientific_qa:
        lines.append(f"### {qa['question']}")
        lines.append("")
        lines.append(f"**Conclusion:** {qa['conclusion']}  ")
        lines.append(f"**Confidence:** {qa['confidence']}  ")
        lines.append("")
        lines.append("**Evidence:**  ")
        ev = qa.get("evidence", {})
        for k, v in ev.items():
            if isinstance(v, dict):
                lines.append(f"- {k}:")
                for kk, vv in v.items():
                    lines.append(f"  - {kk}: {vv}")
            else:
                lines.append(f"- {k}: {v}")
        lines.append("")

    lines.append("---")
    lines.append("")

    # ── Confidence Summary ─────────────────────────────────────────────────
    lines.append("## Confidence Summary")
    lines.append("")
    lines.append("| # | Question | Confidence |")
    lines.append("| - | -------- | ---------- |")
    for i, qa in enumerate(scientific_qa, 1):
        q_short = qa["question"].split(".")[1].strip()[:60]
        lines.append(f"| Q{i} | {q_short} | {qa['confidence']} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Report generated by Phase 3 Transport Universality Validation pipeline.*")
    lines.append("*All transport mathematics, OS parameters, and strategy library are IMMUTABLE from Phase 2.*")
    lines.append("")

    report = "\n".join(lines)
    out_path = PHASE3_DIR / "transport_universality_report.md"
    out_path.write_text(report)
    if verbose:
        print(f"  Saved transport_universality_report.md")
    return report


def write_summary(
    overall_confidence: dict,
    market_summary:     pd.DataFrame,
    universality_scores: pd.DataFrame,
    scientific_qa:      List[dict],
    elapsed_s:          float = 0.0,
    verbose: bool = True,
) -> str:
    """Generate the concise executive summary markdown."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    oc = overall_confidence.get("overall_confidence", "—")
    mean_score = overall_confidence.get("mean_score", 0.0)
    n_high = overall_confidence.get("n_high", 0)
    n_mod  = overall_confidence.get("n_moderate", 0)
    n_weak = overall_confidence.get("n_weak", 0)
    n_unsup = overall_confidence.get("n_unsupported", 0)

    lines = []
    lines.append("# Phase 3 — Summary")
    lines.append(f"**Generated:** {ts}  ")
    lines.append(f"**Elapsed:** {elapsed_s:.1f}s  ")
    lines.append("")
    lines.append("## Objective")
    lines.append("Determine whether the Phase 2 Transport Operating System is domain-agnostic "
                 "across independent financial markets. No parameters were changed. "
                 "Zero recalibration. Identical OS applied to every market.")
    lines.append("")
    lines.append("## Overall Universality Confidence")
    lines.append(f"**{oc}** (mean score: {mean_score:.3f})")
    lines.append("")
    lines.append(f"- High: {n_high} markets")
    lines.append(f"- Moderate: {n_mod} markets")
    lines.append(f"- Weak: {n_weak} markets")
    lines.append(f"- Unsupported: {n_unsup} markets")
    lines.append("")

    lines.append("## Performance Summary")
    if market_summary is not None and len(market_summary) > 0:
        display = market_summary[["Market","PF","Sharpe","MaxDD","Trades","NoTrade_pct"]].copy()
        lines.append(_df_to_md(display))
    lines.append("")

    lines.append("## Universality Scores")
    if universality_scores is not None and len(universality_scores) > 0:
        scores_display = universality_scores[["Market","PF","NoTrade_pct","Score","Rating"]].copy()
        lines.append(_df_to_md(scores_display))
    lines.append("")

    lines.append("## Key Conclusions")
    for qa in scientific_qa:
        conf = qa["confidence"]
        q_short = qa["question"].split(".")[1].strip()[:70]
        lines.append(f"- **{conf}**: {q_short}")
    lines.append("")
    lines.append("*Full details in transport_universality_report.md*")

    summary = "\n".join(lines)
    out_path = PHASE3_DIR / "phase3_summary.md"
    out_path.write_text(summary)
    if verbose:
        print(f"  Saved phase3_summary.md")
    return summary
