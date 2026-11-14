"""
p4_allocator_discovery.py — Market-specific allocator discovery.

For every (market, regime), selects the best strategy family purely from
measured statistics. No manual design. No EUR/USD transfer.

Selection rule (composite score):
  score = 0.4×PF_rank + 0.3×Sharpe_rank + 0.2×WinRate_rank + 0.1×Expectancy_rank
  (all ranks normalised within regime×market cell)
  Minimum MIN_TRADES required to qualify.
  If best PF < 0.85 across all strategies → NO_TRADE.

Family-level aggregation:
  Each family's score = median of its member strategy scores in that regime.
  Best family = highest family score.

Outputs:
  - allocator_by_market.csv    : market×regime → best strategy, family, confidence
  - allocator_by_regime.csv    : regime → most common family across markets
  - allocator_confidence.csv   : confidence levels per market×regime
"""

import sys
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

_HERE = Path(__file__).resolve().parent
PHASE4_DIR = _HERE / "results" / "phase4"

REGIMES_5   = ["Deep_Incoherent","Mod_Incoherent","Transition","Weak_Coherent","Strong_Coherent"]
MARKET_ORDER = ["EURUSD","BTCUSDT","ETHUSDT","XAUUSD","NAS100","USOIL","UKOIL"]

MIN_TRADES    = 5    # minimum trades in a regime cell to qualify
PF_THRESHOLD  = 0.85 # below this PF for all strategies → NO_TRADE


def _rank_norm(series: pd.Series) -> pd.Series:
    mn, mx = series.min(), series.max()
    if mx <= mn:
        return pd.Series(0.5, index=series.index)
    return (series - mn) / (mx - mn + 1e-12)


def discover_allocator_for_market(
    metrics_df: pd.DataFrame,
    symbol: str,
) -> pd.DataFrame:
    """
    Discover best strategy family per regime for one market.

    Returns DataFrame with columns:
      symbol, regime, best_strategy, best_family, composite_score,
      profit_factor, sharpe, win_rate, trade_count, confidence,
      runner_up_family, runner_up_score
    """
    rows = []

    for regime in REGIMES_5:
        sub = metrics_df[
            (metrics_df["regime"] == regime) &
            (metrics_df["trade_count"] >= MIN_TRADES)
        ].copy()

        if len(sub) == 0:
            rows.append(_no_trade_row(symbol, regime, "Insufficient data"))
            continue

        # Composite score per strategy
        sub["pf_n"]  = _rank_norm(sub["profit_factor"].fillna(0))
        sub["sr_n"]  = _rank_norm(sub["sharpe"].fillna(-99))
        sub["wr_n"]  = _rank_norm(sub["win_rate"].fillna(0))
        sub["ex_n"]  = _rank_norm(sub["expectancy"].fillna(-1))
        sub["score"] = (0.4*sub["pf_n"] + 0.3*sub["sr_n"] +
                        0.2*sub["wr_n"] + 0.1*sub["ex_n"])

        # Aggregate to family level
        family_scores = sub.groupby("family")["score"].median().sort_values(ascending=False)
        family_pf     = sub.groupby("family")["profit_factor"].median()

        if len(family_scores) == 0:
            rows.append(_no_trade_row(symbol, regime, "No families"))
            continue

        best_fam      = family_scores.index[0]
        best_fam_score= float(family_scores.iloc[0])
        best_fam_pf   = float(family_pf.get(best_fam, 0.0))

        runner_up = family_scores.index[1] if len(family_scores) > 1 else "—"
        runner_up_score = float(family_scores.iloc[1]) if len(family_scores) > 1 else 0.0

        # NO_TRADE if best family PF below threshold
        if best_fam_pf < PF_THRESHOLD:
            rows.append(_no_trade_row(symbol, regime, f"Best PF={best_fam_pf:.3f}<{PF_THRESHOLD}"))
            continue

        # Best individual strategy in best family
        best_sub = sub[sub["family"] == best_fam].sort_values("score", ascending=False)
        best_strat = str(best_sub.iloc[0]["strategy"])
        best_tc    = int(best_sub.iloc[0]["trade_count"])
        best_pf    = float(best_sub.iloc[0]["profit_factor"])
        best_sr    = float(best_sub.iloc[0]["sharpe"])
        best_wr    = float(best_sub.iloc[0]["win_rate"])

        # Confidence
        if best_pf > 1.2 and best_tc >= 20 and best_sr > 0:
            conf = "High"
        elif best_pf > 1.05 and best_tc >= MIN_TRADES:
            conf = "Moderate"
        elif best_pf > PF_THRESHOLD:
            conf = "Weak"
        else:
            conf = "Unsupported"

        rows.append({
            "symbol"          : symbol,
            "regime"          : regime,
            "best_strategy"   : best_strat,
            "best_family"     : best_fam,
            "composite_score" : best_fam_score,
            "profit_factor"   : best_pf,
            "sharpe"          : best_sr,
            "win_rate"        : best_wr,
            "trade_count"     : best_tc,
            "confidence"      : conf,
            "verdict"         : f"{best_strat} ({best_fam}) PF={best_pf:.3f}",
            "runner_up_family": runner_up,
            "runner_up_score" : runner_up_score,
        })

    return pd.DataFrame(rows)


def _no_trade_row(symbol, regime, reason):
    return {"symbol": symbol, "regime": regime,
            "best_strategy": "NO_TRADE", "best_family": "NoTrade",
            "composite_score": 0.0, "profit_factor": 0.0,
            "sharpe": 0.0, "win_rate": 0.0, "trade_count": 0,
            "confidence": "Weak", "verdict": reason,
            "runner_up_family": "—", "runner_up_score": 0.0}


def discover_all_markets(
    all_metrics: Dict[str, pd.DataFrame],
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Run discovery for all markets.

    Returns:
      allocator_df    : allocator_by_market (market×regime → family)
      regime_df       : allocator_by_regime (regime → most common family)
      confidence_df   : confidence breakdown
    """
    market_frames = []
    for symbol in MARKET_ORDER:
        if symbol not in all_metrics:
            continue
        df = discover_allocator_for_market(all_metrics[symbol], symbol)
        market_frames.append(df)

    if not market_frames:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    allocator_df = pd.concat(market_frames, ignore_index=True)

    # Per-regime cross-market summary
    regime_rows = []
    for regime in REGIMES_5:
        sub = allocator_df[allocator_df["regime"] == regime]
        fam_counts = sub["best_family"].value_counts()
        most_common = fam_counts.index[0] if len(fam_counts) > 0 else "NoTrade"
        n_no_trade  = int((sub["best_family"] == "NoTrade").sum())
        n_markets   = len(sub)
        regime_rows.append({
            "regime"          : regime,
            "most_common_family": most_common,
            "n_markets_using" : int(fam_counts.get(most_common, 0)),
            "n_no_trade"      : n_no_trade,
            "n_markets_total" : n_markets,
            "family_diversity": len(fam_counts),
            "families_seen"   : ", ".join(fam_counts.index.tolist()),
        })
    regime_df = pd.DataFrame(regime_rows)

    # Confidence summary
    conf_rows = []
    for symbol in MARKET_ORDER:
        sub = allocator_df[allocator_df["symbol"] == symbol]
        for _, row in sub.iterrows():
            conf_rows.append({
                "symbol"   : symbol,
                "regime"   : row["regime"],
                "family"   : row["best_family"],
                "strategy" : row["best_strategy"],
                "confidence": row["confidence"],
                "PF"       : row["profit_factor"],
                "trades"   : row["trade_count"],
            })
    confidence_df = pd.DataFrame(conf_rows)

    return allocator_df, regime_df, confidence_df


def build_cross_market_allocator_table(allocator_df: pd.DataFrame) -> pd.DataFrame:
    """
    Pivot to Market × Regime table showing best family.
    Rows = markets, columns = regimes.
    """
    if allocator_df is None or len(allocator_df) == 0:
        return pd.DataFrame()
    pivot = allocator_df.pivot_table(
        index="symbol",
        columns="regime",
        values="best_family",
        aggfunc="first",
    )
    pivot = pivot.reindex(index=MARKET_ORDER, columns=REGIMES_5)
    pivot = pivot.fillna("NoTrade")
    pivot.columns.name = None
    pivot.index.name   = "Market"
    return pivot.reset_index()


def build_allocator_transition_matrix(allocator_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build allocator transition matrix: for each market, what family is chosen
    as regime transitions across the Markov chain?
    Rows = from_regime, Cols = to_regime, Values = most common family transition.
    """
    if allocator_df is None or len(allocator_df) == 0:
        return pd.DataFrame()

    # For each market, get the regime sequence and map to family
    records = []
    for symbol in MARKET_ORDER:
        sub = allocator_df[allocator_df["symbol"] == symbol].set_index("regime")
        for r_from in REGIMES_5:
            for r_to in REGIMES_5:
                fam_from = sub.loc[r_from, "best_family"] if r_from in sub.index else "NoTrade"
                fam_to   = sub.loc[r_to,   "best_family"] if r_to   in sub.index else "NoTrade"
                records.append({"symbol": symbol, "from_regime": r_from,
                                 "to_regime": r_to, "from_family": fam_from,
                                 "to_family": fam_to})
    return pd.DataFrame(records)


def compute_allocator_entropy(allocator_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute entropy of family selection per market.
    High entropy = diverse family use. Low entropy = concentrated.
    """
    rows = []
    for symbol in MARKET_ORDER:
        sub = allocator_df[allocator_df["symbol"] == symbol]
        fam_counts = sub["best_family"].value_counts(normalize=True)
        p = fam_counts.values
        p = p[p > 0]
        H = float(-np.sum(p * np.log(p))) if len(p) > 0 else 0.0
        H_norm = H / np.log(len(fam_counts)) if len(fam_counts) > 1 else 0.0
        rows.append({
            "symbol"         : symbol,
            "n_families_used": len(fam_counts),
            "entropy"        : H,
            "norm_entropy"   : H_norm,
            "families"       : ", ".join(fam_counts.index.tolist()),
        })
    return pd.DataFrame(rows)


def build_scheduler_similarity_matrix(allocator_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute pairwise Jaccard similarity of allocators across markets.
    Similarity = fraction of regimes with same best_family choice.
    """
    if allocator_df is None or len(allocator_df) == 0:
        return pd.DataFrame()

    markets = [m for m in MARKET_ORDER if m in allocator_df["symbol"].values]
    n = len(markets)
    mat = np.zeros((n, n))

    for i, m1 in enumerate(markets):
        for j, m2 in enumerate(markets):
            s1 = allocator_df[allocator_df["symbol"] == m1].set_index("regime")["best_family"]
            s2 = allocator_df[allocator_df["symbol"] == m2].set_index("regime")["best_family"]
            common = s1.index.intersection(s2.index)
            if len(common) == 0:
                mat[i, j] = 0.0
            else:
                matches = sum(s1.loc[r] == s2.loc[r] for r in common)
                mat[i, j] = matches / len(common)

    return pd.DataFrame(mat, index=markets, columns=markets)


def build_family_rankings(all_metrics: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Rank strategy families across all markets and regimes by median PF.
    """
    frames = [df for df in all_metrics.values() if df is not None and len(df) > 0]
    if not frames:
        return pd.DataFrame()
    combined = pd.concat(frames, ignore_index=True)
    combined = combined[combined["regime"] != "ALL"]
    combined = combined[combined["trade_count"] >= MIN_TRADES]

    rows = []
    for regime in REGIMES_5:
        sub = combined[combined["regime"] == regime]
        if len(sub) == 0:
            continue
        fam_stats = sub.groupby("family").agg(
            median_pf   =("profit_factor", "median"),
            mean_sharpe =("sharpe",        "mean"),
            total_trades=("trade_count",   "sum"),
            n_market_regime=("symbol",     "nunique"),
        ).reset_index()
        fam_stats["regime"] = regime
        rows.append(fam_stats)

    if not rows:
        return pd.DataFrame()
    result = pd.concat(rows, ignore_index=True)
    result = result.sort_values(["regime","median_pf"], ascending=[True,False])
    return result
