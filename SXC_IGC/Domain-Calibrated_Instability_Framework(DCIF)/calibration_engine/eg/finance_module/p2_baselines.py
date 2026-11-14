"""
p2_baselines.py — Fixed strategy baselines for Phase 2 comparison.

Six baselines, all using IDENTICAL execution assumptions as the Transport OS:
  - Same commission/slippage (COMMISSION_RT)
  - Same base stop (1.5×ATR) and target (2.5×ATR)
  - Same max hold (24 bars)
  - Risk fraction = 1.0 (full, no OS modulation)
  - No regime filtering — trades every signal regardless of Q

Baselines:
  1. Fixed_EMA        — EMA_Crossover always active
  2. Fixed_MACD       — MACD_Trend always active
  3. Fixed_RSI        — RSI_Momentum always active
  4. Fixed_Donchian   — Donchian_Trend always active
  5. Fixed_Turtle     — Turtle_Breakout always active
  6. Fixed_Best       — NY_Continuation (Phase 1 rank #1 overall)
"""

import sys
import gc
import warnings
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

_HERE = Path(__file__).resolve().parent
_CE   = _HERE.parents[1]
for p in [str(_CE), str(_HERE), str(_HERE / "v12_validate")]:
    if p not in sys.path:
        sys.path.insert(0, p)

from p2_transport_os import COMMISSION_RT
from strategy_library import get_all_strategies

HOLD_BARS   = 24
BASE_STOP   = 1.5
BASE_TARGET = 2.5

BASELINE_STRATEGIES = {
    "Fixed_EMA"     : "EMA_Crossover",
    "Fixed_MACD"    : "MACD_Trend",
    "Fixed_RSI"     : "RSI_Momentum",
    "Fixed_Donchian": "Donchian_Trend",
    "Fixed_Turtle"  : "Turtle_Breakout",
    "Fixed_Best"    : "NY_Continuation",   # Phase 1 #1 overall composite
}


def run_baseline_on_chunk(
    df: pd.DataFrame,
    strategy_name: str,
    strategy_registry: Dict,
    state: dict,
    bar_offset: int = 0,
) -> Tuple[pd.DataFrame, dict]:
    """
    Run one fixed strategy on one month chunk.
    state = {"in_trade": bool, "direction": int, "entry_price": float,
              "entry_bar": int, "stop_price": float, "target_price": float}
    """
    close = df["close"].values
    high  = df["high"].values
    low   = df["low"].values
    atr   = df["atr_14"].values
    Q_arr = df["tr_Q"].values
    n     = len(df)

    # Generate signals once
    try:
        meta    = strategy_registry[strategy_name]
        signals = meta["fn"](df).values
    except Exception:
        return pd.DataFrame(), state

    trades: List[dict] = []

    for i in range(n):
        ts = df.index[i]

        # ── Manage open trade ────────────────────────────────────────────
        if state["in_trade"]:
            h = float(high[i])
            l = float(low[i])
            c = float(close[i])
            elapsed = i + bar_offset - state["entry_bar"]

            stop_hit = target_hit = timeout = False
            exit_price = c

            if state["direction"] == 1:
                if l <= state["stop_price"]:
                    stop_hit = True; exit_price = state["stop_price"]
                elif h >= state["target_price"]:
                    target_hit = True; exit_price = state["target_price"]
            else:
                if h >= state["stop_price"]:
                    stop_hit = True; exit_price = state["stop_price"]
                elif l <= state["target_price"]:
                    target_hit = True; exit_price = state["target_price"]

            if elapsed >= HOLD_BARS and not stop_hit and not target_hit:
                timeout = True; exit_price = c

            if stop_hit or target_hit or timeout:
                gross = state["direction"] * (exit_price - state["entry_price"]) / (state["entry_price"] + 1e-12)
                net   = gross - COMMISSION_RT / state["entry_price"]
                q_val = float(Q_arr[i]) if not np.isnan(Q_arr[i]) else np.nan

                trades.append({
                    "exit_ts"      : ts,
                    "strategy"     : strategy_name,
                    "direction"    : state["direction"],
                    "entry_price"  : state["entry_price"],
                    "exit_price"   : exit_price,
                    "gross_ret"    : gross,
                    "net_ret"      : net,
                    "scaled_net"   : net,   # baselines: no risk scaling
                    "risk_fraction": 1.0,
                    "duration_bars": elapsed,
                    "stop_hit"     : stop_hit,
                    "target_hit"   : target_hit,
                    "timeout"      : timeout,
                    "entry_Q"      : q_val,
                })
                state["in_trade"] = False

        # ── New trade entry ───────────────────────────────────────────────
        if not state["in_trade"]:
            sig = int(signals[i]) if i < len(signals) else 0
            if sig != 0:
                atr_i = float(atr[i]) if not np.isnan(atr[i]) else 0.0
                ep    = float(close[i])
                if atr_i > 0 and ep > 0:
                    state["in_trade"]    = True
                    state["direction"]   = sig
                    state["entry_price"] = ep
                    state["entry_bar"]   = i + bar_offset
                    state["stop_price"]  = ep - sig * BASE_STOP * atr_i
                    state["target_price"]= ep + sig * BASE_TARGET * atr_i

    return pd.DataFrame(trades) if trades else pd.DataFrame(), state


def replay_all_baselines(
    cache_dir: Path,
    strategy_registry: Dict,
    verbose: bool = True,
) -> Dict[str, pd.DataFrame]:
    """
    Replay all six baselines across all monthly cache files.
    Returns dict {baseline_name: trade_DataFrame}.
    """
    cache_files = sorted(cache_dir.glob("ohlc_transport_*.parquet"))
    if not cache_files:
        raise FileNotFoundError(f"No cache files in {cache_dir}")

    results: Dict[str, List[pd.DataFrame]] = {b: [] for b in BASELINE_STRATEGIES}
    states:  Dict[str, dict] = {
        b: {"in_trade": False, "direction": 0,
            "entry_price": 0.0, "entry_bar": -1,
            "stop_price": 0.0, "target_price": 0.0}
        for b in BASELINE_STRATEGIES
    }
    bar_offsets: Dict[str, int] = {b: 0 for b in BASELINE_STRATEGIES}

    # We need to iterate cache files once per baseline — but to save memory,
    # load each file once and run all baselines on it simultaneously.
    bar_offset_global = 0
    for cf in cache_files:
        if verbose:
            print(f"  Baselines on {cf.name} …", flush=True)
        try:
            df = pd.read_parquet(cf)
        except Exception as e:
            if verbose:
                print(f"    WARNING: {e}")
            continue

        for bname, strat_name in BASELINE_STRATEGIES.items():
            if strat_name not in strategy_registry:
                continue
            trade_df, states[bname] = run_baseline_on_chunk(
                df, strat_name, strategy_registry,
                states[bname], bar_offset=bar_offset_global
            )
            if len(trade_df) > 0:
                results[bname].append(trade_df)

        bar_offset_global += len(df)
        del df
        gc.collect()

    # Concatenate
    final: Dict[str, pd.DataFrame] = {}
    for bname, frames in results.items():
        if frames:
            combined = pd.concat(frames, ignore_index=True)
            if verbose:
                print(f"    {bname:<18}: {len(combined)} trades")
            final[bname] = combined
        else:
            final[bname] = pd.DataFrame()

    return final
