"""v2_phase9_10.py — Phase IX: Explainability | Phase X: Practical Value Assessment"""
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, bootstrap


# ── Phase IX — Per-transition explainability reports ─────────────────────

def phase9_explainability(df: pd.DataFrame, max_reports: int = 20) -> pd.DataFrame:
    """
    For every major Q transition (largest |Q| change), generate one
    human-readable report row including price, ATR, volume, gradient,
    reason for classification.
    """
    n   = len(df)
    Q   = df['tr_Q'].values
    s   = df['tr_s'].values         if 'tr_s'           in df.columns else np.full(n, np.nan)
    grd = df['tr_grad_ln_s'].values if 'tr_grad_ln_s'   in df.columns else np.full(n, np.nan)
    st  = df['tr_s_transport'].values if 'tr_s_transport' in df.columns else np.full(n, np.nan)
    atr = df['atr_14'].values       if 'atr_14'         in df.columns else np.full(n, np.nan)
    vol = df['vol_norm'].values      if 'vol_norm'        in df.columns else np.full(n, np.nan)

    # Find transitions and rank by |ΔQ|
    transitions = []
    for i in range(1, n):
        if Q[i] > 0 and Q[i-1] <= 0:
            transitions.append((i, 'INCOH→COH', abs(Q[i] - Q[i-1])))
        elif Q[i] < 0 and Q[i-1] >= 0:
            transitions.append((i, 'COH→INCOH', abs(Q[i] - Q[i-1])))

    # Sort by magnitude, take top max_reports
    transitions.sort(key=lambda x: -x[2])
    transitions = transitions[:max_reports]

    rows = []
    for idx, direction, delta_Q in transitions:
        q_val = float(Q[idx])
        g_val = float(grd[idx]) if np.isfinite(grd[idx]) else 0.0

        # Reason: Q = 4(cτ)²|∇lns|² - 1
        # Q > 0 when |∇lns| > 1/(2cτ) = 0.1  (for c=1, τ=5)
        threshold = 0.1
        if direction == 'INCOH→COH':
            reason = (f"|∇ln s| = {abs(g_val):.4f} exceeded threshold {threshold:.4f}; "
                      f"stress gradient accelerated → coherent transport engaged")
        else:
            reason = (f"|∇ln s| = {abs(g_val):.4f} fell below threshold {threshold:.4f}; "
                      f"stress gradient collapsed → overdamped diffusion resumed")

        rows.append({
            'timestamp'       : df.index[idx],
            'transition_type' : direction,
            'delta_Q'         : float(delta_Q),
            'Q_value'         : q_val,
            'Q_prev'          : float(Q[idx-1]),
            'price'           : float(df['close'].iloc[idx]),
            'atr'             : float(atr[idx]) if np.isfinite(atr[idx]) else np.nan,
            'vol_norm'        : float(vol[idx])  if np.isfinite(vol[idx])  else np.nan,
            's_field'         : float(s[idx])    if np.isfinite(s[idx])    else np.nan,
            's_transport'     : float(st[idx])   if np.isfinite(st[idx])   else np.nan,
            'grad_ln_s'       : g_val,
            'regime_after'    : 'COHERENT' if q_val > 0 else 'INCOHERENT',
            'xi_c_bars'       : float(df['tr_xi_c'].iloc[idx]) if 'tr_xi_c' in df.columns else 10.0,
            'reason'          : reason,
        })

    return pd.DataFrame(rows)


# ── Phase X — Practical Value Assessment ─────────────────────────────────

_CAPABILITIES = [
    'strategy_selection',
    'position_sizing',
    'risk_management',
    'execution',
    'volatility_forecasting',
    'trade_filtering',
    'portfolio_allocation',
]

_RATINGS = ['None', 'Weak', 'Moderate', 'Strong', 'Very Strong']


def _bootstrap_ci(data: np.ndarray, stat_fn, n_boot=1000, ci=0.95) -> tuple:
    """Bootstrap confidence interval for stat_fn applied to data."""
    data = data[np.isfinite(data)]
    if len(data) < 10:
        return (np.nan, np.nan)
    rng  = np.random.default_rng(42)
    boot = np.array([stat_fn(rng.choice(data, size=len(data), replace=True))
                     for _ in range(n_boot)])
    lo   = float(np.percentile(boot, (1 - ci) / 2 * 100))
    hi   = float(np.percentile(boot, (1 + ci) / 2 * 100))
    return lo, hi


def phase10_practical_value(
    phase1: dict,
    phase2: dict,
    phase3: dict,
    phase4: dict,
    phase5: dict,
    phase6: dict,
    phase7: dict,
    phase8: dict,
    all_trades: pd.DataFrame,
    df: pd.DataFrame,
) -> dict:
    """
    Synthesize all phase results into a ranked capability table with
    evidence-backed ratings and confidence intervals.
    """
    rows = []

    # ── strategy_selection ────────────────────────────────────────────────
    if 'summary' in phase4 and len(phase4['summary']) > 0:
        s4   = phase4['summary']
        diffs = s4['pf_difference'].values if 'pf_difference' in s4.columns else np.array([0])
        diffs = diffs[np.isfinite(diffs)]
        mean_diff = float(diffs.mean()) if len(diffs) > 0 else 0.
        ci = _bootstrap_ci(diffs, np.mean)
        # Strategy differentiation: if mean |PF diff| > 0.15 → Strong
        if abs(mean_diff) > 0.30:    rating = 'Strong'
        elif abs(mean_diff) > 0.15:  rating = 'Moderate'
        elif abs(mean_diff) > 0.05:  rating = 'Weak'
        else:                         rating = 'None'
        rows.append({'capability': 'strategy_selection', 'rating': rating,
                     'effect_size': float(mean_diff),
                     'ci_low': ci[0], 'ci_high': ci[1],
                     'evidence': f'Mean PF diff (coh-incoh) = {mean_diff:.3f} across 4 strategies',
                     'n_obs': len(diffs)})

    # ── position_sizing ───────────────────────────────────────────────────
    if 'comparison' in phase5 and len(phase5['comparison']) > 0:
        cmp   = phase5['comparison']
        flat  = cmp.loc[cmp['label'] == 'FLAT_100pct',  'pf']
        sized = cmp.loc[cmp['label'] == 'Q_SIZED',       'pf']
        if len(flat) > 0 and len(sized) > 0:
            diff = float(sized.values[0]) - float(flat.values[0])
        else:
            diff = 0.
        if len(all_trades) > 20:
            sized_rets = (all_trades['net_ret'] * all_trades['entry_Q'].apply(_q_size_fn)).values
            flat_rets  = all_trades['net_ret'].values
            ci = _bootstrap_ci(sized_rets - flat_rets[:len(sized_rets)], np.mean)
        else:
            ci = (np.nan, np.nan)
        if   diff > 0.20: rating = 'Strong'
        elif diff > 0.10: rating = 'Moderate'
        elif diff > 0.02: rating = 'Weak'
        else:              rating = 'None'
        rows.append({'capability': 'position_sizing', 'rating': rating,
                     'effect_size': diff,
                     'ci_low': ci[0], 'ci_high': ci[1],
                     'evidence': f'Q-sized PF - flat PF = {diff:.3f}',
                     'n_obs': len(all_trades)})

    # ── risk_management ───────────────────────────────────────────────────
    if 'rm_summary' in phase6 and len(phase6['rm_summary']) > 0:
        rm = phase6['rm_summary']
        high = rm.loc[rm['Q_bucket'] == 'high', 'pf']
        deep = rm.loc[rm['Q_bucket'] == 'deep', 'pf']
        if len(high) > 0 and len(deep) > 0:
            diff = float(high.values[0]) - float(deep.values[0])
        else:
            diff = 0.
        if   diff > 0.30: rating = 'Strong'
        elif diff > 0.15: rating = 'Moderate'
        elif diff > 0.05: rating = 'Weak'
        else:              rating = 'None'
        rows.append({'capability': 'risk_management', 'rating': rating,
                     'effect_size': diff,
                     'ci_low': np.nan, 'ci_high': np.nan,
                     'evidence': f'PF(high-Q) - PF(deep-Q) = {diff:.3f}',
                     'n_obs': len(phase6['rm_trades']) if 'rm_trades' in phase6 else 0})

    # ── execution ─────────────────────────────────────────────────────────
    mw_p = phase7.get('mw_spread_p', 1.0)
    if np.isnan(mw_p): mw_p = 1.0
    if   mw_p < 0.001: rating = 'Moderate'
    elif mw_p < 0.05:  rating = 'Weak'
    else:               rating = 'None'
    rows.append({'capability': 'execution', 'rating': rating,
                 'effect_size': 1.0 - mw_p,
                 'ci_low': np.nan, 'ci_high': np.nan,
                 'evidence': f'MW spread COHERENT vs INCOHERENT p={mw_p:.4f}',
                 'n_obs': phase7.get('exec_df', pd.DataFrame()).shape[0] if 'exec_df' in phase7 else 0})

    # ── volatility_forecasting ────────────────────────────────────────────
    p2 = phase2.get('summary', {})
    vol_ratio = p2.get('vol_expansion_ratio', 1.0)
    vol_p     = p2.get('mw_p', 1.0)
    n_ev      = p2.get('n_events', 0)
    if np.isnan(vol_p): vol_p = 1.0
    if vol_p < 0.05 and vol_ratio > 1.1:   rating = 'Strong'
    elif vol_p < 0.10 and vol_ratio > 1.05: rating = 'Moderate'
    elif vol_p < 0.20:                      rating = 'Weak'
    else:                                   rating = 'None'
    rows.append({'capability': 'volatility_forecasting', 'rating': rating,
                 'effect_size': float(vol_ratio - 1.0),
                 'ci_low': np.nan, 'ci_high': np.nan,
                 'evidence': f'Post/pre ATR ratio={vol_ratio:.3f}, MW p={vol_p:.4f}, n_events={n_ev}',
                 'n_obs': n_ev})

    # ── trade_filtering ───────────────────────────────────────────────────
    if len(all_trades) > 20:
        coh_r = all_trades.loc[all_trades['entry_regime']=='COHERENT',   'net_ret'].values
        inc_r = all_trades.loc[all_trades['entry_regime']=='INCOHERENT', 'net_ret'].values
        coh_r = coh_r[np.isfinite(coh_r)]; inc_r = inc_r[np.isfinite(inc_r)]
        if len(coh_r) > 5 and len(inc_r) > 5:
            diff = coh_r.mean() - inc_r.mean()
            ci   = _bootstrap_ci(np.concatenate([coh_r, -inc_r]), np.mean)
        else:
            diff = 0.; ci = (np.nan, np.nan)
    else:
        diff = 0.; ci = (np.nan, np.nan)
    if   diff > 0.001:  rating = 'Moderate'
    elif diff > 0.0005: rating = 'Weak'
    else:                rating = 'None'
    rows.append({'capability': 'trade_filtering', 'rating': rating,
                 'effect_size': float(diff),
                 'ci_low': ci[0], 'ci_high': ci[1],
                 'evidence': f'Mean ret COHERENT - INCOHERENT = {diff:.5f}',
                 'n_obs': len(all_trades)})

    # ── portfolio_allocation ──────────────────────────────────────────────
    p1   = phase1.get('persistence', {})
    stay = p1.get('P_stay_coherent', 0.)
    if stay > 0.85:    rating = 'Moderate'
    elif stay > 0.75:  rating = 'Weak'
    else:               rating = 'None'
    rows.append({'capability': 'portfolio_allocation', 'rating': rating,
                 'effect_size': float(stay),
                 'ci_low': np.nan, 'ci_high': np.nan,
                 'evidence': f'P(stay coherent) = {stay:.3f}; regime persistence enables regime-aware allocation',
                 'n_obs': p1.get('n_coherent', 0)})

    table = pd.DataFrame(rows)

    # ── Final verdict ─────────────────────────────────────────────────────
    rating_scores = {'None': 0, 'Weak': 1, 'Moderate': 2, 'Strong': 3, 'Very Strong': 4}
    avg_score = table['rating'].map(rating_scores).mean()
    if avg_score >= 2.5:   verdict = 'C'  # market-state variable for risk management
    elif avg_score >= 1.5: verdict = 'B'  # useful volatility predictor
    elif avg_score >= 0.5: verdict = 'A'  # another technical indicator
    else:                   verdict = 'E'  # no advantage

    verdict_map = {
        'A': 'Q is only another technical indicator.',
        'B': 'Q is a useful volatility predictor.',
        'C': 'Q is a market-state variable suitable for risk management.',
        'D': 'Q is a strategy-allocation engine.',
        'E': 'Q provides no measurable advantage.',
    }

    return {
        'capability_table': table,
        'avg_score':        float(avg_score),
        'verdict':          verdict,
        'verdict_text':     verdict_map[verdict],
    }


def _q_size_fn(q):
    if q <= -0.5:  return 0.25
    elif q <= 0.0: return 0.50
    elif q <= 1.0: return 1.00
    else:          return 1.50
