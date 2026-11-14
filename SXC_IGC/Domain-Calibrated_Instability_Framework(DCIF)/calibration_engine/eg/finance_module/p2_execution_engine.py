"""
p2_execution_engine.py — Bar-by-bar replay engine for Phase 2 Transport OS.

Design:
  - Streams monthly cache parquet files one at a time
  - For each bar: reads Q → classifies regime → calls OS.decide()
  - Generates strategy signal for the OS-selected strategy
  - Executes trade with OS-prescribed risk fraction, stop, target
  - Records full allocator decision log + trade log
  - Only one trade active at a time (no pyramiding)

Key difference from Phase 1:
  Phase 1 ran all strategies flat and independently (PF < 1 uniform).
  Phase 2 applies the OS: dynamic sizing, stop widening, selective trading.
  The execution cost model is IDENTICAL.

Memory: one month at a time, appends to running equity tracker.
"""

import sys
import gc
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

_HERE = Path(__file__).resolve().parent
_CE   = _HERE.parents[1]
for p in [str(_CE), str(_HERE), str(_HERE / "v12_validate")]:
    if p not in sys.path:
        sys.path.insert(0, p)

from p2_transport_os import (
    TransportOSCalibration,
    classify_q_global_p2,
    BASE_RISK_PCT,
    COMMISSION_RT,
)
from strategy_library import get_all_strategies

PHASE2_DIR = _HERE / "results" / "phase2"

# Execution constants (identical to Phase 1 + Phase 2 baseline)
HOLD_BARS = 24        # max 2 hours at 5-min bars

REGIMES_5 = [
    "Deep_Incoherent", "Mod_Incoherent", "Transition",
    "Weak_Coherent",   "Strong_Coherent",
]


# ═══════════════════════════════════════════════════════════════════════════
# Single-bar state
# ═══════════════════════════════════════════════════════════════════════════

class BarState:
    """Minimal stateful position tracker for one-at-a-time trade management."""
    __slots__ = [
        "in_trade", "direction", "entry_price", "entry_bar",
        "stop_price", "target_price", "strategy", "regime",
        "risk_fraction", "stop_mult", "target_mult",
    ]
    def __init__(self):
        self.in_trade    = False
        self.direction   = 0
        self.entry_price = 0.0
        self.entry_bar   = -1
        self.stop_price  = 0.0
        self.target_price= 0.0
        self.strategy    = ""
        self.regime      = ""
        self.risk_fraction = 0.0
        self.stop_mult   = 1.5
        self.target_mult = 2.5


# ═══════════════════════════════════════════════════════════════════════════
# Core execution function
# ═══════════════════════════════════════════════════════════════════════════

def run_transport_os_on_chunk(
    df: pd.DataFrame,
    os: TransportOSCalibration,
    strategy_registry: Dict,
    state: BarState,
    bar_offset: int = 0,
) -> Tuple[pd.DataFrame, pd.DataFrame, BarState]:
    """
    Run the Transport OS on one monthly DataFrame chunk.

    Returns:
      trade_records    : DataFrame of completed trades this chunk
      decision_records : DataFrame of every-bar allocator decisions
      state            : updated BarState (carry-over to next chunk)
    """
    close  = df["close"].values
    high   = df["high"].values
    low    = df["low"].values
    atr    = df["atr_14"].values
    Q_vals = df["tr_Q"].values
    n      = len(df)

    # Pre-compute all strategy signals for this chunk (strategies don't see Q)
    strat_signals: Dict[str, np.ndarray] = {}
    for name, meta in strategy_registry.items():
        try:
            sig = meta["fn"](df)
            strat_signals[name] = sig.values
        except Exception:
            strat_signals[name] = np.zeros(n, dtype=np.int8)

    trades    : List[dict] = []
    decisions : List[dict] = []

    for i in range(n):
        ts       = df.index[i]
        q_val    = float(Q_vals[i]) if not np.isnan(Q_vals[i]) else np.nan
        regime   = classify_q_global_p2(q_val, os.q05, os.q95)
        decision = os.decide(regime)

        # ── Manage open trade ────────────────────────────────────────────
        trade_closed = False
        if state.in_trade:
            h = float(high[i])
            l = float(low[i])
            c = float(close[i])
            elapsed = i + bar_offset - state.entry_bar

            stop_hit = target_hit = timeout = False

            if state.direction == 1:
                if l <= state.stop_price:
                    stop_hit = True; exit_price = state.stop_price
                elif h >= state.target_price:
                    target_hit = True; exit_price = state.target_price
            else:
                if h >= state.stop_price:
                    stop_hit = True; exit_price = state.stop_price
                elif l <= state.target_price:
                    target_hit = True; exit_price = state.target_price

            if elapsed >= HOLD_BARS and not stop_hit and not target_hit:
                timeout = True; exit_price = c

            if stop_hit or target_hit or timeout:
                gross = state.direction * (exit_price - state.entry_price) / (state.entry_price + 1e-12)
                # FIXED: COMMISSION_RT is already a fraction of notional (0.03%),
                # so subtract directly without dividing by entry_price.
                net   = gross - COMMISSION_RT
                # Scale by risk_fraction
                scaled_net = net * state.risk_fraction

                trades.append({
                    "entry_time"   : state.entry_bar,        # stored as integer bar index
                    "exit_time"    : i + bar_offset,
                    "entry_ts"     : df.index[max(0, i - elapsed)],  # approx
                    "exit_ts"      : ts,
                    "strategy"     : state.strategy,
                    "regime"       : state.regime,
                    "direction"    : state.direction,
                    "entry_price"  : state.entry_price,
                    "exit_price"   : exit_price,
                    "gross_ret"    : gross,
                    "net_ret"      : net,
                    "scaled_net"   : scaled_net,             # risk-weighted return
                    "risk_fraction": state.risk_fraction,
                    "duration_bars": elapsed,
                    "stop_hit"     : stop_hit,
                    "target_hit"   : target_hit,
                    "timeout"      : timeout,
                    "stop_mult"    : state.stop_mult,
                    "target_mult"  : state.target_mult,
                    "entry_Q"      : q_val,
                })
                state.in_trade = False
                trade_closed   = True

        # ── New trade entry ───────────────────────────────────────────────
        if not state.in_trade and decision["trading_allowed"]:
            selected = decision["strategy"]
            signals  = strat_signals.get(selected)
            if signals is not None:
                sig = int(signals[i]) if i < len(signals) else 0
                if sig != 0:
                    atr_i = float(atr[i]) if not np.isnan(atr[i]) else 0.0
                    ep    = float(close[i])
                    if atr_i > 0 and ep > 0:
                        sm = decision["stop_atr_mult"]
                        tm = decision["target_atr_mult"]
                        state.in_trade     = True
                        state.direction    = sig
                        state.entry_price  = ep
                        state.entry_bar    = i + bar_offset
                        state.stop_price   = ep - sig * sm * atr_i
                        state.target_price = ep + sig * tm * atr_i
                        state.strategy     = selected
                        state.regime       = regime
                        state.risk_fraction= decision["risk_fraction"]
                        state.stop_mult    = sm
                        state.target_mult  = tm

        # ── Record decision ───────────────────────────────────────────────
        decisions.append({
            "timestamp"      : ts,
            "bar_idx"        : i + bar_offset,
            "Q"              : q_val,
            "regime"         : regime,
            "trading_allowed": decision["trading_allowed"],
            "selected_strategy": decision["strategy"],
            "risk_fraction"  : decision["risk_fraction"],
            "stop_mult"      : decision["stop_atr_mult"],
            "target_mult"    : decision["target_atr_mult"],
            "in_trade"       : state.in_trade,
            "confidence"     : decision["confidence"],
        })

    trade_df    = pd.DataFrame(trades)    if trades    else pd.DataFrame()
    decision_df = pd.DataFrame(decisions) if decisions else pd.DataFrame()
    return trade_df, decision_df, state


# ═══════════════════════════════════════════════════════════════════════════
# Full replay across all cached months
# ═══════════════════════════════════════════════════════════════════════════

def replay_transport_os(
    os: TransportOSCalibration,
    cache_dir: Path,
    strategy_registry: Dict,
    verbose: bool = True,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Replay the full Transport OS across all monthly cache files.

    Returns:
      all_trades    : DataFrame of all trades with scaled returns
      all_decisions : DataFrame of all per-bar OS decisions
    """
    cache_files = sorted(cache_dir.glob("ohlc_transport_*.parquet"))
    if not cache_files:
        raise FileNotFoundError(f"No cached parquet files in {cache_dir}")

    state      = BarState()
    all_trades : List[pd.DataFrame] = []
    all_dec    : List[pd.DataFrame] = []
    bar_offset = 0

    for cf in cache_files:
        if verbose:
            print(f"  Replaying {cf.name} …", flush=True)
        try:
            df = pd.read_parquet(cf)
        except Exception as e:
            if verbose:
                print(f"    WARNING: {e}")
            continue

        trade_df, dec_df, state = run_transport_os_on_chunk(
            df, os, strategy_registry, state, bar_offset=bar_offset
        )
        bar_offset += len(df)

        if len(trade_df) > 0:
            all_trades.append(trade_df)
        if len(dec_df) > 0:
            all_dec.append(dec_df)

        del df
        gc.collect()

    trades_final = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    dec_final    = pd.concat(all_dec,    ignore_index=True) if all_dec    else pd.DataFrame()

    if verbose:
        print(f"  OS replay complete: {len(trades_final)} trades, "
              f"{len(dec_final)} bar decisions", flush=True)

    return trades_final, dec_final


# ═══════════════════════════════════════════════════════════════════════════
# Allocator decision analytics
# ═══════════════════════════════════════════════════════════════════════════

def compute_allocator_analytics(dec_df: pd.DataFrame) -> dict:
    """
    Analyse how the OS behaved across the replay.

    Returns dict with:
      - no_trade_fraction
      - strategy_switch_count
      - strategy_switch_rate_per_hour
      - time_per_strategy
      - regime_time_fractions
      - avg_risk_fraction
      - risk_utilisation
    """
    if len(dec_df) == 0:
        return {}

    total_bars = len(dec_df)

    # No-trade fraction
    no_trade_mask = ~dec_df["trading_allowed"]
    no_trade_frac = float(no_trade_mask.mean())

    # Strategy switches (excluding NO_TRADE)
    strats = dec_df["selected_strategy"].values
    switches = int(np.sum(strats[1:] != strats[:-1]))
    bars_per_hour = 12  # 5-min bars
    switch_rate = switches / (total_bars / bars_per_hour)

    # Time per strategy
    time_per = dec_df.groupby("selected_strategy").size() / total_bars
    time_per = time_per.to_dict()

    # Regime time fractions
    regime_frac = dec_df.groupby("regime").size() / total_bars
    regime_frac = regime_frac.to_dict()

    # Risk utilisation
    avg_risk = float(dec_df["risk_fraction"].mean())
    max_risk = float(dec_df["risk_fraction"].max())
    risk_util = avg_risk / (max_risk + 1e-12)

    # Avg regime duration
    regime_arr = dec_df["regime"].values
    runs = []
    cur = regime_arr[0]; length = 1
    for v in regime_arr[1:]:
        if v == cur:
            length += 1
        else:
            runs.append(length)
            cur = v; length = 1
    runs.append(length)
    avg_regime_dur_bars = float(np.mean(runs)) if runs else 0.0

    return {
        "total_bars"             : total_bars,
        "no_trade_fraction"      : no_trade_frac,
        "strategy_switch_count"  : switches,
        "strategy_switch_rate_per_hour": switch_rate,
        "avg_regime_duration_bars": avg_regime_dur_bars,
        "avg_regime_duration_min" : avg_regime_dur_bars * 5,
        "avg_risk_fraction"      : avg_risk,
        "risk_utilisation"       : risk_util,
        "time_per_strategy"      : time_per,
        "regime_time_fractions"  : regime_frac,
    }
