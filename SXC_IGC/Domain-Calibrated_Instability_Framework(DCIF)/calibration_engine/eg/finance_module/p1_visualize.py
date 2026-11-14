"""
p1_visualize.py — Heatmap and visualization for Phase 1.

Outputs:
  - results/phase1/plots/strategy_regime_heatmap.png  (profit factor)
  - results/phase1/plots/strategy_regime_heatmap_sharpe.png
  - results/phase1/plots/regime_markov.png
  - results/phase1/plots/regime_durations.png
  - results/phase1/plots/regime_q_distribution.png
"""

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

_HERE = Path(__file__).resolve().parent
_CE   = _HERE.parents[1]
for p in [str(_CE), str(_HERE)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from p1_checkpoint import RESULTS_DIR, q_series_path, mark_heatmap_complete

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

try:
    import seaborn as sns
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False

REGIMES_5 = [
    "Deep_Incoherent",
    "Mod_Incoherent",
    "Transition",
    "Weak_Coherent",
    "Strong_Coherent",
]

REGIME_COLORS = {
    "Deep_Incoherent" : "#8B0000",   # dark red
    "Mod_Incoherent"  : "#FF6B6B",   # red
    "Transition"      : "#FFD700",   # gold
    "Weak_Coherent"   : "#90EE90",   # light green
    "Strong_Coherent" : "#006400",   # dark green
}

PLOTS_DIR = RESULTS_DIR / "plots"


def _pivot_metric(matrix_df: pd.DataFrame, metric: str,
                  min_trades: int = 10) -> pd.DataFrame:
    """Build strategy × regime pivot for a given metric."""
    sub = matrix_df[
        (matrix_df["regime"].isin(REGIMES_5)) &
        (matrix_df["trade_count"] >= min_trades)
    ].copy()
    if len(sub) == 0:
        return pd.DataFrame()
    pivot = sub.pivot_table(index="strategy", columns="regime",
                            values=metric, aggfunc="first")
    # Keep only columns in REGIMES_5
    cols = [c for c in REGIMES_5 if c in pivot.columns]
    pivot = pivot[cols]
    pivot = pivot.loc[pivot.mean(axis=1).sort_values(ascending=False).index]
    return pivot


def plot_heatmap_pf(matrix_df: pd.DataFrame, out_dir: Path):
    """Profit factor heatmap."""
    pivot = _pivot_metric(matrix_df, "profit_factor")
    if pivot.empty:
        return
    _plot_heatmap(pivot, "Profit Factor", "strategy_regime_heatmap.png",
                  out_dir, center=1.0, vmin=0.0, vmax=2.5)


def plot_heatmap_sharpe(matrix_df: pd.DataFrame, out_dir: Path):
    """Sharpe ratio heatmap."""
    pivot = _pivot_metric(matrix_df, "sharpe")
    if pivot.empty:
        return
    _plot_heatmap(pivot, "Sharpe Ratio", "strategy_regime_heatmap_sharpe.png",
                  out_dir, center=0.0, vmin=-3.0, vmax=3.0)


def _plot_heatmap(pivot: pd.DataFrame, title: str, filename: str,
                  out_dir: Path, center: float, vmin: float, vmax: float):
    n_strats = len(pivot)
    fig_h = max(6, n_strats * 0.38)
    fig, ax = plt.subplots(figsize=(12, fig_h))

    # Short column labels
    col_labels = [c.replace("_", "\n") for c in pivot.columns]

    if HAS_SEABORN:
        sns.heatmap(
            pivot, ax=ax, annot=True, fmt=".2f",
            cmap=sns.diverging_palette(10, 130, as_cmap=True),
            center=center, vmin=vmin, vmax=vmax,
            linewidths=0.5, linecolor="white",
            cbar_kws={"label": title, "shrink": 0.8},
            xticklabels=col_labels,
        )
    else:
        im = ax.imshow(pivot.values, aspect="auto", cmap="RdYlGn",
                       vmin=vmin, vmax=vmax)
        ax.set_xticks(range(len(pivot.columns)))
        ax.set_xticklabels(col_labels, rotation=30, ha="right")
        ax.set_yticks(range(len(pivot.index)))
        ax.set_yticklabels(pivot.index)
        for i in range(pivot.shape[0]):
            for j in range(pivot.shape[1]):
                v = pivot.iloc[i, j]
                if not np.isnan(v):
                    ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=8)
        plt.colorbar(im, ax=ax, label=title, shrink=0.8)

    ax.set_title(
        f"Strategy × Transport Regime — {title}\n"
        f"(Incoherent ← → Coherent)", fontsize=13, fontweight="bold"
    )
    ax.set_xlabel("Transport Regime", fontsize=11)
    ax.set_ylabel("Strategy", fontsize=11)
    plt.tight_layout()
    fig.savefig(out_dir / filename, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {filename}")


def plot_regime_markov(markov_df: pd.DataFrame, out_dir: Path):
    """Visualise the 5×5 Markov transition matrix."""
    if markov_df is None or len(markov_df) == 0:
        return
    # Extract numeric block
    row_labels = [r.replace("from_", "").replace("_", "\n") for r in markov_df.index]
    col_labels = [c.replace("to_", "").replace("_", "\n") for c in markov_df.columns]
    data = markov_df.values.astype(float)

    fig, ax = plt.subplots(figsize=(8, 7))
    if HAS_SEABORN:
        sns.heatmap(data, ax=ax, annot=True, fmt=".3f",
                    cmap="Blues", vmin=0, vmax=1,
                    xticklabels=col_labels, yticklabels=row_labels,
                    linewidths=0.5)
    else:
        im = ax.imshow(data, cmap="Blues", vmin=0, vmax=1)
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                ax.text(j, i, f"{data[i,j]:.3f}", ha="center", va="center", fontsize=8)
        ax.set_xticks(range(len(col_labels))); ax.set_xticklabels(col_labels, rotation=30, ha="right")
        ax.set_yticks(range(len(row_labels))); ax.set_yticklabels(row_labels)
        plt.colorbar(im, ax=ax)

    ax.set_title("5-Level Regime Markov Transition Matrix\n"
                 "(P(row → col) per bar)", fontsize=13, fontweight="bold")
    ax.set_xlabel("To Regime")
    ax.set_ylabel("From Regime")
    plt.tight_layout()
    fig.savefig(out_dir / "regime_markov.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  Saved: regime_markov.png")


def plot_regime_durations(stab_df: pd.DataFrame, out_dir: Path):
    """Bar chart of regime time fractions and mean duration."""
    if stab_df is None or len(stab_df) == 0:
        return

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # Plot 1: time fractions
    ax = axes[0]
    regimes = stab_df["regime"].tolist()
    fracs   = stab_df["time_fraction"].values
    colors  = [REGIME_COLORS.get(r, "#888") for r in regimes]
    bars    = ax.barh(regimes, fracs, color=colors, edgecolor="white")
    for bar, val in zip(bars, fracs):
        ax.text(val + 0.005, bar.get_y() + bar.get_height() / 2,
                f"{val:.3f}", va="center", fontsize=9)
    ax.set_xlim(0, max(fracs) * 1.2)
    ax.set_xlabel("Time Fraction")
    ax.set_title("Regime Time Fractions", fontweight="bold")
    ax.invert_yaxis()

    # Plot 2: mean duration in minutes
    ax = axes[1]
    mean_min = stab_df["mean_minutes"].values
    bars2    = ax.barh(regimes, mean_min, color=colors, edgecolor="white")
    for bar, val in zip(bars2, mean_min):
        ax.text(val + 0.5, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}", va="center", fontsize=9)
    ax.set_xlabel("Mean Duration (minutes)")
    ax.set_title("Mean Regime Duration", fontweight="bold")
    ax.invert_yaxis()

    fig.suptitle("Transport Regime Statistics — EUR/USD 2023–2025",
                 fontsize=13, fontweight="bold")
    plt.tight_layout()
    fig.savefig(out_dir / "regime_durations.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  Saved: regime_durations.png")


def plot_q_distribution(out_dir: Path):
    """Histogram of Q values coloured by regime."""
    q_path = q_series_path()
    if not q_path.exists():
        return
    q_df = pd.read_parquet(q_path)
    Q    = q_df["Q"].dropna().values

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Full distribution
    ax = axes[0]
    ax.hist(Q, bins=200, color="#4488FF", alpha=0.7, edgecolor="none")
    ax.axvline(0, color="red", lw=2, label="Q=0 (transition)")
    ax.axvline(float(np.percentile(Q, 5)),  color="#8B0000", lw=1.5, ls="--", label="Q5% (Deep_Inc)")
    ax.axvline(float(np.percentile(Q, 95)), color="#006400", lw=1.5, ls="--", label="Q95% (Strong_Coh)")
    ax.set_xlabel("Q")
    ax.set_ylabel("Frequency")
    ax.set_title("Q Distribution (full dataset)")
    ax.legend(fontsize=8)

    # Log-scale
    ax = axes[1]
    ax.hist(Q, bins=200, color="#4488FF", alpha=0.7, edgecolor="none", log=True)
    ax.axvline(0, color="red", lw=2)
    ax.set_xlabel("Q")
    ax.set_ylabel("log(Frequency)")
    ax.set_title("Q Distribution (log scale)")
    ax.set_yscale("log")

    fig.suptitle("Transport Q Distribution — EUR/USD 2023–2025",
                 fontsize=13, fontweight="bold")
    plt.tight_layout()
    fig.savefig(out_dir / "regime_q_distribution.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  Saved: regime_q_distribution.png")
    del q_df
    import gc; gc.collect()


def run_visualizations(manifest: dict, verbose: bool = True):
    """Run all visualizations."""
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    matrix_path = RESULTS_DIR / "phase1_strategy_matrix.csv"
    markov_path = RESULTS_DIR / "markov_matrix.csv"
    stab_path   = RESULTS_DIR / "regime_transition_statistics.csv"

    if matrix_path.exists():
        matrix_df = pd.read_csv(matrix_path)
        if verbose:
            print("  Plotting heatmaps …", flush=True)
        plot_heatmap_pf(matrix_df, PLOTS_DIR)
        plot_heatmap_sharpe(matrix_df, PLOTS_DIR)
    else:
        if verbose:
            print("  WARNING: matrix CSV not found, skipping heatmaps", flush=True)

    if markov_path.exists():
        markov_df = pd.read_csv(markov_path, index_col=0)
        if verbose:
            print("  Plotting Markov matrix …", flush=True)
        plot_regime_markov(markov_df, PLOTS_DIR)

    if stab_path.exists():
        stab_df = pd.read_csv(stab_path)
        if verbose:
            print("  Plotting regime durations …", flush=True)
        plot_regime_durations(stab_df, PLOTS_DIR)

    if verbose:
        print("  Plotting Q distribution …", flush=True)
    plot_q_distribution(PLOTS_DIR)

    mark_heatmap_complete(manifest)
    if verbose:
        print("  Visualizations complete.", flush=True)
