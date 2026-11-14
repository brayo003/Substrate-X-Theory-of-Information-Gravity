"""
p5_visuals.py — Phase 5 Visualization Engine.

Generates all required plots for the 2026 out-of-sample validation:
  - Equity curves (per market, 2026)
  - PF comparison: 2025 vs 2026 (bar chart)
  - Q distribution comparison (2025 vs 2026 per market)
  - Regime occupancy comparison (side-by-side)
  - Drawdown curves (2026)
  - NoTrade% comparison (2025 vs 2026)
  - Scheduler/allocator comparison heatmap
  - Statistical test results (heatmap)
  - Transport drift index (per market)
"""

import sys
import warnings
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

_HERE = Path(__file__).resolve().parent
PHASE5_DIR = _HERE / "results" / "phase5"
PLOTS_DIR  = PHASE5_DIR / "plots"

REGIMES_5    = ["Deep_Incoherent", "Mod_Incoherent", "Transition", "Weak_Coherent", "Strong_Coherent"]
REGIME_SHORT = ["DI", "MI", "TR", "WC", "SC"]
MARKET_ORDER = ["EURUSD", "BTCUSDT", "ETHUSDT", "NAS100", "XAUUSD", "USOIL", "UKOIL"]
COLORS_MARKET = ["#2196F3", "#FF9800", "#9C27B0", "#4CAF50", "#F44336", "#795548", "#00BCD4"]
COLOR_2025 = "#546E7A"
COLOR_2026 = "#F57C00"


def _setup():
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def _get_mpl():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "figure.dpi": 130, "font.size": 9,
        "axes.titlesize": 10, "axes.labelsize": 9,
        "figure.facecolor": "white", "axes.facecolor": "#f8f9fa",
        "grid.alpha": 0.4, "grid.color": "#cccccc",
    })
    return plt


# ═══════════════════════════════════════════════════════════════════════════
# 1. Equity curves
# ═══════════════════════════════════════════════════════════════════════════

def plot_equity_curves(
    all_trade_logs: Dict[str, pd.DataFrame],
    all_bar_logs:   Dict[str, pd.DataFrame],
):
    plt = _get_mpl()
    fig, axes = plt.subplots(3, 3, figsize=(15, 10))
    axes = axes.flatten()

    for idx, sym in enumerate(MARKET_ORDER):
        ax = axes[idx]
        tl = all_trade_logs.get(sym)
        if tl is not None and len(tl) > 0 and "net_ret" in tl.columns:
            equity = tl["net_ret"].cumsum().values
            ax.plot(equity, color=COLORS_MARKET[idx], lw=1.5, label=sym)
            ax.axhline(0, color="black", lw=0.8, ls="--", alpha=0.6)
            # Shade drawdown
            peak = np.maximum.accumulate(equity)
            dd   = equity - peak
            ax.fill_between(range(len(equity)), equity, peak,
                            where=dd < 0, alpha=0.25, color="red")
            pf_str  = f"PF={_pf(tl['net_ret'].values):.2f}"
            ax.set_title(f"{sym} 2026 Equity  {pf_str}", fontsize=9)
        else:
            ax.set_title(f"{sym} — No trades", fontsize=9)
            ax.text(0.5, 0.5, "No Trades", ha="center", va="center",
                    transform=ax.transAxes, color="gray")
        ax.set_xlabel("Trade #")
        ax.set_ylabel("Cumulative Net Return")
        ax.grid(True)

    # Hide empty panel
    axes[-1].set_visible(False)
    fig.suptitle("Phase 5 — 2026 OOS Equity Curves (Frozen Transport OS)", fontsize=11, fontweight="bold")
    plt.tight_layout()
    _save(fig, "equity_curves_2026.png")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════
# 2. PF comparison 2025 vs 2026
# ═══════════════════════════════════════════════════════════════════════════

def plot_pf_comparison(
    stats_2025: Dict[str, Dict],
    stats_2026: Dict[str, Dict],
):
    plt = _get_mpl()
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    metrics = [
        ("profit_factor", "Profit Factor", 1.0),
        ("sharpe",        "Sharpe Ratio",  0.0),
        ("win_rate",      "Win Rate",       0.5),
    ]

    for ax, (m, label, ref_line) in zip(axes, metrics):
        v25 = [float(stats_2025.get(s, {}).get(m, 0.0)) for s in MARKET_ORDER]
        v26 = [float(stats_2026.get(s, {}).get(m, 0.0)) for s in MARKET_ORDER]

        x   = np.arange(len(MARKET_ORDER))
        w   = 0.35
        ax.bar(x - w/2, v25, w, label="2025 (P4)", color=COLOR_2025, alpha=0.85)
        ax.bar(x + w/2, v26, w, label="2026 (P5)", color=COLOR_2026, alpha=0.85)
        ax.axhline(ref_line, color="red", lw=1.0, ls="--", alpha=0.7, label=f"ref={ref_line}")
        ax.set_xticks(x)
        ax.set_xticklabels(MARKET_ORDER, rotation=30, ha="right")
        ax.set_title(label)
        ax.legend(fontsize=8)
        ax.grid(axis="y", alpha=0.4)

    fig.suptitle("Phase 5 — Performance Comparison: 2025 (P4) vs 2026 (P5 OOS)", fontweight="bold")
    plt.tight_layout()
    _save(fig, "pf_comparison_2025_vs_2026.png")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════
# 3. Q distributions
# ═══════════════════════════════════════════════════════════════════════════

def plot_q_distributions(
    all_data_2026: Dict[str, pd.DataFrame],
):
    plt = _get_mpl()
    cache_dir = _HERE / "cache"
    fig, axes = plt.subplots(3, 3, figsize=(15, 10))
    axes = axes.flatten()

    for idx, sym in enumerate(MARKET_ORDER):
        ax = axes[idx]

        # 2026
        df26 = all_data_2026.get(sym)
        q26  = df26["tr_Q"].dropna().values if df26 is not None and "tr_Q" in df26.columns else np.array([])

        # 2025
        if sym == "EURUSD":
            frames = [pd.read_parquet(fp)["tr_Q"].dropna()
                      for fp in sorted(cache_dir.glob("ohlc_transport_2025_*.parquet"))
                      if "tr_Q" in pd.read_parquet(fp).columns]
            q25 = pd.concat(frames).values if frames else np.array([])
        else:
            p3 = _HERE / "results" / "phase3" / f"prepared_{sym}.parquet"
            q25 = pd.read_parquet(p3)["tr_Q"].dropna().values if p3.exists() else np.array([])

        bins = np.linspace(-3, 5, 60)
        if len(q25) > 10:
            ax.hist(q25, bins=bins, density=True, alpha=0.55, color=COLOR_2025, label="2025")
        if len(q26) > 10:
            ax.hist(q26, bins=bins, density=True, alpha=0.55, color=COLOR_2026, label="2026")

        ax.axvline(0, color="green", lw=1.0, ls="--", alpha=0.8, label="Q=0")
        ax.axvline(-1.0,  color="blue",  lw=0.8, ls=":", alpha=0.7)
        ax.axvline(1.73,  color="red",   lw=0.8, ls=":", alpha=0.7)
        ax.set_title(f"{sym} Q Distribution", fontsize=9)
        ax.legend(fontsize=7)
        ax.set_xlabel("Q")

    axes[-1].set_visible(False)
    fig.suptitle("Phase 5 — Q Distribution: 2025 vs 2026 (vertical lines = frozen thresholds)", fontweight="bold")
    plt.tight_layout()
    _save(fig, "q_distributions_2025_vs_2026.png")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════
# 4. Regime occupancy comparison
# ═══════════════════════════════════════════════════════════════════════════

def plot_regime_comparison(
    all_data_2026: Dict[str, pd.DataFrame],
    regime_stability_df: Optional[pd.DataFrame] = None,
):
    plt = _get_mpl()
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    axes = axes.flatten()
    regime_colors = ["#D32F2F", "#FF7043", "#FFB300", "#66BB6A", "#1565C0"]

    cache_dir = _HERE / "cache"

    for idx, sym in enumerate(MARKET_ORDER):
        ax = axes[idx]
        df26 = all_data_2026.get(sym)
        occ26 = np.array([float((df26["regime"] == r).mean()) for r in REGIMES_5]) \
                if df26 is not None and "regime" in df26.columns else np.zeros(5)

        # 2025
        if sym == "EURUSD":
            frames = []
            for fp in sorted(cache_dir.glob("ohlc_transport_2025_*.parquet")):
                df = pd.read_parquet(fp)
                if "regime" in df.columns:
                    frames.append(df["regime"])
            reg25 = pd.concat(frames) if frames else pd.Series(dtype=str)
        else:
            p3 = _HERE / "results" / "phase3" / f"prepared_{sym}.parquet"
            reg25 = pd.read_parquet(p3)["regime"] if p3.exists() else pd.Series(dtype=str)

        occ25 = np.array([float((reg25 == r).mean()) for r in REGIMES_5]) if len(reg25) > 0 else np.zeros(5)

        x = np.arange(5)
        w = 0.35
        ax.bar(x - w/2, occ25, w, color=COLOR_2025, alpha=0.85, label="2025")
        ax.bar(x + w/2, occ26, w, color=COLOR_2026, alpha=0.85, label="2026")
        ax.set_xticks(x)
        ax.set_xticklabels(REGIME_SHORT, fontsize=8)
        ax.set_title(f"{sym}", fontsize=9)
        ax.legend(fontsize=7)
        ax.set_ylim(0, 1)
        ax.grid(axis="y", alpha=0.4)

    axes[-1].set_visible(False)
    fig.suptitle("Phase 5 — Regime Occupancy: 2025 vs 2026 (DI/MI/TR/WC/SC)", fontweight="bold")
    plt.tight_layout()
    _save(fig, "regime_comparison_2025_vs_2026.png")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════
# 5. Drawdown curves
# ═══════════════════════════════════════════════════════════════════════════

def plot_drawdown_curves(all_trade_logs: Dict[str, pd.DataFrame]):
    plt = _get_mpl()
    fig, ax = plt.subplots(figsize=(13, 5))

    for idx, sym in enumerate(MARKET_ORDER):
        tl = all_trade_logs.get(sym)
        if tl is None or len(tl) == 0:
            continue
        eq   = tl["net_ret"].cumsum().values
        peak = np.maximum.accumulate(eq)
        dd   = eq - peak
        ax.plot(dd, label=sym, color=COLORS_MARKET[idx], lw=1.2, alpha=0.85)

    ax.axhline(0, color="black", lw=0.8, ls="--")
    ax.set_title("Phase 5 — 2026 Drawdown Curves (all markets)", fontsize=10, fontweight="bold")
    ax.set_xlabel("Trade #")
    ax.set_ylabel("Drawdown (net return units)")
    ax.legend(fontsize=8)
    ax.grid(True)
    plt.tight_layout()
    _save(fig, "drawdown_curves_2026.png")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════
# 6. NoTrade% comparison
# ═══════════════════════════════════════════════════════════════════════════

def plot_notrade_comparison(
    stats_2025: Dict[str, Dict],
    stats_2026: Dict[str, Dict],
):
    plt = _get_mpl()
    fig, ax = plt.subplots(figsize=(10, 5))

    v25 = [float(stats_2025.get(s, {}).get("no_trade_pct", 0.0)) * 100 for s in MARKET_ORDER]
    v26 = [float(stats_2026.get(s, {}).get("no_trade_pct", 0.0)) * 100 for s in MARKET_ORDER]

    x = np.arange(len(MARKET_ORDER))
    w = 0.35
    ax.bar(x - w/2, v25, w, label="2025", color=COLOR_2025, alpha=0.85)
    ax.bar(x + w/2, v26, w, label="2026", color=COLOR_2026, alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(MARKET_ORDER)
    ax.set_ylabel("NoTrade %")
    ax.set_title("Phase 5 — NoTrade% Comparison: 2025 vs 2026", fontweight="bold")
    ax.legend()
    ax.grid(axis="y", alpha=0.4)
    plt.tight_layout()
    _save(fig, "notrade_comparison.png")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════
# 7. Scheduler / allocator heatmap
# ═══════════════════════════════════════════════════════════════════════════

def plot_scheduler_comparison(
    all_trade_logs_2026: Dict[str, pd.DataFrame],
):
    plt = _get_mpl()
    alloc_path = _HERE / "results" / "phase4" / "allocator_by_market.csv"
    if not alloc_path.exists():
        return
    alloc = pd.read_csv(alloc_path)

    family_map = {"NoTrade": 0, "Trend": 1, "MeanReversion": 2, "Momentum": 3,
                  "Scalping": 4, "Volatility": 5, "Session": 6, "PassiveLiquidity": 7}

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Frozen (expected) scheduler
    frozen = np.zeros((len(MARKET_ORDER), 5))
    for i, sym in enumerate(MARKET_ORDER):
        sub = alloc[alloc["symbol"] == sym]
        for j, regime in enumerate(REGIMES_5):
            row = sub[sub["regime"] == regime]
            if len(row) > 0:
                fam = row.iloc[0].get("best_family", "NoTrade")
                frozen[i, j] = family_map.get(str(fam), 0)

    # Observed (2026) scheduler
    observed = np.zeros((len(MARKET_ORDER), 5))
    for i, sym in enumerate(MARKET_ORDER):
        tl = all_trade_logs_2026.get(sym)
        if tl is None or len(tl) == 0:
            continue
        for j, regime in enumerate(REGIMES_5):
            sub = tl[tl["regime"] == regime] if "regime" in tl.columns else pd.DataFrame()
            if len(sub) > 0 and "family" in sub.columns:
                top = sub["family"].mode()
                fam = top.iloc[0] if len(top) > 0 else "NoTrade"
                observed[i, j] = family_map.get(str(fam), 0)

    for ax, data, title in [(axes[0], frozen, "Frozen Scheduler (P4)"),
                             (axes[1], observed, "Observed 2026 (P5)")]:
        im = ax.imshow(data, cmap="tab10", aspect="auto", vmin=0, vmax=7)
        ax.set_xticks(range(5))
        ax.set_xticklabels(REGIME_SHORT, fontsize=8)
        ax.set_yticks(range(len(MARKET_ORDER)))
        ax.set_yticklabels(MARKET_ORDER, fontsize=8)
        ax.set_title(title, fontsize=9)
        for i in range(len(MARKET_ORDER)):
            for j in range(5):
                rev = {v: k for k, v in family_map.items()}
                ax.text(j, i, rev.get(int(data[i, j]), "?")[:4],
                        ha="center", va="center", fontsize=7, color="white",
                        fontweight="bold")

    fig.suptitle("Phase 5 — Scheduler Comparison (frozen vs observed 2026)", fontweight="bold")
    plt.tight_layout()
    _save(fig, "scheduler_comparison.png")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════
# 8. Transport drift index bar chart
# ═══════════════════════════════════════════════════════════════════════════

def plot_transport_drift(transport_drift_df: Optional[pd.DataFrame]):
    if transport_drift_df is None or len(transport_drift_df) == 0:
        return
    plt = _get_mpl()
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    cols = ["tv_distance", "ks_stat"]
    labels = ["Total Variation Distance (Q)", "KS Statistic (Q)"]
    for ax, col, label in zip(axes, cols, labels):
        if col in transport_drift_df.columns:
            subs = transport_drift_df.set_index("symbol")[col].reindex(MARKET_ORDER).fillna(0)
            colors = ["#F44336" if v > 0.3 else "#FF9800" if v > 0.15 else "#4CAF50"
                      for v in subs.values]
            ax.bar(subs.index, subs.values, color=colors, alpha=0.85)
            ax.set_title(label, fontsize=9)
            ax.set_ylabel(col)
            ax.set_xticklabels(MARKET_ORDER, rotation=30, ha="right")
            ax.grid(axis="y", alpha=0.4)
            ax.axhline(0.2, color="orange", lw=1, ls="--", alpha=0.7, label="moderate threshold")
            ax.legend(fontsize=7)

    fig.suptitle("Phase 5 — Transport Layer Drift (Q distribution shift)", fontweight="bold")
    plt.tight_layout()
    _save(fig, "transport_drift_index.png")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════
# 9. Statistical test heatmap
# ═══════════════════════════════════════════════════════════════════════════

def plot_statistical_tests(stat_tests_df: Optional[pd.DataFrame]):
    if stat_tests_df is None or len(stat_tests_df) == 0:
        return
    plt = _get_mpl()
    fig, ax = plt.subplots(figsize=(10, 4))

    cols = ["mw_pval", "ks_pval", "ttest_pval", "wilcox_pval"]
    avail = [c for c in cols if c in stat_tests_df.columns]
    if not avail:
        plt.close(fig)
        return

    df = stat_tests_df.set_index("symbol").reindex(MARKET_ORDER)[avail].fillna(1.0)
    im = ax.imshow(df.values.T, aspect="auto", cmap="RdYlGn_r", vmin=0, vmax=0.1)
    ax.set_xticks(range(len(MARKET_ORDER)))
    ax.set_xticklabels(MARKET_ORDER, rotation=30, ha="right")
    ax.set_yticks(range(len(avail)))
    ax.set_yticklabels([c.replace("_pval", "") for c in avail])

    for i, sym in enumerate(MARKET_ORDER):
        for j, col in enumerate(avail):
            val = df.loc[sym, col] if sym in df.index else 1.0
            star = "**" if val < 0.01 else "*" if val < 0.05 else ""
            ax.text(i, j, f"{val:.3f}{star}", ha="center", va="center", fontsize=7)

    plt.colorbar(im, ax=ax, label="p-value")
    ax.set_title("Phase 5 — Statistical Tests: 2025 vs 2026 (p-values)", fontweight="bold")
    plt.tight_layout()
    _save(fig, "statistical_tests_heatmap.png")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════
# Master runner
# ═══════════════════════════════════════════════════════════════════════════

def _pf(rets):
    wins = rets[rets > 0]; losses = rets[rets < 0]
    w = wins.sum(); l = abs(losses.sum())
    return w / (l + 1e-12) if l > 0 else (99.0 if w > 0 else 0.0)


def _save(fig, name: str):
    out = PLOTS_DIR / name
    fig.savefig(out, bbox_inches="tight")


def run_all_visuals(
    all_data_2026:       Dict[str, pd.DataFrame],
    all_trade_logs:      Dict[str, pd.DataFrame],
    all_bar_logs:        Dict[str, pd.DataFrame],
    stats_2025:          Dict[str, Dict],
    stats_2026:          Dict[str, Dict],
    drift_results:       Dict[str, pd.DataFrame],
    verbose:             bool = True,
):
    _setup()

    def _try(fn, name, *args, **kwargs):
        try:
            fn(*args, **kwargs)
            if verbose:
                print(f"  [OK] {name}", flush=True)
        except Exception as e:
            if verbose:
                print(f"  [WARN] {name}: {e}", flush=True)

    _try(plot_equity_curves,      "equity_curves",        all_trade_logs, all_bar_logs)
    _try(plot_pf_comparison,      "pf_comparison",        stats_2025, stats_2026)
    _try(plot_q_distributions,    "q_distributions",      all_data_2026)
    _try(plot_regime_comparison,  "regime_comparison",    all_data_2026,
         drift_results.get("regime_stability"))
    _try(plot_drawdown_curves,    "drawdown_curves",      all_trade_logs)
    _try(plot_notrade_comparison, "notrade_comparison",   stats_2025, stats_2026)
    _try(plot_scheduler_comparison,"scheduler_comparison",all_trade_logs)
    _try(plot_transport_drift,    "transport_drift",      drift_results.get("transport_drift"))
    _try(plot_statistical_tests,  "statistical_tests",    drift_results.get("statistical_tests"))

    if verbose:
        print(f"  Plots saved to {PLOTS_DIR}", flush=True)
