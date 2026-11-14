"""
transport_signal_eval.py
========================
Controlled evaluation of candidate transport signals as replacements for Q.

Design
------
Strategy:  NY_Continuation (strategy_library.py line 471).
           Enter at hour==13 UTC in direction of EMA9/EMA21 trend.
           Exactly one signal per trading day (at most).
           Enter next open, exit at HOLD_BARS=24, ATR-stop 1.5, target 2.5.

Data split
----------
  IS calibration : 2023-01 to 2024-12  (used ONLY for threshold selection)
  WF fold 1      : 2025-01 to 2025-06  (walk-forward OOS fold 1)
  WF fold 2      : 2025-07 to 2025-10  (walk-forward OOS fold 2)
  Held-out       : 2026-01 to 2026-07  (touched before — final sanity check only,
                                         NO threshold tuning on this period)

Candidate gates (applied independently to NY_Continuation signal):
  A. No gate         — enter every NY_Continuation bar (ungated baseline)
  B. Q gate          — Strong_Coherent: tr_Q >= q95 (existing, q95=1.732 frozen)
  C. rv5 pct gate    — realized_vol_5 >= IS 70th percentile at hour==13
  D. v_abs gate      — |tr_grad_ln_s| (field velocity proxy) >= IS 70th pct at hour==13
  E. v_persist gate  — EWMA sign-persistence of tr_grad_ln_s >= IS 70th pct at hour==13
  F. tension gate    — |T_sys - T_sys_ewm| (T_sys deviation) >= IS 70th pct at hour==13

All IS thresholds are derived from 2023-2024 ONLY.
The same frozen thresholds are applied to WF folds and held-out — no re-fitting.

Cost model (matches existing pipeline exactly):
  COMMISSION = 0.00020  (2 pip one-way)
  SLIPPAGE   = 0.00005  (0.5 pip per side)
  TOTAL RT   = 0.00050  (5 pip round-trip = COMMISSION*2 + SLIPPAGE*2)
  ATR_STOP   = 1.5
  ATR_TARGET = 2.5
  HOLD_BARS  = 24

Outputs: results/transport_signal_eval/ directory with:
  - signal_stats.csv         : per-signal IS/WF1/WF2/HO statistics
  - trade_log_<gate>.csv     : per-trade records for each gate
  - EVAL_REPORT.md           : narrative summary

No existing files are modified.
"""

import sys
import warnings
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────────────────
HERE = Path(__file__).resolve().parent
CACHE_DIR   = HERE / "cache"
RESULTS_DIR = HERE / "results" / "transport_signal_eval"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ── Execution constants (identical to existing pipeline) ──────────────────
COMMISSION  = 0.00020
SLIPPAGE    = 0.00005
TOTAL_RT    = (COMMISSION + SLIPPAGE) * 2   # 0.00050
ATR_STOP    = 1.5
ATR_TARGET  = 2.5
HOLD_BARS   = 24

# ── Data split boundaries ─────────────────────────────────────────────────
IS_START   = "2023-01"
IS_END     = "2024-12"
WF1_START  = "2025-01"
WF1_END    = "2025-06"
WF2_START  = "2025-07"
WF2_END    = "2025-10"
HO_START   = "2026-01"
HO_END     = "2026-07"

# Frozen Q threshold from calibration (NOT re-derived)
Q95_FROZEN = 1.7322887804197729


# ══════════════════════════════════════════════════════════════════════════
# 1.  DATA LOADING
# ══════════════════════════════════════════════════════════════════════════

def load_cache() -> pd.DataFrame:
    """Load all monthly cache files and concatenate."""
    files = sorted(CACHE_DIR.glob("ohlc_transport_*.parquet"))
    if not files:
        raise FileNotFoundError(f"No cache files in {CACHE_DIR}")
    frames = []
    for f in files:
        try:
            df = pd.read_parquet(f)
            frames.append(df)
        except Exception as e:
            print(f"  Warning: could not load {f.name}: {e}")
    full = pd.concat(frames).sort_index()
    # Drop duplicates (monthly files sometimes overlap at boundaries)
    full = full[~full.index.duplicated(keep='first')]
    return full


def split_data(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Return named period slices."""
    return {
        "IS":  df[IS_START:IS_END],
        "WF1": df[WF1_START:WF1_END],
        "WF2": df[WF2_START:WF2_END],
        "HO":  df.get(HO_START) and df[HO_START:HO_END] or df[HO_START:HO_END],
    }


# ══════════════════════════════════════════════════════════════════════════
# 2.  FEATURE ENGINEERING
# ══════════════════════════════════════════════════════════════════════════

EWMA_SPAN = 12   # 1-hour EWMA for smoothing (12 × 5min bars)
TAU       = 5.0  # relaxation time in bars (matches transport_layer.py DEFAULT_TAU)


def add_transport_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add candidate signal columns.  All computations are causal (no look-ahead)."""
    out = df.copy()

    # ── A. Already have tr_Q, realized_vol_5 in cache ────────────────────

    # ── B. Field velocity proxy: tr_grad_ln_s (= ∇ ln s, one-bar backward diff)
    #       This IS the ∂s/∂t of the composite signal, re-expressed as log-gradient.
    #       Already in cache as tr_grad_ln_s.
    out['v_abs']    = out['tr_grad_ln_s'].abs()

    # ── C. v_persistence: EWMA of sign of tr_grad_ln_s
    #       Measures directional momentum of the composite field.
    #       Range (-1, +1); high |value| → composite trending consistently.
    sign_v = np.sign(out['tr_grad_ln_s'])
    out['v_persist_abs'] = sign_v.ewm(span=EWMA_SPAN, adjust=False).mean().abs()

    # ── D. Tension: |tr_grad_ln_s| × τ  (= |v| × τ, inertia proxy)
    #       Directly from transport_layer: tension = |v| * tau represents
    #       how much "inertia" the field currently carries before damping.
    out['tension'] = out['v_abs'] * TAU

    # ── E. T_sys deviation: |T_sys - EWMA(T_sys)|
    #       T_sys is a long-lag ODE integrator; its deviation from its own
    #       short-run EWMA captures sudden acceleration — which may coincide
    #       with regime transitions.
    tsys_ewm = out['T_sys'].ewm(span=EWMA_SPAN, adjust=False).mean()
    out['tsys_dev'] = (out['T_sys'] - tsys_ewm).abs()

    return out


# ══════════════════════════════════════════════════════════════════════════
# 3.  NY_CONTINUATION SIGNAL GENERATION
# ══════════════════════════════════════════════════════════════════════════

def generate_ny_signal(df: pd.DataFrame) -> pd.Series:
    """
    Reproduce NY_Continuation from strategy_library.py exactly.

    Enter at hour==13 UTC in direction of EMA9/EMA21 trend (first occurrence
    each hour where trend direction changes).
    Returns Series of {-1, 0, +1}.
    """
    hour = df.index.hour
    fast = df['close'].ewm(span=9,  adjust=False).mean()
    slow = df['close'].ewm(span=21, adjust=False).mean()
    trend = (fast > slow).astype(int) - (fast < slow).astype(int)
    is_ny = (hour == 13)

    sig = pd.Series(0, index=df.index, dtype=np.int8)
    sig[is_ny & (trend == 1)  & (trend.shift(1) != 1)]  =  1
    sig[is_ny & (trend == -1) & (trend.shift(1) != -1)] = -1
    return sig


# ══════════════════════════════════════════════════════════════════════════
# 4.  GATE DEFINITIONS
# ══════════════════════════════════════════════════════════════════════════

def derive_is_thresholds(is_df: pd.DataFrame, pct: float = 70.0) -> Dict[str, float]:
    """
    Derive all gate thresholds from IS data, at hour==13 bars only.
    pct=70 means the threshold is the 70th percentile of the IS distribution
    at NY-open bars — i.e. the gate admits the top ~30% of bars by that signal.
    """
    ny_bars = is_df[is_df.index.hour == 13].dropna(
        subset=['tr_Q', 'realized_vol_5', 'v_abs', 'v_persist_abs', 'tension', 'tsys_dev']
    )
    thresholds = {
        'rv5':       float(np.percentile(ny_bars['realized_vol_5'], pct)),
        'v_abs':     float(np.percentile(ny_bars['v_abs'], pct)),
        'v_persist': float(np.percentile(ny_bars['v_persist_abs'], pct)),
        'tension':   float(np.percentile(ny_bars['tension'], pct)),
        'tsys_dev':  float(np.percentile(ny_bars['tsys_dev'], pct)),
    }
    return thresholds


def build_gates(df: pd.DataFrame, thresholds: Dict[str, float]) -> Dict[str, pd.Series]:
    """
    Return a boolean Series per gate.  True = allow trade.
    All comparisons use only contemporaneous (bar-close) information.
    """
    gates = {
        # A: no gate — always True
        'A_no_gate': pd.Series(True, index=df.index),

        # B: Q gate (existing) — Strong_Coherent
        'B_Q_gate': df['tr_Q'] >= Q95_FROZEN,

        # C: rv5 gate — realized vol above IS 70th percentile
        'C_rv5': df['realized_vol_5'] >= thresholds['rv5'],

        # D: field velocity gate — |grad_ln_s| above IS 70th percentile
        'D_v_abs': df['v_abs'] >= thresholds['v_abs'],

        # E: v_persistence gate — EWMA sign persistence above IS 70th percentile
        'E_v_persist': df['v_persist_abs'] >= thresholds['v_persist'],

        # F: tension gate — |v| × τ above IS 70th percentile
        'F_tension': df['tension'] >= thresholds['tension'],

        # G: T_sys deviation gate
        'G_tsys_dev': df['tsys_dev'] >= thresholds['tsys_dev'],
    }
    return {k: v.fillna(False) for k, v in gates.items()}


# ══════════════════════════════════════════════════════════════════════════
# 5.  TRADE SIMULATOR
# ══════════════════════════════════════════════════════════════════════════

def simulate_trades(
    df: pd.DataFrame,
    signal: pd.Series,
    gate: pd.Series,
    label: str,
    period: str,
) -> pd.DataFrame:
    """
    Bar-by-bar trade simulator.

    Entry:  bar where signal != 0 AND gate == True
            Execute at NEXT bar's open.
    Exit:   first of: ATR_STOP hit, ATR_TARGET hit, HOLD_BARS elapsed.
            Exit at bar-close (conservative — no intra-bar precision).
    Cost:   TOTAL_RT applied to each closed trade.
    One trade at a time.
    """
    records = []

    in_trade    = False
    direction   = 0
    entry_price = 0.0
    entry_bar   = -1
    stop_price  = 0.0
    tgt_price   = 0.0
    entry_atr   = 0.0

    sig_arr  = signal.values
    gate_arr = gate.values
    open_arr = df['open'].values
    close_arr= df['close'].values
    high_arr = df['high'].values
    low_arr  = df['low'].values
    atr_arr  = df['atr_14'].values
    ts_arr   = df.index

    n = len(df)

    for i in range(1, n):    # start at 1 — we enter at bar i using signal from i-1
        # ── manage open trade ────────────────────────────────────────────
        if in_trade:
            bars_held = i - entry_bar
            hi, lo, cl = high_arr[i], low_arr[i], close_arr[i]

            # Check stop
            if direction == 1 and lo <= stop_price:
                exit_price = stop_price
                exit_reason = "stop"
            elif direction == -1 and hi >= stop_price:
                exit_price = stop_price
                exit_reason = "stop"
            # Check target
            elif direction == 1 and hi >= tgt_price:
                exit_price = tgt_price
                exit_reason = "target"
            elif direction == -1 and lo <= tgt_price:
                exit_price = tgt_price
                exit_reason = "target"
            # Time exit
            elif bars_held >= HOLD_BARS:
                exit_price = cl
                exit_reason = "time"
            else:
                continue

            # Compute PnL (in price units = EUR/USD)
            raw_pnl  = direction * (exit_price - entry_price)
            net_pnl  = raw_pnl - TOTAL_RT

            records.append({
                'gate':         label,
                'period':       period,
                'entry_time':   ts_arr[entry_bar],
                'exit_time':    ts_arr[i],
                'direction':    direction,
                'entry_price':  entry_price,
                'exit_price':   exit_price,
                'exit_reason':  exit_reason,
                'bars_held':    bars_held,
                'entry_atr':    entry_atr,
                'raw_pnl':      raw_pnl,
                'net_pnl':      net_pnl,
                'cost':         TOTAL_RT,
            })
            in_trade = False

        # ── check for new entry (from previous bar's signal) ─────────────
        if not in_trade and sig_arr[i-1] != 0 and gate_arr[i-1]:
            direction   = int(sig_arr[i-1])
            entry_price = float(open_arr[i])   # enter at next bar's open
            entry_bar   = i
            entry_atr   = float(atr_arr[i])
            atr         = entry_atr if entry_atr > 0 else 0.0001
            stop_price  = entry_price - direction * ATR_STOP   * atr
            tgt_price   = entry_price + direction * ATR_TARGET * atr
            in_trade    = True

    # Close any remaining open trade at last bar close
    if in_trade:
        cl = close_arr[-1]
        raw_pnl = direction * (cl - entry_price)
        net_pnl = raw_pnl - TOTAL_RT
        records.append({
            'gate':         label,
            'period':       period,
            'entry_time':   ts_arr[entry_bar],
            'exit_time':    ts_arr[-1],
            'direction':    direction,
            'entry_price':  entry_price,
            'exit_price':   cl,
            'exit_reason':  'end_of_data',
            'bars_held':    len(df) - entry_bar,
            'entry_atr':    entry_atr,
            'raw_pnl':      raw_pnl,
            'net_pnl':      net_pnl,
            'cost':         TOTAL_RT,
        })

    return pd.DataFrame(records)


# ══════════════════════════════════════════════════════════════════════════
# 6.  PERFORMANCE METRICS
# ══════════════════════════════════════════════════════════════════════════

def compute_metrics(trades: pd.DataFrame, gate: str, period: str) -> Dict:
    """Compute trading performance metrics from a trade log."""
    if trades.empty:
        return {
            'gate': gate, 'period': period,
            'n_trades': 0, 'n_wins': 0, 'n_losses': 0,
            'win_rate': np.nan, 'profit_factor': np.nan,
            'expectancy': np.nan, 'expectancy_pips': np.nan,
            'total_net_pnl': 0.0, 'total_net_pips': 0.0,
            'avg_winner': np.nan, 'avg_loser': np.nan,
            'max_drawdown': np.nan, 'sharpe': np.nan,
            'calmar': np.nan,
            'cost_sensitivity_2x': np.nan,
            'pct_gate_passed': np.nan,
        }

    t = trades.copy()
    wins   = t[t['net_pnl'] > 0]
    losses = t[t['net_pnl'] <= 0]

    gross_win  = wins['net_pnl'].sum()
    gross_loss = losses['net_pnl'].sum()

    pf = (gross_win / -gross_loss) if gross_loss < 0 else np.inf
    exp = t['net_pnl'].mean()

    # Equity curve for drawdown / Sharpe
    equity = t['net_pnl'].cumsum()
    running_max = equity.cummax()
    drawdown = running_max - equity
    max_dd = drawdown.max()

    # Sharpe (annualised assuming ~250 trades/year is unrealistic for NY-only;
    # use per-trade Sharpe which is more honest for small N)
    trade_sharpe = (exp / t['net_pnl'].std()) if t['net_pnl'].std() > 0 else np.nan

    # Calmar = total return / max drawdown
    calmar = (equity.iloc[-1] / max_dd) if max_dd > 0 else np.nan

    # Cost sensitivity: how does PF change at 2× costs?
    extra_cost = TOTAL_RT  # additional TOTAL_RT applied
    t2 = t.copy()
    t2['net_pnl2'] = t2['net_pnl'] - extra_cost
    w2 = t2[t2['net_pnl2'] > 0]['net_pnl2'].sum()
    l2 = t2[t2['net_pnl2'] <= 0]['net_pnl2'].sum()
    pf2 = (w2 / -l2) if l2 < 0 else np.inf

    return {
        'gate':              gate,
        'period':            period,
        'n_trades':          len(t),
        'n_wins':            len(wins),
        'n_losses':          len(losses),
        'win_rate':          len(wins) / len(t),
        'profit_factor':     round(pf, 3),
        'expectancy':        round(exp, 6),
        'expectancy_pips':   round(exp * 10000, 2),
        'total_net_pnl':     round(t['net_pnl'].sum(), 6),
        'total_net_pips':    round(t['net_pnl'].sum() * 10000, 2),
        'avg_winner':        round(wins['net_pnl'].mean() * 10000, 2) if len(wins) else np.nan,
        'avg_loser':         round(losses['net_pnl'].mean() * 10000, 2) if len(losses) else np.nan,
        'max_drawdown_pips': round(max_dd * 10000, 2),
        'sharpe_per_trade':  round(trade_sharpe, 3) if not np.isnan(trade_sharpe) else np.nan,
        'calmar':            round(calmar, 3) if not np.isnan(calmar) else np.nan,
        'pf_2x_cost':        round(pf2, 3),
        'cost_sensitivity':  round(pf - pf2, 3),
    }


def bootstrap_ci(net_pnl: pd.Series, n_boot: int = 2000, ci: float = 0.95) -> Tuple[float, float]:
    """Bootstrap confidence interval for mean net PnL per trade."""
    if len(net_pnl) < 5:
        return (np.nan, np.nan)
    rng = np.random.default_rng(42)
    boot_means = [rng.choice(net_pnl.values, size=len(net_pnl), replace=True).mean()
                  for _ in range(n_boot)]
    lo = np.percentile(boot_means, (1 - ci) / 2 * 100)
    hi = np.percentile(boot_means, (1 + ci) / 2 * 100)
    return (round(lo * 10000, 2), round(hi * 10000, 2))


# ══════════════════════════════════════════════════════════════════════════
# 7.  MAIN EVALUATION LOOP
# ══════════════════════════════════════════════════════════════════════════

def run_evaluation():
    print("=" * 70)
    print("TRANSPORT SIGNAL EVALUATION")
    print("=" * 70)

    # ── Load data ─────────────────────────────────────────────────────────
    print("\nLoading cache files...")
    full_df = load_cache()
    print(f"  Total bars: {len(full_df):,}  ({full_df.index[0].date()} to {full_df.index[-1].date()})")

    # ── Add features ──────────────────────────────────────────────────────
    print("Adding transport features...")
    full_df = add_transport_features(full_df)

    # ── Generate NY signal over full history ──────────────────────────────
    print("Generating NY_Continuation signal...")
    full_signal = generate_ny_signal(full_df)

    # ── Split ─────────────────────────────────────────────────────────────
    periods = {
        "IS":  (IS_START,  IS_END),
        "WF1": (WF1_START, WF1_END),
        "WF2": (WF2_START, WF2_END),
        "HO":  (HO_START,  HO_END),
    }
    slices = {}
    for name, (start, end) in periods.items():
        try:
            slices[name] = full_df[start:end]
        except Exception:
            slices[name] = pd.DataFrame()
    
    # Report period sizes
    for name, sl in slices.items():
        ny_count = (sl.index.hour == 13).sum() if len(sl) else 0
        sig_count = (full_signal[sl.index] != 0).sum() if len(sl) else 0
        print(f"  {name}: {len(sl):,} bars, {ny_count:,} hour-13 bars, {sig_count:,} raw signals")

    # ── Derive thresholds from IS only ────────────────────────────────────
    print("\nDeriving IS thresholds (2023-2024 only, 70th pct at hour==13)...")
    is_df = slices["IS"]
    thresholds = derive_is_thresholds(is_df, pct=70.0)
    print("  Thresholds:")
    for k, v in thresholds.items():
        print(f"    {k:15s}: {v:.6f}")
    print(f"    {'Q (frozen)':15s}: {Q95_FROZEN:.6f}  (q95 from manifest, not re-derived)")

    # ── Run all gate × period combinations ────────────────────────────────
    all_trades  : List[pd.DataFrame] = []
    all_metrics : List[Dict]         = []

    print("\nRunning simulations...")
    for period_name, sl in slices.items():
        if len(sl) < 100:
            print(f"  {period_name}: skipping (insufficient data: {len(sl)} bars)")
            continue

        sig_slice  = full_signal[sl.index]
        gates      = build_gates(sl, thresholds)

        for gate_name, gate_series in gates.items():
            trades = simulate_trades(sl, sig_slice, gate_series, gate_name, period_name)
            metrics = compute_metrics(trades, gate_name, period_name)

            if len(trades) > 0:
                ci_lo, ci_hi = bootstrap_ci(trades['net_pnl'])
                metrics['boot_ci_lo_pips'] = ci_lo
                metrics['boot_ci_hi_pips'] = ci_hi
            else:
                metrics['boot_ci_lo_pips'] = np.nan
                metrics['boot_ci_hi_pips'] = np.nan

            all_trades.append(trades)
            all_metrics.append(metrics)

            n = metrics['n_trades']
            pf = metrics['profit_factor']
            exp_p = metrics['expectancy_pips']
            print(f"  {period_name:4s} | {gate_name:18s} | "
                  f"N={n:4d}  PF={pf:6.3f}  exp={exp_p:+7.2f}pip")

    # ── Save results ──────────────────────────────────────────────────────
    print("\nSaving results...")

    metrics_df = pd.DataFrame(all_metrics)
    metrics_df.to_csv(RESULTS_DIR / "signal_stats.csv", index=False)
    print(f"  Wrote signal_stats.csv ({len(metrics_df)} rows)")

    if all_trades:
        trades_df = pd.concat([t for t in all_trades if not t.empty], ignore_index=True)
        trades_df.to_csv(RESULTS_DIR / "trade_log_all.csv", index=False)
        for gate_name in trades_df['gate'].unique():
            sub = trades_df[trades_df['gate'] == gate_name]
            sub.to_csv(RESULTS_DIR / f"trade_log_{gate_name}.csv", index=False)
        print(f"  Wrote trade_log_all.csv ({len(trades_df)} trades)")

    # Save thresholds for reproducibility
    thresh_record = {
        'derivation_period': f"{IS_START} to {IS_END}",
        'percentile': 70.0,
        'Q_frozen_q95': Q95_FROZEN,
        **thresholds
    }
    with open(RESULTS_DIR / "thresholds.json", "w") as f:
        json.dump(thresh_record, f, indent=2)

    return metrics_df, trades_df if all_trades else pd.DataFrame()


# ══════════════════════════════════════════════════════════════════════════
# 8.  REPORTING
# ══════════════════════════════════════════════════════════════════════════

def build_report(metrics_df: pd.DataFrame, trades_df: pd.DataFrame) -> str:
    """Build a narrative markdown report from results."""
    lines = []
    lines.append("# Transport Signal Evaluation Report\n")
    lines.append(f"**Generated:** {pd.Timestamp.now(tz='UTC').strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(f"\n**Strategy:** NY_Continuation (hour==13 UTC, EMA9/EMA21 trend)")
    lines.append(f"\n**Cost model:** {TOTAL_RT*10000:.1f} pip round-trip "
                 f"(commission {COMMISSION*10000:.1f}pip + slippage {SLIPPAGE*10000:.1f}pip × 2)")
    lines.append(f"\n**IS calibration:** {IS_START} to {IS_END} (threshold derivation only)")
    lines.append(f"\n**WF fold 1:** {WF1_START} to {WF1_END}")
    lines.append(f"\n**WF fold 2:** {WF2_START} to {WF2_END}")
    lines.append(f"\n**Held-out:** {HO_START} to {HO_END} (sanity check only)\n")

    lines.append("\n---\n")
    lines.append("## Candidate Gate Descriptions\n")
    lines.append("| Gate | Signal | Derivation |")
    lines.append("|------|--------|------------|")
    lines.append("| A_no_gate    | Always True | Baseline: enter every NY bar |")
    lines.append("| B_Q_gate     | tr_Q ≥ 1.732 | Existing Q gate (q95 frozen from 2023–2025 calibration) |")
    lines.append("| C_rv5        | realized_vol_5 ≥ IS 70th pct | 5-bar realized volatility of returns |")
    lines.append("| D_v_abs      | |tr_grad_ln_s| ≥ IS 70th pct | Field velocity magnitude (|∂s/∂t|) |")
    lines.append("| E_v_persist  | EWMA sign persistence ≥ IS 70th pct | Directional momentum of composite s |")
    lines.append("| F_tension    | |tr_grad_ln_s| × τ ≥ IS 70th pct | Inertia proxy (v × τ = tension) |")
    lines.append("| G_tsys_dev   | |T_sys − EWMA(T_sys)| ≥ IS 70th pct | T_sys acceleration |")
    lines.append("")

    # --- Summary tables ---
    for period in ["IS", "WF1", "WF2", "HO"]:
        sub = metrics_df[metrics_df['period'] == period]
        if sub.empty:
            continue
        lines.append(f"\n## {period} Performance\n")
        display_cols = ['gate','n_trades','win_rate','profit_factor',
                        'expectancy_pips','total_net_pips','max_drawdown_pips',
                        'sharpe_per_trade','pf_2x_cost',
                        'boot_ci_lo_pips','boot_ci_hi_pips']
        display_cols = [c for c in display_cols if c in sub.columns]
        sub_disp = sub[display_cols].copy()
        sub_disp['win_rate'] = sub_disp['win_rate'].map(lambda x: f"{x:.1%}" if pd.notna(x) else "n/a")
        lines.append(sub_disp.to_markdown(index=False, floatfmt=".3f"))

    lines.append("\n---\n")
    lines.append("## Walk-Forward Summary (WF1 + WF2 combined)\n")

    wf = metrics_df[metrics_df['period'].isin(['WF1','WF2'])]
    if not wf.empty:
        wf_agg = wf.groupby('gate').agg(
            n_trades=('n_trades','sum'),
            total_net_pips=('total_net_pips','sum'),
        ).reset_index()
        wf_pf = []
        for gate_name, grp in wf.groupby('gate'):
            tlog = trades_df[
                (trades_df['gate'] == gate_name) &
                (trades_df['period'].isin(['WF1','WF2']))
            ]
            if len(tlog):
                w = tlog[tlog['net_pnl'] > 0]['net_pnl'].sum()
                l = tlog[tlog['net_pnl'] <= 0]['net_pnl'].sum()
                pf = (w / -l) if l < 0 else np.inf
                exp = tlog['net_pnl'].mean() * 10000
                ci_lo, ci_hi = bootstrap_ci(tlog['net_pnl'])
            else:
                pf, exp, ci_lo, ci_hi = np.nan, np.nan, np.nan, np.nan
            wf_pf.append({'gate': gate_name, 'pf': round(pf, 3),
                          'exp_pips': round(exp, 2) if pd.notna(exp) else np.nan,
                          'ci_95_pips': f"[{ci_lo}, {ci_hi}]"})
        wf_agg = wf_agg.merge(pd.DataFrame(wf_pf), on='gate')
        lines.append(wf_agg.to_markdown(index=False, floatfmt=".3f"))

    lines.append("\n---\n")
    lines.append("## Gate Correlation Note\n")
    lines.append("D_v_abs and F_tension are monotone functions of the same underlying quantity "
                 "|tr_grad_ln_s|. Any performance difference between them is purely from the "
                 "different threshold level produced by the τ=5 multiplier. They are NOT "
                 "independent signals and should not both be selected as candidates if one "
                 "is already chosen.\n")
    lines.append("\nE_v_persist (EWMA sign persistence) IS a distinct signal: it measures "
                 "directional continuity over a window, not instantaneous magnitude.\n")

    lines.append("\n---\n")
    lines.append("## Decision Criteria\n")
    lines.append("A gate is considered superior to the no-gate baseline (A) if ALL of:\n")
    lines.append("1. WF1 + WF2 combined PF > 1.0\n")
    lines.append("2. WF expectancy per trade > 0 (positive after full costs)\n")
    lines.append("3. 95% bootstrap CI lower bound > −5 pips (excludes clearly negative)\n")
    lines.append("4. PF at 2× cost still > 1.0\n")
    lines.append("5. N_trades ≥ 30 over WF1+WF2 (minimum for inference)\n")
    lines.append("\nIf multiple gates pass all five criteria, prefer the simpler one "
                 "(lower maintenance burden, fewer parameters).\n")

    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════
# 9.  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    metrics_df, trades_df = run_evaluation()

    print("\nBuilding report...")
    report = build_report(metrics_df, trades_df)
    report_path = RESULTS_DIR / "EVAL_REPORT.md"
    report_path.write_text(report)
    print(f"  Wrote {report_path}")

    print("\nDONE.  Key outputs:")
    print(f"  {RESULTS_DIR}/signal_stats.csv")
    print(f"  {RESULTS_DIR}/trade_log_all.csv")
    print(f"  {RESULTS_DIR}/EVAL_REPORT.md")
    print(f"  {RESULTS_DIR}/thresholds.json")
