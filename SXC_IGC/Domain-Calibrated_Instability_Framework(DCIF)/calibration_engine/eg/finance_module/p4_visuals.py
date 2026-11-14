"""
p4_visuals.py — Phase 4 visualizations.

Produces:
  allocator_heatmap.png          Market×Regime family heatmap
  scheduler_similarity_heatmap.png  Pairwise allocator similarity
  pl_vs_field_heatmap.png        PL median PF vs field
  family_rankings_heatmap.png    Family median PF per regime×market
"""

import warnings
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

_HERE      = Path(__file__).resolve().parent
PHASE4_DIR = _HERE / "results" / "phase4"
PLOTS_DIR  = PHASE4_DIR / "plots"

REGIMES_5    = ["Deep_Incoherent","Mod_Incoherent","Transition","Weak_Coherent","Strong_Coherent"]
MARKET_ORDER = ["EURUSD","BTCUSDT","ETHUSDT","XAUUSD","NAS100","USOIL","UKOIL"]

FAMILY_COLORS = {
    "Trend":           "#1f77b4",
    "Momentum":        "#ff7f0e",
    "MeanReversion":   "#2ca02c",
    "Breakout":        "#d62728",
    "Scalping":        "#9467bd",
    "Session":         "#8c564b",
    "Volatility":      "#e377c2",
    "PassiveLiquidity":"#17becf",
    "NoTrade":         "#7f7f7f",
}

FAMILY_ORDER = list(FAMILY_COLORS.keys())


def _setup():
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    return plt


def _fam_to_int(fam: str) -> int:
    return FAMILY_ORDER.index(fam) if fam in FAMILY_ORDER else len(FAMILY_ORDER)


# ═══════════════════════════════════════════════════════════════════════════
# 1. Allocator heatmap  (Market × Regime → best family)
# ═══════════════════════════════════════════════════════════════════════════

def plot_allocator_heatmap(cross_market_df: pd.DataFrame, verbose=True):
    plt = _setup()
    import matplotlib.pyplot as plt2
    from matplotlib.patches import Patch

    markets = [m for m in MARKET_ORDER if m in cross_market_df["Market"].values]
    df = cross_market_df.set_index("Market").reindex(markets)

    nrows, ncols = len(markets), len(REGIMES_5)
    mat = np.zeros((nrows, ncols), dtype=int)
    for i, m in enumerate(markets):
        for j, r in enumerate(REGIMES_5):
            fam = str(df.loc[m, r]) if r in df.columns else "NoTrade"
            mat[i, j] = _fam_to_int(fam)

    cmap_vals = [FAMILY_COLORS.get(f, "#aaaaaa") for f in FAMILY_ORDER + ["Unknown"]]
    from matplotlib.colors import ListedColormap
    cmap = ListedColormap(cmap_vals)

    fig, ax = plt2.subplots(figsize=(12, 5))
    im = ax.imshow(mat, cmap=cmap, vmin=0, vmax=len(FAMILY_ORDER), aspect="auto")

    for i in range(nrows):
        for j in range(ncols):
            fam = str(df.iloc[i][REGIMES_5[j]]) if REGIMES_5[j] in df.columns else "NoTrade"
            short = fam[:6] if fam != "PassiveLiquidity" else "PL"
            ax.text(j, i, short, ha="center", va="center", fontsize=8,
                    color="white" if fam in ("Trend","MeanReversion","Scalping","Session","NoTrade") else "black")

    ax.set_xticks(range(ncols))
    ax.set_xticklabels([r.replace("_","\n") for r in REGIMES_5], fontsize=8)
    ax.set_yticks(range(nrows))
    ax.set_yticklabels(markets, fontsize=9)
    ax.set_title("Phase 4 — Market-Specific Allocator Discovery\n(Best Family per Market×Regime)", fontsize=11)

    legend = [Patch(facecolor=FAMILY_COLORS[f], label=f) for f in FAMILY_ORDER]
    ax.legend(handles=legend, loc="upper right", bbox_to_anchor=(1.22, 1), fontsize=7)
    plt2.tight_layout()
    out = PLOTS_DIR / "allocator_heatmap.png"
    plt2.savefig(out, dpi=150, bbox_inches="tight")
    plt2.close()
    if verbose: print(f"  Saved allocator_heatmap.png")


# ═══════════════════════════════════════════════════════════════════════════
# 2. Scheduler similarity heatmap
# ═══════════════════════════════════════════════════════════════════════════

def plot_scheduler_similarity(sim_matrix: pd.DataFrame, verbose=True):
    plt = _setup()
    import matplotlib.pyplot as plt2

    markets = [m for m in MARKET_ORDER if m in sim_matrix.index]
    mat = sim_matrix.reindex(index=markets, columns=markets).values.astype(float)

    fig, ax = plt2.subplots(figsize=(8, 6))
    im = ax.imshow(mat, cmap="YlOrRd", vmin=0, vmax=1)
    plt2.colorbar(im, ax=ax, label="Jaccard similarity (fraction of regimes with same family)")

    for i in range(len(markets)):
        for j in range(len(markets)):
            ax.text(j, i, f"{mat[i,j]:.2f}", ha="center", va="center",
                    fontsize=9, color="black" if mat[i,j] < 0.6 else "white")

    ax.set_xticks(range(len(markets))); ax.set_xticklabels(markets, rotation=30, ha="right", fontsize=9)
    ax.set_yticks(range(len(markets))); ax.set_yticklabels(markets, fontsize=9)
    ax.set_title("Phase 4 — Scheduler Similarity Matrix\n(Jaccard: same family choice per regime)", fontsize=11)
    plt2.tight_layout()
    out = PLOTS_DIR / "scheduler_similarity_heatmap.png"
    plt2.savefig(out, dpi=150, bbox_inches="tight")
    plt2.close()
    if verbose: print(f"  Saved scheduler_similarity_heatmap.png")


# ═══════════════════════════════════════════════════════════════════════════
# 3. PL vs field comparison heatmap
# ═══════════════════════════════════════════════════════════════════════════

def plot_pl_vs_field(pl_stats: pd.DataFrame, verbose=True):
    plt = _setup()
    import matplotlib.pyplot as plt2

    markets = [m for m in MARKET_ORDER if m in pl_stats["symbol"].values]
    nrows, ncols = len(markets), len(REGIMES_5)
    mat_diff = np.full((nrows, ncols), np.nan)
    mat_wins = np.zeros((nrows, ncols), dtype=int)

    for i, sym in enumerate(markets):
        for j, reg in enumerate(REGIMES_5):
            row = pl_stats[(pl_stats["symbol"]==sym) & (pl_stats["regime"]==reg)]
            if len(row) > 0:
                mat_diff[i, j] = float(row["pl_vs_other_diff"].iloc[0])
                mat_wins[i, j] = int(row["pl_wins"].iloc[0])

    fig, ax = plt2.subplots(figsize=(12, 5))
    im = ax.imshow(mat_diff, cmap="RdYlGn", vmin=-0.5, vmax=0.5, aspect="auto")
    plt2.colorbar(im, ax=ax, label="PL median PF − Other median PF")

    for i in range(nrows):
        for j in range(ncols):
            v = mat_diff[i, j]
            if not np.isnan(v):
                sign = "▲" if mat_wins[i,j] else "▼"
                ax.text(j, i, f"{sign}{v:+.2f}", ha="center", va="center", fontsize=8)

    ax.set_xticks(range(ncols))
    ax.set_xticklabels([r.replace("_","\n") for r in REGIMES_5], fontsize=8)
    ax.set_yticks(range(nrows)); ax.set_yticklabels(markets, fontsize=9)
    ax.set_title("Phase 4 — Passive Liquidity vs Field\n(PL median PF minus all other families' median PF)", fontsize=11)
    plt2.tight_layout()
    out = PLOTS_DIR / "pl_vs_field_heatmap.png"
    plt2.savefig(out, dpi=150, bbox_inches="tight")
    plt2.close()
    if verbose: print(f"  Saved pl_vs_field_heatmap.png")


# ═══════════════════════════════════════════════════════════════════════════
# 4. Family rankings bar chart per regime
# ═══════════════════════════════════════════════════════════════════════════

def plot_family_rankings(family_rankings: pd.DataFrame, verbose=True):
    plt = _setup()
    import matplotlib.pyplot as plt2

    nrows = len(REGIMES_5)
    fig, axes = plt2.subplots(1, nrows, figsize=(16, 5), sharey=False)
    if nrows == 1:
        axes = [axes]

    for ax, regime in zip(axes, REGIMES_5):
        sub = family_rankings[family_rankings["regime"] == regime].copy()
        if len(sub) == 0:
            ax.set_title(regime[:8], fontsize=8); continue
        sub = sub.sort_values("median_pf", ascending=True)
        colors = [FAMILY_COLORS.get(f, "#aaaaaa") for f in sub["family"]]
        ax.barh(sub["family"], sub["median_pf"], color=colors, edgecolor="black", linewidth=0.5)
        ax.axvline(x=1.0, color="black", linestyle="--", linewidth=0.8)
        ax.set_title(regime.replace("_","\n"), fontsize=7)
        ax.set_xlabel("Median PF", fontsize=7)
        ax.tick_params(labelsize=7)

    plt2.suptitle("Phase 4 — Strategy Family Rankings by Regime (Median Profit Factor)", fontsize=10)
    plt2.tight_layout()
    out = PLOTS_DIR / "family_rankings_heatmap.png"
    plt2.savefig(out, dpi=150, bbox_inches="tight")
    plt2.close()
    if verbose: print(f"  Saved family_rankings_heatmap.png")


# ═══════════════════════════════════════════════════════════════════════════
# Master
# ═══════════════════════════════════════════════════════════════════════════

def run_all_visuals(
    cross_market_df:   pd.DataFrame,
    sim_matrix:        pd.DataFrame,
    pl_stats:          pd.DataFrame,
    family_rankings:   pd.DataFrame,
    verbose: bool = True,
):
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    for fn, args, label in [
        (plot_allocator_heatmap,   (cross_market_df,), "allocator_heatmap"),
        (plot_scheduler_similarity,(sim_matrix,),       "scheduler_similarity"),
        (plot_pl_vs_field,         (pl_stats,),         "pl_vs_field"),
        (plot_family_rankings,     (family_rankings,),  "family_rankings"),
    ]:
        try:
            fn(*args, verbose=verbose)
        except Exception as e:
            if verbose: print(f"  WARNING {label}: {e}")
