"""
p2_visualize.py — Visualizations for Phase 2 Transport OS.

Outputs:
  allocator_heatmap.png         — strategy selected per regime (counts + risk)
  strategy_switch_timeline.png  — selected strategy over time
  risk_budget_timeline.png      — risk fraction over time
  equity_curves.png             — cumulative returns: OS vs all baselines
  performance_comparison.png    — bar chart of key metrics
  regime_strategy_matrix.png    — regime × strategy frequency heatmap
"""

import sys
import warnings
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

_HERE = Path(__file__).resolve().parent
PHASE2_DIR = _HERE / "results" / "phase2"

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

try:
    import seaborn as sns
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False

REGIME_COLORS = {
    "Deep_Incoherent" : "#8B0000",
    "Mod_Incoherent"  : "#FF6B6B",
    "Transition"      : "#FFD700",
    "Weak_Coherent"   : "#90EE90",
    "Strong_Coherent" : "#006400",
}
BASELINE_COLORS = [
    "#2196F3", "#FF5722", "#4CAF50", "#9C27B0", "#FF9800", "#607D8B"
]


def plot_allocator_heatmap(dec_df: pd.DataFrame, out_dir: Path):
    """Heatmap: regime × strategy frequency with risk as annotation."""
    if len(dec_df) == 0:
        return

    regimes = ["Deep_Incoherent", "Mod_Incoherent", "Transition",
               "Weak_Coherent",   "Strong_Coherent"]
    strategies = [s for s in dec_df["selected_strategy"].unique() if s != "NO_TRADE"]
    strategies = sorted(strategies)
    all_strats = strategies + ["NO_TRADE"]

    # Frequency table
    ct = pd.crosstab(dec_df["regime"], dec_df["selected_strategy"])
    ct = ct.reindex(index=regimes, columns=all_strats, fill_value=0)
    ct_pct = ct.div(ct.sum(axis=1) + 1e-6, axis=0) * 100

    fig, ax = plt.subplots(figsize=(max(8, len(all_strats) * 1.4), 5))
    data = ct_pct.values.astype(float)

    if HAS_SEABORN:
        sns.heatmap(data, ax=ax, annot=True, fmt=".1f", cmap="YlOrRd",
                    xticklabels=all_strats, yticklabels=regimes,
                    cbar_kws={"label": "% of bars"}, linewidths=0.5)
    else:
        im = ax.imshow(data, cmap="YlOrRd", aspect="auto")
        ax.set_xticks(range(len(all_strats)))
        ax.set_xticklabels(all_strats, rotation=45, ha="right")
        ax.set_yticks(range(len(regimes)))
        ax.set_yticklabels(regimes)
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                ax.text(j, i, f"{data[i,j]:.1f}%", ha="center", va="center", fontsize=8)
        plt.colorbar(im, ax=ax, label="% of bars")

    ax.set_title("Transport OS: Regime × Strategy Frequency Heatmap\n"
                 "(% of bars where each strategy is selected per regime)",
                 fontweight="bold")
    ax.set_xlabel("Selected Strategy")
    ax.set_ylabel("Q Regime")
    plt.tight_layout()
    fig.savefig(out_dir / "allocator_heatmap.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  Saved: allocator_heatmap.png")


def plot_strategy_switch_timeline(dec_df: pd.DataFrame, out_dir: Path):
    """Strategy selection over time (sampled for readability)."""
    if len(dec_df) == 0:
        return

    strategies = sorted(dec_df["selected_strategy"].unique())
    strat_idx  = {s: i for i, s in enumerate(strategies)}
    cmap       = plt.get_cmap("tab20", len(strategies))

    # Sample every 12 bars (1 per hour)
    df_sub = dec_df.iloc[::12].copy()
    df_sub["strat_i"] = df_sub["selected_strategy"].map(strat_idx).fillna(-1)

    fig, axes = plt.subplots(2, 1, figsize=(16, 7), sharex=True)

    # Top: strategy selection as coloured scatter
    ax = axes[0]
    for i, strat in enumerate(strategies):
        mask = df_sub["selected_strategy"] == strat
        ax.scatter(df_sub.loc[mask, "timestamp"], df_sub.loc[mask, "strat_i"],
                   c=[cmap(i)], s=4, alpha=0.7, label=strat)
    ax.set_yticks(range(len(strategies)))
    ax.set_yticklabels(strategies, fontsize=8)
    ax.set_title("Strategy Switch Timeline (sampled hourly)", fontweight="bold")
    ax.set_ylabel("Active Strategy")
    ax.legend(loc="upper right", fontsize=7, ncol=3)

    # Bottom: Q value coloured by regime
    ax = axes[1]
    for regime, color in REGIME_COLORS.items():
        mask = dec_df.iloc[::12]["regime"] == regime
        ax.scatter(df_sub.loc[mask, "timestamp"], df_sub.loc[mask, "Q"],
                   c=color, s=2, alpha=0.5, label=regime)
    ax.axhline(0, color="black", lw=1, ls="--")
    ax.set_title("Q Values by Regime", fontweight="bold")
    ax.set_ylabel("Q")
    ax.legend(loc="upper right", fontsize=7, ncol=3)
    ax.set_xlabel("Date")

    plt.tight_layout()
    fig.savefig(out_dir / "strategy_switch_timeline.png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    print("  Saved: strategy_switch_timeline.png")


def plot_risk_budget_timeline(dec_df: pd.DataFrame, out_dir: Path):
    """Risk fraction budget over time."""
    if len(dec_df) == 0:
        return

    df_sub = dec_df.iloc[::12].copy()

    fig, axes = plt.subplots(2, 1, figsize=(16, 6), sharex=True)

    ax = axes[0]
    ax.fill_between(df_sub["timestamp"], df_sub["risk_fraction"],
                    alpha=0.6, color="#2196F3", label="Risk Fraction")
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("Risk Fraction")
    ax.set_title("Transport OS: Risk Budget Over Time", fontweight="bold")
    ax.legend(loc="upper right")
    ax.axhline(0.25, color="orange", lw=1, ls="--", label="min risk")
    ax.axhline(1.0, color="red", lw=1, ls="--", label="max risk")

    ax = axes[1]
    # Colour bars by regime
    for regime, color in REGIME_COLORS.items():
        mask = df_sub["regime"] == regime
        ax.bar(df_sub.loc[mask, "timestamp"], 1,
               width=pd.Timedelta("5min") * 12, color=color,
               alpha=0.7, label=regime)
    ax.set_ylim(0, 1)
    ax.set_ylabel("Active Regime")
    ax.set_title("Q Regime State", fontweight="bold")
    ax.legend(loc="upper right", fontsize=7, ncol=3)
    ax.set_xlabel("Date")

    plt.tight_layout()
    fig.savefig(out_dir / "risk_budget_timeline.png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    print("  Saved: risk_budget_timeline.png")


def plot_equity_curves(
    os_trades: pd.DataFrame,
    baseline_trades: Dict[str, pd.DataFrame],
    out_dir: Path,
):
    """Cumulative return curves: OS vs all baselines."""
    fig, ax = plt.subplots(figsize=(14, 7))

    ret_col = "scaled_net" if "scaled_net" in os_trades.columns else "net_ret"

    def _equity_curve(trades, col):
        if len(trades) == 0:
            return None, None
        if "exit_ts" in trades.columns:
            t = trades.sort_values("exit_ts")
        else:
            t = trades
        returns = t[col].dropna().values
        eq = np.cumsum(returns)
        return t.index if "exit_ts" not in trades.columns else t["exit_ts"].values, eq

    # Transport OS
    ts, eq = _equity_curve(os_trades, ret_col)
    if ts is not None:
        ax.plot(ts, eq, lw=2.5, color="#E53935", label="Transport OS", zorder=5)
        # Drawdown fill
        running = np.maximum.accumulate(eq)
        dd = running - eq
        ax.fill_between(ts, eq, running, where=dd > 0, alpha=0.15, color="#E53935")

    # Baselines
    for i, (bname, bdf) in enumerate(baseline_trades.items()):
        b_col = "scaled_net" if "scaled_net" in bdf.columns else "net_ret"
        ts_b, eq_b = _equity_curve(bdf, b_col)
        if ts_b is not None:
            color = BASELINE_COLORS[i % len(BASELINE_COLORS)]
            ax.plot(ts_b, eq_b, lw=1.2, color=color, alpha=0.75,
                    ls="--", label=bname)

    ax.axhline(0, color="black", lw=1, ls="-")
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative Return (risk-scaled)")
    ax.set_title("Transport OS vs Fixed Baselines — Equity Curves",
                 fontsize=13, fontweight="bold")
    ax.legend(loc="upper left", fontsize=9)
    plt.tight_layout()
    fig.savefig(out_dir / "equity_curves.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  Saved: equity_curves.png")


def plot_performance_comparison(comp_df: pd.DataFrame, out_dir: Path):
    """Bar chart comparison of key metrics."""
    if len(comp_df) == 0:
        return

    metrics = ["profit_factor", "sharpe", "max_drawdown", "win_rate", "trade_count"]
    titles  = ["Profit Factor", "Sharpe Ratio", "Max Drawdown", "Win Rate", "Trade Count"]
    n_metrics = len(metrics)

    fig, axes = plt.subplots(1, n_metrics, figsize=(4 * n_metrics, 5))

    labels = comp_df["label"].tolist()
    colors = ["#E53935"] + BASELINE_COLORS[:len(labels)-1]

    for ax, m, t in zip(axes, metrics, titles):
        vals = comp_df[m].fillna(0).values
        bars = ax.bar(range(len(labels)), vals, color=colors, edgecolor="white")
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
        ax.set_title(t, fontweight="bold", fontsize=10)
        ax.axhline(0, color="black", lw=0.5)
        for bar, val in zip(bars, vals):
            if not np.isnan(val):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                        f"{val:.3f}", ha="center", va="bottom", fontsize=7)

    fig.suptitle("Phase 2: Performance Comparison — Transport OS vs Fixed Baselines",
                 fontsize=12, fontweight="bold")
    plt.tight_layout()
    fig.savefig(out_dir / "performance_comparison.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  Saved: performance_comparison.png")


def run_all_visualizations(
    os_trades: pd.DataFrame,
    baseline_trades: Dict[str, pd.DataFrame],
    dec_df: pd.DataFrame,
    comp_df: pd.DataFrame,
    verbose: bool = True,
):
    """Run all Phase 2 visualizations."""
    out = PHASE2_DIR / "plots"
    out.mkdir(parents=True, exist_ok=True)

    if verbose:
        print("  Plotting allocator heatmap …", flush=True)
    plot_allocator_heatmap(dec_df, out)

    if verbose:
        print("  Plotting strategy switch timeline …", flush=True)
    plot_strategy_switch_timeline(dec_df, out)

    if verbose:
        print("  Plotting risk budget timeline …", flush=True)
    plot_risk_budget_timeline(dec_df, out)

    if verbose:
        print("  Plotting equity curves …", flush=True)
    plot_equity_curves(os_trades, baseline_trades, out)

    if verbose:
        print("  Plotting performance comparison …", flush=True)
    plot_performance_comparison(comp_df, out)

    if verbose:
        print(f"  All plots saved to {out}", flush=True)
