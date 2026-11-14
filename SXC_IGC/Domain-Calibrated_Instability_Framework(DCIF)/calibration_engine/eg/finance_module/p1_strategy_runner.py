"""
p1_strategy_runner.py — Incremental strategy execution for Phase 1.

For each strategy:
  1. Stream monthly chunks
  2. Generate signals (strategy does NOT see Q)
  3. Simulate execution under uniform assumptions
  4. Append trades to intermediate/<strategy>.parquet
  5. Checkpoint completion

Memory: at most 1 month OHLC + 1 month trade records in RAM at a time.
"""

import sys
import gc
from pathlib import Path
from typing import Dict, Iterator

import numpy as np
import pandas as pd

_HERE = Path(__file__).resolve().parent
_CE   = _HERE.parents[1]
for p in [str(_CE), str(_HERE), str(_HERE / "v12_validate")]:
    if p not in sys.path:
        sys.path.insert(0, p)

from p1_checkpoint import (
    append_trades_to_intermediate,
    intermediate_path_for_strategy,
    is_strategy_done,
    mark_strategy_complete,
)
from p1_data_stream import classify_q_global

# ── Execution constants (IDENTICAL for all strategies) ─────────────────────
# EUR/USD retail spread + commission, expressed as fraction of notional (round-trip):
#   Spread  : 1.0 pip half-spread → 2.0 pips RT = 0.0002 at 1.0 quote = 0.02%
#   Commission: 0.5 pip per side retail  → 1.0 pip RT = 0.0001 = 0.01%
#   Total RT : 0.0003 = 0.03% of notional
# NOTE: This is a *fraction* (not a pip count), so it is subtracted directly
# from gross_ret without any division by price.
COMMISSION_PER_SIDE = 0.00010   # 0.01% per side (fraction of notional)
SLIPPAGE_PER_SIDE   = 0.00005   # 0.005% per side
TOTAL_COST_RT       = 2 * (COMMISSION_PER_SIDE + SLIPPAGE_PER_SIDE)  # = 0.00030

HOLD_BARS  = 24     # max 2 hours at 5-min bars
ATR_STOP   = 1.5    # stop loss in ATR multiples
ATR_TARGET = 2.5    # take profit in ATR multiples

REGIMES_5 = [
    "Deep_Incoherent",
    "Mod_Incoherent",
    "Transition",
    "Weak_Coherent",
    "Strong_Coherent",
]


def simulate_strategy_on_chunk(
    df: pd.DataFrame,
    signals: pd.Series,
    strategy_name: str,
    family: str,
    q_regimes: np.ndarray,
) -> pd.DataFrame:
    """
    Simulate one strategy on one monthly chunk.

    Q regimes are pre-labeled but strategies do NOT use Q.
    Execution is identical for all strategies.

    Returns DataFrame of trades from this chunk.
    """
    close  = df["close"].values
    high   = df["high"].values
    low    = df["low"].values
    atr    = df["atr_14"].values
    Q_vals = df["tr_Q"].values
    n      = len(df)

    trades = []
    signal_vals = signals.values

    for i in range(n):
        sig = int(signal_vals[i]) if not np.isnan(signal_vals[i]) else 0
        if sig == 0:
            continue
        direction   = sig
        entry_price = float(close[i])
        atr_i       = float(atr[i]) if not np.isnan(atr[i]) else 0.0
        if atr_i <= 0 or np.isnan(entry_price) or entry_price <= 0:
            continue

        stop_dist    = ATR_STOP   * atr_i
        target_dist  = ATR_TARGET * atr_i
        stop_price   = entry_price - direction * stop_dist
        target_price = entry_price + direction * target_dist

        max_j      = min(i + HOLD_BARS, n - 1)
        exit_j     = max_j
        stop_hit   = False
        target_hit = False
        mfe = 0.0
        mae = 0.0

        for j in range(i + 1, max_j + 1):
            h = float(high[j])
            l = float(low[j])
            if np.isnan(h) or np.isnan(l):
                continue
            fav = direction * (float(close[j]) - entry_price)
            adv = direction * (entry_price - float(close[j]))
            if fav > mfe:
                mfe = fav
            if adv > mae:
                mae = adv

            if direction == 1:
                if l <= stop_price:
                    exit_j = j; stop_hit = True; break
                if h >= target_price:
                    exit_j = j; target_hit = True; break
            else:
                if h >= stop_price:
                    exit_j = j; stop_hit = True; break
                if l <= target_price:
                    exit_j = j; target_hit = True; break

        exit_price = float(close[exit_j])
        gross_ret  = direction * (exit_price - entry_price) / (entry_price + 1e-12)
        # FIXED: TOTAL_COST_RT is already a fraction of notional (0.03%),
        # so subtract it directly — do NOT divide by entry_price again.
        net_ret    = gross_ret - TOTAL_COST_RT

        trades.append({
            "strategy"     : strategy_name,
            "family"       : family,
            "entry_time"   : df.index[i],
            "exit_time"    : df.index[exit_j],
            "direction"    : direction,
            "entry_price"  : entry_price,
            "exit_price"   : exit_price,
            "gross_ret"    : gross_ret,
            "net_ret"      : net_ret,
            "duration_bars": exit_j - i,
            "stop_hit"     : stop_hit,
            "target_hit"   : target_hit,
            "timeout"      : not stop_hit and not target_hit,
            "mfe"          : mfe / (entry_price + 1e-12),
            "mae"          : mae / (entry_price + 1e-12),
            "mfe_mae_ratio": mfe / (mae + 1e-12),
            "entry_Q"      : float(Q_vals[i]) if not np.isnan(Q_vals[i]) else np.nan,
            "exit_Q"       : float(Q_vals[exit_j]) if not np.isnan(Q_vals[exit_j]) else np.nan,
            "entry_regime" : str(q_regimes[i]),
        })

    if not trades:
        return pd.DataFrame(columns=[
            "strategy","family","entry_time","exit_time","direction",
            "entry_price","exit_price","gross_ret","net_ret","duration_bars",
            "stop_hit","target_hit","timeout","mfe","mae","mfe_mae_ratio",
            "entry_Q","exit_Q","entry_regime",
        ])
    return pd.DataFrame(trades)


def run_strategy_incremental(
    strategy_name: str,
    strategy_meta: Dict,
    month_iterator: Iterator,
    manifest: Dict,
    q05: float,
    q95: float,
    verbose: bool = True,
) -> int:
    """
    Run one strategy over all monthly chunks incrementally.

    Skips if already marked complete in manifest.
    Appends trades to intermediate parquet after each chunk.
    Returns total trade count.
    """
    if is_strategy_done(manifest, strategy_name):
        p = intermediate_path_for_strategy(strategy_name)
        count = len(pd.read_parquet(p)) if p.exists() else 0
        if verbose:
            print(f"  [SKIP] {strategy_name} already done ({count} trades)", flush=True)
        return count

    fn     = strategy_meta["fn"]
    family = strategy_meta["family"]

    # Clear any previous incomplete intermediate file
    p = intermediate_path_for_strategy(strategy_name)
    if p.exists():
        p.unlink()

    total_trades = 0

    for year, month_1, df in month_iterator:
        try:
            # Generate signals (strategy does NOT see Q)
            signals = fn(df)
            # Classify Q regimes using global thresholds
            q_regimes = classify_q_global(df["tr_Q"].values, q05=q05, q95=q95)
            # Simulate
            trades = simulate_strategy_on_chunk(
                df, signals, strategy_name, family, q_regimes
            )
            if len(trades) > 0:
                append_trades_to_intermediate(strategy_name, trades)
                total_trades += len(trades)
                if verbose:
                    print(f"    {year}-{month_1:02d}: {len(trades)} trades "
                          f"(total: {total_trades})", flush=True)
        except Exception as e:
            if verbose:
                print(f"    WARNING: {strategy_name} chunk {year}-{month_1:02d} failed: {e}")
        finally:
            del df
            gc.collect()

    mark_strategy_complete(manifest, strategy_name, total_trades)
    if verbose:
        print(f"  [DONE] {strategy_name}: {total_trades} total trades", flush=True)
    return total_trades


def run_all_strategies_incremental(
    strategy_registry: Dict,
    data_dir: Path,
    manifest: Dict,
    q_quantiles: Dict,
    years=(2023, 2024, 2025),
    verbose: bool = True,
) -> None:
    """
    Run all strategies incrementally, one at a time.

    For each strategy, re-opens the month iterator so we stream fresh
    chunks. This keeps peak memory to 1 month × 1 strategy at a time.
    """
    from p1_data_stream import iter_months

    q05 = q_quantiles["q05"]
    q95 = q_quantiles["q95"]

    strategies_done   = set(manifest["pipeline"]["strategies_complete"])
    strategies_all    = list(strategy_registry.keys())
    strategies_todo   = [s for s in strategies_all if s not in strategies_done]

    if verbose:
        print(f"  Strategies total: {len(strategies_all)}")
        print(f"  Already complete: {len(strategies_done)}")
        print(f"  To process: {len(strategies_todo)}", flush=True)

    for i, name in enumerate(strategies_todo):
        meta = strategy_registry[name]
        if verbose:
            print(f"\n  [{i+1}/{len(strategies_todo)}] Running: {name} ({meta['family']})",
                  flush=True)
        # Open a fresh month iterator for this strategy
        month_iter = iter_months(data_dir, years=list(years),
                                 force_rebuild=False, verbose=False)
        run_strategy_incremental(
            name, meta, month_iter, manifest, q05, q95, verbose=verbose
        )
        gc.collect()
