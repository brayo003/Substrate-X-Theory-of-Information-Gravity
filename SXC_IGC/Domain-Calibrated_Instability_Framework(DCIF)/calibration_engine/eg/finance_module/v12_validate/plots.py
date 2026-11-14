"""
plots.py — Visualisation for V12 validation report.

All figures saved to an output directory.
Non-interactive backend (Agg) is used so this runs headlessly.
"""

import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path


FIREWALL_COLOR = '#d62728'
NOMINAL_COLOR  = '#2ca02c'
T_COLOR        = '#1f77b4'
FIG_DPI        = 120


def _shade_phases(ax, v12: pd.DataFrame):
    """Shade FIREWALL periods in red on ax."""
    phase = v12['phase']
    in_fw = False
    start = None
    for ts, p in phase.items():
        if p == 'FIREWALL' and not in_fw:
            start = ts
            in_fw = True
        elif p != 'FIREWALL' and in_fw:
            ax.axvspan(start, ts, alpha=0.18, color=FIREWALL_COLOR, lw=0)
            in_fw = False
    if in_fw and start is not None:
        ax.axvspan(start, phase.index[-1], alpha=0.18, color=FIREWALL_COLOR, lw=0)


def fig_tension_history(v12: pd.DataFrame, out_dir: Path):
    """T_sys over full history with FIREWALL shading."""
    fig, ax = plt.subplots(figsize=(16, 4))
    ax.plot(v12.index, v12['T_sys'], color=T_COLOR, lw=0.6, label='T_sys')
    ax.axhline(1.0, color=FIREWALL_COLOR, lw=0.8, ls='--', label='FIREWALL threshold')
    ax.axhline(0.4, color=NOMINAL_COLOR,  lw=0.8, ls='--', label='NOMINAL restore')
    _shade_phases(ax, v12)
    ax.set_ylabel('T_sys')
    ax.set_title('V12 Tension — Full History')
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / 'fig_tension_history.png', dpi=FIG_DPI)
    plt.close(fig)


def fig_vol_vs_tension(merged: pd.DataFrame, out_dir: Path):
    """Scatter of T_sys vs realized_vol, coloured by phase."""
    fig, ax = plt.subplots(figsize=(7, 5))
    for phase, color, label in [('FIREWALL', FIREWALL_COLOR, 'FIREWALL'),
                                  ('NOMINAL',  NOMINAL_COLOR,  'NOMINAL')]:
        sub = merged[merged['phase'] == phase]
        ax.scatter(sub['T_sys'], sub['realized_vol'],
                   c=color, alpha=0.15, s=3, label=label, rasterized=True)
    ax.set_xlabel('T_sys')
    ax.set_ylabel('Realized Volatility')
    ax.set_title('Tension vs Realized Volatility')
    ax.legend(markerscale=5, fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / 'fig_vol_vs_tension.png', dpi=FIG_DPI)
    plt.close(fig)


def fig_phase_overlay(v12: pd.DataFrame, ohlc: pd.DataFrame, out_dir: Path,
                      max_bars: int = 2000):
    """Close price with FIREWALL/NOMINAL overlay."""
    v12_sub  = v12.iloc[-max_bars:]
    ohlc_sub = ohlc.reindex(v12_sub.index)
    fig, ax  = plt.subplots(figsize=(16, 4))
    ax.plot(ohlc_sub.index, ohlc_sub['close'], color='#333333', lw=0.6)
    _shade_phases(ax, v12_sub)
    fw_patch = mpatches.Patch(color=FIREWALL_COLOR, alpha=0.4, label='FIREWALL')
    ax.legend(handles=[fw_patch], fontsize=8)
    ax.set_ylabel('EUR/USD')
    ax.set_title(f'EUR/USD Close — last {max_bars} bars with FIREWALL overlay')
    fig.tight_layout()
    fig.savefig(out_dir / 'fig_phase_overlay.png', dpi=FIG_DPI)
    plt.close(fig)


def fig_phase_durations(transitions: pd.DataFrame, out_dir: Path):
    """Histograms of FIREWALL and NOMINAL episode durations."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    for ax, phase, color in [(axes[0], 'FIREWALL', FIREWALL_COLOR),
                               (axes[1], 'NOMINAL',  NOMINAL_COLOR)]:
        sub = transitions[transitions['phase'] == phase]['duration_min']
        if sub.empty:
            continue
        ax.hist(sub, bins=50, color=color, edgecolor='none', alpha=0.8)
        ax.set_xlabel('Duration (minutes)')
        ax.set_ylabel('Count')
        ax.set_title(f'{phase} episode durations  (median={sub.median():.0f} min)')
    fig.tight_layout()
    fig.savefig(out_dir / 'fig_phase_durations.png', dpi=FIG_DPI)
    plt.close(fig)


def fig_boxplots_by_phase(merged: pd.DataFrame, label_cols: list, out_dir: Path):
    """Box plots comparing label distributions for FIREWALL vs NOMINAL."""
    n = len(label_cols)
    cols_per_row = 4
    rows = (n + cols_per_row - 1) // cols_per_row
    fig, axes = plt.subplots(rows, cols_per_row, figsize=(16, rows * 3))
    axes = axes.flatten()

    for i, col in enumerate(label_cols):
        ax = axes[i]
        data = [
            merged[merged['phase'] == 'FIREWALL'][col].dropna().values,
            merged[merged['phase'] == 'NOMINAL'][col].dropna().values,
        ]
        bp = ax.boxplot(data, labels=['FW', 'NM'], patch_artist=True,
                        showfliers=False, widths=0.5)
        for patch, color in zip(bp['boxes'], [FIREWALL_COLOR, NOMINAL_COLOR]):
            patch.set_facecolor(color)
            patch.set_alpha(0.6)
        ax.set_title(col, fontsize=9)

    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)
    fig.suptitle('Label distributions: FIREWALL vs NOMINAL', fontsize=11)
    fig.tight_layout()
    fig.savefig(out_dir / 'fig_boxplots_by_phase.png', dpi=FIG_DPI)
    plt.close(fig)


def fig_lead_lag(xcorr: pd.Series, out_dir: Path):
    """Lead/lag cross-correlation between T_sys and realized_vol."""
    fig, ax = plt.subplots(figsize=(9, 4))
    lags = xcorr.index.tolist()
    ax.bar(lags, xcorr.values, color=T_COLOR, alpha=0.7)
    ax.axvline(0, color='black', lw=0.8)
    ci = 2.0 / np.sqrt(len(lags) * 10)   # rough 95 % CI
    ax.axhline( ci, color='grey', lw=0.8, ls='--', label='±95 % CI (approx)')
    ax.axhline(-ci, color='grey', lw=0.8, ls='--')
    ax.set_xlabel('Lag (bars, positive = T_sys leads)')
    ax.set_ylabel('Cross-correlation')
    ax.set_title('Lead/Lag: T_sys vs Realized Volatility')
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / 'fig_lead_lag.png', dpi=FIG_DPI)
    plt.close(fig)


def fig_predictive_heatmap(pred_df: pd.DataFrame, out_dir: Path):
    """Heatmap of Spearman ρ between T_sys and forward labels."""
    rho_cols = [c for c in pred_df.columns if c.startswith('rho_k')]
    p_cols   = [c for c in pred_df.columns if c.startswith('p_k')]
    if not rho_cols:
        return
    rho_mat = pred_df.set_index('label')[rho_cols].astype(float)
    p_mat   = pred_df.set_index('label')[p_cols].astype(float)

    fig, ax = plt.subplots(figsize=(8, max(3, len(rho_mat) * 0.5 + 1)))
    cax = ax.imshow(rho_mat.values, aspect='auto', cmap='RdBu_r',
                    vmin=-0.4, vmax=0.4)
    plt.colorbar(cax, ax=ax, label='Spearman ρ')
    ax.set_xticks(range(len(rho_cols)))
    ax.set_xticklabels([c.replace('rho_', '') for c in rho_cols])
    ax.set_yticks(range(len(rho_mat)))
    ax.set_yticklabels(rho_mat.index.tolist(), fontsize=8)
    # asterisks for significance
    for r in range(len(rho_mat)):
        for c in range(len(rho_cols)):
            p = p_mat.values[r, c]
            if not np.isnan(p) and p < 0.05:
                ax.text(c, r, '*', ha='center', va='center', fontsize=8,
                        color='black' if abs(rho_mat.values[r, c]) < 0.25 else 'white')
    ax.set_title('Predictive Spearman ρ: T_sys(t) vs label(t+k)  (* p<0.05)')
    fig.tight_layout()
    fig.savefig(out_dir / 'fig_predictive_heatmap.png', dpi=FIG_DPI)
    plt.close(fig)


def fig_forward_ratios(fwd_df: pd.DataFrame, out_dir: Path):
    """Forward window ratios vs baseline for FIREWALL transitions."""
    if fwd_df.empty:
        return
    ratio_cols = [c for c in fwd_df.columns if c.endswith('_vs_nominal')]
    horizons   = sorted(fwd_df['horizon_min'].unique())

    fig, axes = plt.subplots(1, len(ratio_cols), figsize=(4 * len(ratio_cols), 4))
    if len(ratio_cols) == 1:
        axes = [axes]
    for ax, col in zip(axes, ratio_cols):
        means = [fwd_df[fwd_df['horizon_min'] == h][col].mean() for h in horizons]
        ax.bar(range(len(horizons)), means, color=FIREWALL_COLOR, alpha=0.7)
        ax.axhline(1.0, color='black', lw=0.8, ls='--', label='Nominal baseline')
        ax.set_xticks(range(len(horizons)))
        ax.set_xticklabels([f'{h}m' for h in horizons])
        ax.set_title(col.replace('mean_', '').replace('_vs_nominal', ''), fontsize=9)
        ax.set_ylabel('Ratio to NOMINAL baseline')
        ax.legend(fontsize=7)
    fig.suptitle('Post-FIREWALL forward window: ratio to NOMINAL baseline')
    fig.tight_layout()
    fig.savefig(out_dir / 'fig_forward_ratios.png', dpi=FIG_DPI)
    plt.close(fig)


def fig_stability_heatmap(stab_df: pd.DataFrame, group_col: str, out_dir: Path):
    """Heatmap of rank-biserial r by year or session."""
    if stab_df.empty:
        return
    pivot = stab_df.pivot(index='label', columns=group_col, values='rank_biserial_r')
    fig, ax = plt.subplots(figsize=(max(5, pivot.shape[1] * 1.5), max(3, pivot.shape[0] * 0.5 + 1)))
    cax = ax.imshow(pivot.values.astype(float), aspect='auto',
                    cmap='RdBu_r', vmin=-0.5, vmax=0.5)
    plt.colorbar(cax, ax=ax, label='Rank-biserial r')
    ax.set_xticks(range(pivot.shape[1]))
    ax.set_xticklabels(pivot.columns.tolist())
    ax.set_yticks(range(pivot.shape[0]))
    ax.set_yticklabels(pivot.index.tolist(), fontsize=8)
    ax.set_title(f'Stability of FIREWALL effect by {group_col}')
    fig.tight_layout()
    fig.savefig(out_dir / f'fig_stability_{group_col}.png', dpi=FIG_DPI)
    plt.close(fig)


def generate_all_figures(v12, ohlc, merged, transitions, xcorr,
                         pred_df, fwd_df, stab_year, stab_sess,
                         label_cols, out_dir: Path):
    """Render and save all figures."""
    out_dir.mkdir(parents=True, exist_ok=True)
    print("  Generating figures …")
    fig_tension_history(v12, out_dir)
    fig_vol_vs_tension(merged, out_dir)
    fig_phase_overlay(v12, ohlc, out_dir)
    fig_phase_durations(transitions, out_dir)
    fig_boxplots_by_phase(merged, label_cols, out_dir)
    fig_lead_lag(xcorr, out_dir)
    fig_predictive_heatmap(pred_df, out_dir)
    fig_forward_ratios(fwd_df, out_dir)
    fig_stability_heatmap(stab_year, 'year',    out_dir)
    fig_stability_heatmap(stab_sess, 'session', out_dir)
    print(f"  Figures saved to {out_dir}")
