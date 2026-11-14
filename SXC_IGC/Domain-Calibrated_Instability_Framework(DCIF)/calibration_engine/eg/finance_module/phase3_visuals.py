"""
phase3_visuals.py — Cross-market visualizations for Phase 3 universality analysis.

Produces:
  - cross_market_heatmap.png    : Market × Metric heatmap
  - cross_market_pf.png         : Profit factor comparison bar chart
  - cross_market_regimes.png    : Regime distribution stacked bar chart
  - cross_market_notradeq.png   : No-trade fraction + Q stats
  - cross_market_markov.png     : Markov transition heatmaps
"""

import sys
import warnings
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

_HERE = Path(__file__).resolve().parent

PHASE3_DIR  = _HERE / "results" / "phase3"
PLOTS_DIR   = PHASE3_DIR / "plots"

REGIMES_5 = [
    "Deep_Incoherent", "Mod_Incoherent", "Transition",
    "Weak_Coherent",   "Strong_Coherent",
]

REGIME_COLORS = {
    "Deep_Incoherent" : "#d73027",
    "Mod_Incoherent"  : "#f46d43",
    "Transition"      : "#fee08b",
    "Weak_Coherent"   : "#74add1",
    "Strong_Coherent" : "#313695",
}

MARKET_ORDER = ["EURUSD", "BTCUSDT", "ETHUSDT", "XAUUSD", "NAS100", "USOIL", "UKOIL"]


def _setup():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    return plt


# ═══════════════════════════════════════════════════════════════════════════
# 1. Cross-market performance heatmap
# ═══════════════════════════════════════════════════════════════════════════

def plot_cross_market_heatmap(market_summary: pd.DataFrame, verbose: bool = True):
    """Heatmap of key metrics across all markets."""
    plt = _setup()
    import matplotlib.pyplot as plt2
    import matplotlib.colors as mcolors

    metrics = ["PF", "Sharpe", "WinRate", "NoTrade_pct", "CoherentFrac", "NormEntropy"]
    available = [m for m in metrics if m in market_summary.columns]

    markets = [m for m in MARKET_ORDER if m in market_summary["Market"].values]
    df_plot = market_summary.set_index("Market").reindex(markets)

    mat = df_plot[available].values.astype(float)

    # Normalise each column to [0, 1] for colour mapping
    mat_norm = np.zeros_like(mat)
    for j in range(mat.shape[1]):
        col = mat[:, j]
        col_min, col_max = np.nanmin(col), np.nanmax(col)
        if col_max > col_min:
            mat_norm[:, j] = (col - col_min) / (col_max - col_min)
        else:
            mat_norm[:, j] = 0.5

    fig, ax = plt2.subplots(figsize=(len(available) * 1.4 + 1, len(markets) * 0.7 + 1.5))
    im = ax.imshow(mat_norm, cmap="RdYlGn", aspect="auto", vmin=0, vmax=1)

    ax.set_xticks(range(len(available)))
    ax.set_xticklabels(available, rotation=30, ha="right", fontsize=9)
    ax.set_yticks(range(len(markets)))
    ax.set_yticklabels(markets, fontsize=9)

    for i in range(len(markets)):
        for j in range(len(available)):
            val = mat[i, j]
            txt = f"{val:.3f}" if not np.isnan(val) else "—"
            ax.text(j, i, txt, ha="center", va="center", fontsize=7,
                    color="black" if 0.2 < mat_norm[i, j] < 0.8 else "white")

    plt2.colorbar(im, ax=ax, label="Normalised value (per column)")
    ax.set_title("Phase 3 — Cross-Market Transport OS: Key Metrics Heatmap", fontsize=11, pad=10)
    plt2.tight_layout()
    out = PLOTS_DIR / "cross_market_heatmap.png"
    plt2.savefig(out, dpi=150, bbox_inches="tight")
    plt2.close()
    if verbose:
        print(f"  Saved cross_market_heatmap.png")


# ═══════════════════════════════════════════════════════════════════════════
# 2. Profit factor comparison
# ═══════════════════════════════════════════════════════════════════════════

def plot_cross_market_pf(market_summary: pd.DataFrame, verbose: bool = True):
    """Bar chart of profit factor across all markets."""
    plt = _setup()
    import matplotlib.pyplot as plt2

    markets = [m for m in MARKET_ORDER if m in market_summary["Market"].values]
    df = market_summary.set_index("Market").reindex(markets)

    pf_vals = df["PF"].values.astype(float)
    colors  = ["#2166ac" if v >= 1.0 else "#d73027" for v in pf_vals]

    fig, ax = plt2.subplots(figsize=(10, 5))
    bars = ax.bar(markets, pf_vals, color=colors, edgecolor="black", linewidth=0.7, alpha=0.85)
    ax.axhline(y=1.0, color="black", linestyle="--", linewidth=1.2, label="PF = 1.0 (breakeven)")

    for bar, val in zip(bars, pf_vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f"{val:.3f}", ha="center", va="bottom", fontsize=9)

    ax.set_ylabel("Profit Factor", fontsize=11)
    ax.set_title("Phase 3 — Transport OS Profit Factor Across Markets\n(Identical OS, zero recalibration)",
                 fontsize=11)
    ax.legend(fontsize=9)
    ax.set_ylim(0, max(pf_vals) * 1.25 + 0.3)
    plt2.tight_layout()
    out = PLOTS_DIR / "cross_market_pf.png"
    plt2.savefig(out, dpi=150, bbox_inches="tight")
    plt2.close()
    if verbose:
        print(f"  Saved cross_market_pf.png")


# ═══════════════════════════════════════════════════════════════════════════
# 3. Regime distribution stacked bar chart
# ═══════════════════════════════════════════════════════════════════════════

def plot_cross_market_regimes(
    all_regime_stats: Dict[str, dict],
    verbose: bool = True,
):
    """Stacked bar chart showing regime time fraction for each market."""
    plt = _setup()
    import matplotlib.pyplot as plt2

    markets = [m for m in MARKET_ORDER if m in all_regime_stats]
    n = len(markets)
    if n == 0:
        return

    regime_data = {r: [] for r in REGIMES_5}
    for sym in markets:
        fracs = all_regime_stats[sym].get("regime_fractions", {})
        for r in REGIMES_5:
            regime_data[r].append(fracs.get(r, 0.0) * 100)

    fig, ax = plt2.subplots(figsize=(12, 5))
    x = np.arange(n)
    bottoms = np.zeros(n)

    for r in REGIMES_5:
        vals = np.array(regime_data[r])
        ax.bar(x, vals, bottom=bottoms, label=r, color=REGIME_COLORS[r], alpha=0.85, edgecolor="white")
        for i, (v, b) in enumerate(zip(vals, bottoms)):
            if v > 3:
                ax.text(x[i], b + v / 2, f"{v:.1f}%", ha="center", va="center",
                        fontsize=7, color="white" if r in ("Deep_Incoherent","Strong_Coherent","Mod_Incoherent") else "black")
        bottoms += vals

    ax.set_xticks(x)
    ax.set_xticklabels(markets, fontsize=10)
    ax.set_ylabel("Time fraction (%)", fontsize=11)
    ax.set_title("Phase 3 — Regime Distribution Across Markets (Identical Q thresholds)", fontsize=11)
    ax.legend(loc="upper right", fontsize=8, ncol=2)
    ax.set_ylim(0, 105)
    plt2.tight_layout()
    out = PLOTS_DIR / "cross_market_regimes.png"
    plt2.savefig(out, dpi=150, bbox_inches="tight")
    plt2.close()
    if verbose:
        print(f"  Saved cross_market_regimes.png")


# ═══════════════════════════════════════════════════════════════════════════
# 4. No-trade fraction + Q statistics
# ═══════════════════════════════════════════════════════════════════════════

def plot_no_trade_and_q(
    market_summary: pd.DataFrame,
    all_alloc_metrics: Dict[str, dict],
    verbose: bool = True,
):
    """Two-panel: no-trade fraction and Q distribution stats."""
    plt = _setup()
    import matplotlib.pyplot as plt2

    markets = [m for m in MARKET_ORDER if m in market_summary["Market"].values]
    df = market_summary.set_index("Market").reindex(markets)

    fig, axes = plt2.subplots(1, 2, figsize=(13, 5))

    # Panel 1: No-trade fraction
    ax = axes[0]
    nt = df["NoTrade_pct"].values.astype(float) if "NoTrade_pct" in df.columns else np.zeros(len(markets))
    colors = ["#2166ac" if v > 80 else "#d73027" for v in nt]
    bars = ax.bar(markets, nt, color=colors, edgecolor="black", alpha=0.8)
    ax.axhline(y=80, color="gray", linestyle="--", linewidth=1, label="80% threshold")
    ax.axhline(y=95.02, color="blue", linestyle=":", linewidth=1, label="EUR/USD baseline (95.02%)")
    for bar, v in zip(bars, nt):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f"{v:.1f}%", ha="center", va="bottom", fontsize=8)
    ax.set_title("No-Trade Fraction per Market", fontsize=10)
    ax.set_ylabel("No-trade %", fontsize=10)
    ax.set_ylim(0, 105)
    ax.legend(fontsize=8)
    ax.tick_params(axis="x", rotation=30)

    # Panel 2: Q mean ± std
    ax2 = axes[1]
    q_means = np.array([all_alloc_metrics.get(m, {}).get("q_mean", 0.0) for m in markets])
    q_stds  = np.array([all_alloc_metrics.get(m, {}).get("q_std",  0.0) for m in markets])
    x = np.arange(len(markets))
    ax2.bar(x, q_means, yerr=q_stds, color="#4575b4", edgecolor="black", alpha=0.8, capsize=5)
    ax2.axhline(y=-1.0, color="red",   linestyle="--", linewidth=1, label="q05 = -1.0")
    ax2.axhline(y=1.73, color="green", linestyle="--", linewidth=1, label="q95 = 1.73")
    ax2.set_xticks(x)
    ax2.set_xticklabels(markets, rotation=30, ha="right", fontsize=9)
    ax2.set_title("Q Distribution (mean ± std) per Market", fontsize=10)
    ax2.set_ylabel("Q value", fontsize=10)
    ax2.legend(fontsize=8)

    plt2.suptitle("Phase 3 — Transport OS: No-Trade Suppression and Q Statistics", fontsize=11, y=1.01)
    plt2.tight_layout()
    out = PLOTS_DIR / "cross_market_notradeq.png"
    plt2.savefig(out, dpi=150, bbox_inches="tight")
    plt2.close()
    if verbose:
        print(f"  Saved cross_market_notradeq.png")


# ═══════════════════════════════════════════════════════════════════════════
# 5. Universality score chart
# ═══════════════════════════════════════════════════════════════════════════

def plot_universality_scores(universality_scores: pd.DataFrame, verbose: bool = True):
    """Bar chart of universality scores with rating labels."""
    plt = _setup()
    import matplotlib.pyplot as plt2

    df = universality_scores.copy()
    markets = [m for m in MARKET_ORDER if m in df["Market"].values]
    df = df.set_index("Market").reindex(markets)

    scores = df["Score"].values.astype(float)
    ratings = df["Rating"].values if "Rating" in df.columns else ["—"] * len(markets)

    rating_colors = {
        "High"       : "#1a9850",
        "Moderate"   : "#a6d96a",
        "Weak"       : "#fdae61",
        "Unsupported": "#d73027",
    }
    colors = [rating_colors.get(r, "#999999") for r in ratings]

    fig, ax = plt2.subplots(figsize=(10, 5))
    bars = ax.bar(markets, scores, color=colors, edgecolor="black", alpha=0.85)
    ax.axhline(y=0.80, color="green",  linestyle="--", linewidth=1, label="High threshold (0.80)")
    ax.axhline(y=0.60, color="orange", linestyle="--", linewidth=1, label="Moderate threshold (0.60)")
    ax.axhline(y=0.40, color="red",    linestyle="--", linewidth=1, label="Weak threshold (0.40)")

    for bar, score, rating in zip(bars, scores, ratings):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f"{score:.2f}\n[{rating}]", ha="center", va="bottom", fontsize=8)

    ax.set_ylabel("Universality Score (0–1)", fontsize=11)
    ax.set_title("Phase 3 — Transport Universality Score by Market", fontsize=11)
    ax.legend(fontsize=8)
    ax.set_ylim(0, 1.15)
    plt2.tight_layout()
    out = PLOTS_DIR / "universality_scores.png"
    plt2.savefig(out, dpi=150, bbox_inches="tight")
    plt2.close()
    if verbose:
        print(f"  Saved universality_scores.png")


# ═══════════════════════════════════════════════════════════════════════════
# 6. Markov transition heatmaps (grid)
# ═══════════════════════════════════════════════════════════════════════════

def plot_markov_grid(
    markov_tables: Dict[str, pd.DataFrame],
    verbose: bool = True,
):
    """Grid of Markov transition heatmaps, one per market."""
    plt = _setup()
    import matplotlib.pyplot as plt2

    markets = [m for m in MARKET_ORDER if m in markov_tables]
    n = len(markets)
    if n == 0:
        return

    ncols = min(4, n)
    nrows = (n + ncols - 1) // ncols
    fig, axes = plt2.subplots(nrows, ncols, figsize=(ncols * 4, nrows * 3.5))
    if n == 1:
        axes = np.array([[axes]])
    elif nrows == 1:
        axes = axes.reshape(1, -1)

    short_labels = [r[:4] for r in REGIMES_5]

    for idx, sym in enumerate(markets):
        row, col = divmod(idx, ncols)
        ax = axes[row, col]
        mat = markov_tables[sym].values.astype(float)
        im = ax.imshow(mat, cmap="Blues", vmin=0, vmax=1)
        ax.set_xticks(range(5)); ax.set_xticklabels(short_labels, fontsize=7, rotation=45)
        ax.set_yticks(range(5)); ax.set_yticklabels(short_labels, fontsize=7)
        ax.set_title(sym, fontsize=9)
        for i in range(5):
            for j in range(5):
                v = mat[i, j]
                ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                        fontsize=6, color="white" if v > 0.6 else "black")

    # Hide empty subplots
    for idx in range(n, nrows * ncols):
        row, col = divmod(idx, ncols)
        axes[row, col].set_visible(False)

    plt2.suptitle("Phase 3 — Markov Transition Matrices by Market", fontsize=11)
    plt2.tight_layout()
    out = PLOTS_DIR / "cross_market_markov.png"
    plt2.savefig(out, dpi=150, bbox_inches="tight")
    plt2.close()
    if verbose:
        print(f"  Saved cross_market_markov.png")


# ═══════════════════════════════════════════════════════════════════════════
# Master call
# ═══════════════════════════════════════════════════════════════════════════

def run_all_visuals(
    market_summary:    pd.DataFrame,
    all_regime_stats:  Dict[str, dict],
    all_alloc_metrics: Dict[str, dict],
    markov_tables:     Dict[str, pd.DataFrame],
    universality_scores: pd.DataFrame,
    verbose: bool = True,
):
    """Run all Phase 3 visualizations."""
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    if verbose:
        print("  Generating Phase 3 visualizations …", flush=True)

    try:
        plot_cross_market_heatmap(market_summary, verbose)
    except Exception as e:
        print(f"  WARNING heatmap: {e}")

    try:
        plot_cross_market_pf(market_summary, verbose)
    except Exception as e:
        print(f"  WARNING pf chart: {e}")

    try:
        plot_cross_market_regimes(all_regime_stats, verbose)
    except Exception as e:
        print(f"  WARNING regime chart: {e}")

    try:
        plot_no_trade_and_q(market_summary, all_alloc_metrics, verbose)
    except Exception as e:
        print(f"  WARNING no-trade/Q chart: {e}")

    try:
        plot_universality_scores(universality_scores, verbose)
    except Exception as e:
        print(f"  WARNING universality scores: {e}")

    try:
        plot_markov_grid(markov_tables, verbose)
    except Exception as e:
        print(f"  WARNING markov grid: {e}")
