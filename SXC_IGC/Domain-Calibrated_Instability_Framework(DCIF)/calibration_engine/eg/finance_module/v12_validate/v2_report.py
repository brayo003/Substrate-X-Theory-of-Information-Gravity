"""v2_report.py — V2 plots, CSV outputs, and markdown reports."""
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


def _save(fig, path):
    fig.savefig(path, dpi=110, bbox_inches='tight')
    plt.close(fig)


def ensure_dirs(base: Path):
    p = base / "results" / "plots"
    p.mkdir(parents=True, exist_ok=True)
    return base / "results"


# ── Phase I plots ─────────────────────────────────────────────────────────

def plot_regime_durations(run_stats: pd.DataFrame, out: Path):
    if not HAS_MPL or run_stats is None or len(run_stats) == 0:
        return
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, reg in zip(axes, ['COHERENT', 'INCOHERENT']):
        row = run_stats[run_stats['regime'] == reg]
        if len(row) == 0:
            continue
        ax.bar(['mean', 'median', 'p25', 'p75'],
               [row['mean_bars'].values[0], row['median_bars'].values[0],
                row['p25_bars'].values[0],  row['p75_bars'].values[0]],
               color='green' if reg == 'COHERENT' else 'red', alpha=0.7)
        ax.set_title(f'{reg} run durations (bars)')
        ax.set_ylabel('Bars')
    fig.suptitle('Phase I — Regime Persistence')
    _save(fig, out / 'plots' / 'phase1_regime_durations.png')


def plot_markov(markov: pd.DataFrame, out: Path):
    if not HAS_MPL or markov is None or len(markov) == 0:
        return
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(markov.values, cmap='RdYlGn', vmin=0, vmax=1)
    ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
    ax.set_xticklabels(['to INCOHERENT', 'to COHERENT'])
    ax.set_yticklabels(['from INCOHERENT', 'from COHERENT'])
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f'{markov.values[i,j]:.3f}', ha='center', va='center',
                    fontsize=14, fontweight='bold')
    plt.colorbar(im, ax=ax)
    ax.set_title('Phase I — Markov Transition Matrix')
    _save(fig, out / 'plots' / 'phase1_markov.png')


# ── Phase II plots ────────────────────────────────────────────────────────

def plot_volatility_event_profile(event_profiles: pd.DataFrame, out: Path):
    if not HAS_MPL or event_profiles is None or len(event_profiles) == 0:
        return
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    ax = axes[0]
    ax.plot(event_profiles['lag'], event_profiles['mean_atr_norm'],
            color='steelblue', lw=2)
    ax.axvline(0, color='red', lw=1.5, ls='--', label='Q transition')
    ax.axhline(1.0, color='gray', lw=0.8, ls=':')
    ax.fill_between(event_profiles['lag'], event_profiles['mean_atr_norm'],
                    1.0, where=event_profiles['lag'] >= 0, alpha=0.2, color='orange')
    ax.set_xlabel('Lag (bars)'); ax.set_ylabel('Normalized ATR')
    ax.set_title('Phase II — ATR around INCOH→COH transition')
    ax.legend()
    ax = axes[1]
    ax.plot(event_profiles['lag'], event_profiles['mean_rv20'],
            color='darkorange', lw=2, label='RV-20')
    ax.plot(event_profiles['lag'], event_profiles['mean_rv5'],
            color='tomato',     lw=1.5, ls='--', label='RV-5')
    ax.axvline(0, color='red', lw=1.5, ls='--')
    ax.set_xlabel('Lag (bars)'); ax.set_ylabel('Realized vol')
    ax.set_title('Phase II — Realized Vol around Q transition')
    ax.legend()
    fig.suptitle('Phase II — Volatility Cluster Origin')
    _save(fig, out / 'plots' / 'phase2_vol_event_profile.png')


# ── Phase III plots ───────────────────────────────────────────────────────

def plot_lead_lag_comparison(lead_lag_df: pd.DataFrame, out: Path):
    if not HAS_MPL or lead_lag_df is None or len(lead_lag_df) == 0:
        return
    sub = lead_lag_df.dropna(subset=['mean_lead_bars'])
    if len(sub) == 0:
        return
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = ['green' if v > 0 else 'red' for v in sub['mean_lead_bars']]
    ax.barh(sub['indicator'], sub['mean_lead_bars'], color=colors, alpha=0.8)
    ax.axvline(0, color='black', lw=1.2)
    ax.set_xlabel('Mean lead (bars); positive = Q leads indicator')
    ax.set_title('Phase III — Q Lead/Lag vs Existing Indicators')
    _save(fig, out / 'plots' / 'phase3_lead_lag.png')


# ── Phase IV plots ────────────────────────────────────────────────────────

def plot_strategy_regime_matrix(matrix: pd.DataFrame, out: Path):
    if not HAS_MPL or matrix is None or len(matrix) == 0:
        return
    strats  = matrix['strategy'].unique()
    regimes = ['COHERENT', 'INCOHERENT']
    pf_data = np.full((len(strats), 2), np.nan)
    for i, s in enumerate(strats):
        for j, r in enumerate(regimes):
            row = matrix[(matrix['strategy'] == s) & (matrix['regime'] == r)]
            if len(row) > 0:
                pf_data[i, j] = row['profit_factor'].values[0]
    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(strats)); w = 0.35
    ax.bar(x - w/2, pf_data[:, 0], w, label='COHERENT',   color='green',   alpha=0.8)
    ax.bar(x + w/2, pf_data[:, 1], w, label='INCOHERENT', color='tomato',  alpha=0.8)
    ax.axhline(1.0, color='gray', lw=0.8, ls='--')
    ax.set_xticks(x); ax.set_xticklabels(strats, rotation=15)
    ax.set_ylabel('Profit Factor'); ax.legend()
    ax.set_title('Phase IV — Profit Factor by Strategy × Regime')
    _save(fig, out / 'plots' / 'phase4_strategy_matrix.png')


# ── Phase V plots ─────────────────────────────────────────────────────────

def plot_sizing_comparison(comparison: pd.DataFrame, out: Path):
    if not HAS_MPL or comparison is None or len(comparison) == 0:
        return
    cols = ['pf', 'sharpe', 'total_ret', 'max_dd']
    cols = [c for c in cols if c in comparison.columns]
    if len(cols) == 0:
        return
    fig, axes = plt.subplots(1, len(cols), figsize=(4*len(cols), 5))
    if len(cols) == 1:
        axes = [axes]
    for ax, col in zip(axes, cols):
        vals   = comparison[col].values
        labels = comparison['label'].values
        colors = ['steelblue', 'green']
        ax.bar(labels, vals, color=colors[:len(vals)], alpha=0.8)
        ax.set_title(col); ax.set_ylabel(col)
    fig.suptitle('Phase V — Position Sizing Comparison')
    _save(fig, out / 'plots' / 'phase5_sizing.png')


# ── Phase VIII plots ──────────────────────────────────────────────────────

def plot_microstructure(micro_df: pd.DataFrame, out: Path):
    if not HAS_MPL or micro_df is None or len(micro_df) == 0:
        return
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=False)
    for ax, kind, title in zip(axes,
        ['INCOH_COH', 'COH_INCOH'],
        ['INCOH→COH: Spread', 'COH→INCOH: Spread']):
        sub = micro_df[micro_df['type'] == kind]
        if len(sub) == 0:
            continue
        ax.plot(sub['lag'], sub['mean_spread'], lw=2, color='steelblue')
        ax.axvline(0, color='red', lw=1.5, ls='--', label='Transition')
        ax.set_xlabel('Lag (bars)'); ax.set_ylabel('Mean Spread (pips)')
        ax.set_title(f'Phase VIII — {title}')
        ax.legend()
    _save(fig, out / 'plots' / 'phase8_microstructure.png')


# ── Phase X table plot ────────────────────────────────────────────────────

def plot_capability_table(cap_table: pd.DataFrame, verdict: str,
                           verdict_text: str, out: Path):
    if not HAS_MPL or cap_table is None or len(cap_table) == 0:
        return
    rating_map = {'None': 0, 'Weak': 1, 'Moderate': 2, 'Strong': 3, 'Very Strong': 4}
    scores = cap_table['rating'].map(rating_map).values
    colors = ['#d73027','#fc8d59','#fee08b','#91cf60','#1a9850']
    row_colors = [colors[min(s, 4)] for s in scores]
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.axis('off')
    tbl_data = cap_table[['capability', 'rating', 'effect_size', 'ci_low', 'ci_high']].copy()
    tbl_data['effect_size'] = tbl_data['effect_size'].apply(
        lambda x: f'{x:.4f}' if not np.isnan(x) else 'n/a')
    tbl_data['ci_low']  = tbl_data['ci_low'].apply(
        lambda x: f'{x:.4f}' if not np.isnan(x) else 'n/a')
    tbl_data['ci_high'] = tbl_data['ci_high'].apply(
        lambda x: f'{x:.4f}' if not np.isnan(x) else 'n/a')
    t = ax.table(cellText=tbl_data.values, colLabels=tbl_data.columns,
                 loc='center', cellLoc='center')
    t.auto_set_font_size(False); t.set_fontsize(10)
    for i, rc in enumerate(row_colors):
        for j in range(len(tbl_data.columns)):
            t[i+1, j].set_facecolor(rc + '55')
    ax.set_title(f'Phase X — Practical Value  |  Verdict {verdict}: {verdict_text}',
                 fontsize=11, pad=20)
    _save(fig, out / 'plots' / 'phase10_capability_table.png')


# ── CSV writers ───────────────────────────────────────────────────────────

def save_all_csvs(results: dict, out: Path):
    csv_map = {
        'regime_run_stats.csv'        : results.get('p1_run_stats'),
        'markov_matrix.csv'           : results.get('p1_markov'),
        'regime_transition_events.csv': results.get('p1_transitions'),
        'volatility_event_profiles.csv': results.get('p2_profiles'),
        'lead_lag_comparison.csv'     : results.get('p3_lead_lag'),
        'detection_comparison.csv'    : results.get('p3_detection'),
        'strategy_regime_matrix.csv'  : results.get('p4_matrix'),
        'strategy_summary.csv'        : results.get('p4_summary'),
        'sizing_comparison.csv'       : results.get('p5_comparison'),
        'sizing_buckets.csv'          : results.get('p5_buckets'),
        'risk_management_matrix.csv'  : results.get('p6_rm_summary'),
        'execution_matrix.csv'        : results.get('p7_exec'),
        'microstructure_profiles.csv' : results.get('p8_micro'),
        'explainability_reports.csv'  : results.get('p9_explain'),
        'capability_table.csv'        : results.get('p10_table'),
    }
    for fname, df in csv_map.items():
        if df is None or (hasattr(df, '__len__') and len(df) == 0):
            continue
        if isinstance(df, pd.DataFrame):
            df.to_csv(out / fname, index=False)


# ── Markdown report builders ──────────────────────────────────────────────

def build_v2_report(results: dict, out: Path) -> str:
    p1   = results.get('p1_persistence', {})
    p2s  = results.get('p2_summary', {})
    p3l  = results.get('p3_lead_lag')
    p4s  = results.get('p4_summary')
    p5c  = results.get('p5_comparison')
    p6s  = results.get('p6_rm_summary')
    p7   = results.get('p7_exec_dict', {})
    p8s  = results.get('p8_micro_summary', {})
    p10  = results.get('p10_result', {})
    cap  = results.get('p10_table')
    verdict = p10.get('verdict', '?')
    vtext   = p10.get('verdict_text', '')

    lines = [
        "# SXC-IGC Transport Regime Validation V2",
        "",
        "## Phase I — Regime Persistence",
        "",
        f"- P(stay COHERENT)   = **{p1.get('P_stay_coherent', float('nan')):.3f}**",
        f"- P(stay INCOHERENT) = **{p1.get('P_stay_incoherent', float('nan')):.3f}**",
        f"- Mean COHERENT run  = **{p1.get('coherent_mean_bars', float('nan')):.1f} bars "
        f"({p1.get('coherent_mean_bars', 0)*5:.0f} min)**",
        f"- Mean INCOHERENT run= **{p1.get('incoherent_mean_bars', float('nan')):.1f} bars**",
        f"- Verdict: **{p1.get('verdict', '?')}**",
        "",
        "---", "", "## Phase II — Volatility Cluster Origin", "",
        f"- N transition events = {p2s.get('n_events', 0)}",
        f"- Pre-event ATR (norm) = {p2s.get('pre_mean_atr_norm', float('nan')):.3f}",
        f"- Post-event ATR (norm)= {p2s.get('post_mean_atr_norm', float('nan')):.3f}",
        f"- Vol expansion ratio  = **{p2s.get('vol_expansion_ratio', float('nan')):.3f}**",
        f"- MW p-value           = {p2s.get('mw_p', float('nan')):.4f}",
        f"- Statistically significant: {p2s.get('vol_expansion_significant', False)}",
        "",
        "---", "", "## Phase III — Lead/Lag vs Existing Indicators", "",
    ]
    if p3l is not None and len(p3l) > 0:
        lines.append(p3l.to_markdown(index=False))
    lines += ["", "---", "", "## Phase IV — Strategy Suitability Matrix", ""]
    if p4s is not None and len(p4s) > 0:
        lines.append(p4s.to_markdown(index=False))
    lines += ["", "---", "", "## Phase V — Position Sizing", ""]
    if p5c is not None and len(p5c) > 0:
        lines.append(p5c.to_markdown(index=False))
    lines += ["", "---", "", "## Phase VI — Risk Management", ""]
    if p6s is not None and len(p6s) > 0:
        lines.append(p6s.to_markdown(index=False))
    lines += [
        "", "---", "", "## Phase VII — Execution Quality", "",
        f"- MW spread p-value (COHERENT vs INCOHERENT): "
        f"{p7.get('mw_spread_p', float('nan')):.4f}",
    ]
    if 'exec_df' in p7 and p7['exec_df'] is not None and len(p7['exec_df']) > 0:
        lines.append(p7['exec_df'].to_markdown(index=False))
    lines += [
        "", "---", "", "## Phase VIII — Microstructure", "",
        f"- N transitions: {p8s.get('n_transitions', 0)}",
        f"- INCOH→COH spread ratio (post/pre): {p8s.get('INCOH_COH_spread_ratio', float('nan')):.3f}",
        f"- COH→INCOH spread ratio (post/pre): {p8s.get('COH_INCOH_spread_ratio', float('nan')):.3f}",
        "", "---", "", "## Phase IX — Explainability",
        "", "See explainability_reports.csv for per-transition human-readable reports.",
        "", "---", "", "## Phase X — Practical Value Assessment", "",
    ]
    if cap is not None and len(cap) > 0:
        lines.append(cap[['capability','rating','effect_size','evidence']].to_markdown(index=False))
    lines += [
        "", f"**Average score: {p10.get('avg_score', float('nan')):.2f} / 4.0**",
        "", f"## Final Scientific Conclusion",
        "", f"**Verdict {verdict}: {vtext}**",
        "",
        "### Supporting evidence:",
        f"- Regime persistence: P(stay coherent) = {p1.get('P_stay_coherent', float('nan')):.3f}",
        f"- Volatility prediction: expansion ratio = {p2s.get('vol_expansion_ratio', float('nan')):.3f}",
        f"- Strategy differentiation: mean PF diff = "
        + (f"{p4s['pf_difference'].mean():.3f}" if p4s is not None and 'pf_difference' in p4s.columns and len(p4s) > 0 else "n/a"),
        f"- Execution: MW spread p = {p7.get('mw_spread_p', float('nan')):.4f}",
    ]

    text = "\n".join(lines)
    (out / "transport_regime_validation_v2.md").write_text(text)
    return text


def build_market_state_report(results: dict, out: Path) -> str:
    p1  = results.get('p1_persistence', {})
    p2s = results.get('p2_summary', {})
    p10 = results.get('p10_result', {})

    lines = [
        "# Market State Report — SXC-IGC Transport V2",
        "",
        "This report answers: **Is Q a market-state variable?**",
        "",
        "## Evidence Summary",
        "",
        f"| Property | Value | Implication |",
        f"|---|---|---|",
        f"| Regime persistence (P stay coherent) | {p1.get('P_stay_coherent', float('nan')):.3f} "
        f"| {'Persistent states → allocatable' if p1.get('P_stay_coherent', 0) > 0.7 else 'Transient → noisy'} |",
        f"| Vol expansion at Q transition | {p2s.get('vol_expansion_ratio', float('nan')):.3f}x "
        f"| {'Yes, vol follows Q' if p2s.get('vol_expansion_ratio', 1) > 1.05 else 'Weak'} |",
        f"| Final verdict | {p10.get('verdict', '?')} "
        f"| {p10.get('verdict_text', '')} |",
        "",
    ]
    text = "\n".join(lines)
    (out / "market_state_report.md").write_text(text)
    return text


def build_summary_dashboard(results: dict, df: pd.DataFrame, out: Path) -> str:
    p10 = results.get('p10_result', {})
    cap = results.get('p10_table', pd.DataFrame())
    p1  = results.get('p1_persistence', {})
    p2s = results.get('p2_summary', {})

    Q   = df['tr_Q'].dropna().values
    coh_frac = float((Q > 0).mean())

    lines = [
        "# SXC-IGC Summary Dashboard — Validation V2",
        "",
        f"Dataset: {len(df):,} bars  |  "
        f"{df.index.min().date()} → {df.index.max().date()}",
        "",
        "## Key Numbers",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| Coherent fraction | {coh_frac*100:.1f}% |",
        f"| P(stay coherent) | {p1.get('P_stay_coherent', float('nan')):.3f} |",
        f"| P(stay incoherent) | {p1.get('P_stay_incoherent', float('nan')):.3f} |",
        f"| Mean coherent run | {p1.get('coherent_mean_bars', float('nan')):.1f} bars |",
        f"| Vol expansion at transition | {p2s.get('vol_expansion_ratio', float('nan')):.3f}x |",
        f"| Vol expansion p-value | {p2s.get('mw_p', float('nan')):.4f} |",
        "",
        "## Capability Ratings",
        "",
    ]
    if len(cap) > 0:
        for _, row in cap.iterrows():
            lines.append(f"- **{row['capability']}**: {row['rating']}")
    lines += [
        "",
        f"## Final Verdict",
        "",
        f"**{p10.get('verdict', '?')}: {p10.get('verdict_text', '')}**",
        "",
        "## Output Files",
        "",
        "| File | Contents |",
        "|---|---|",
        "| transport_regime_validation_v2.md | Full 10-phase report |",
        "| market_state_report.md | Is Q a market-state variable? |",
        "| regime_transition_events.csv | Every Q regime episode |",
        "| volatility_event_profiles.csv | Vol profile around Q transitions |",
        "| lead_lag_comparison.csv | Q vs ADX/ATR/HV lead-lag |",
        "| strategy_regime_matrix.csv | 4 strategies × 2 regimes |",
        "| risk_management_matrix.csv | Stop/target results by Q bucket |",
        "| execution_matrix.csv | Spread/IAE by regime |",
        "| capability_table.csv | Ranked practical capabilities |",
        "| plots/ | All V2 plots |",
    ]
    text = "\n".join(lines)
    (out / "summary_dashboard.md").write_text(text)
    return text
