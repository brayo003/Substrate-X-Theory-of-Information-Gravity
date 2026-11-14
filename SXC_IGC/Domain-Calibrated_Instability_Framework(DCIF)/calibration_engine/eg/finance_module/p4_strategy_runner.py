"""
p4_strategy_runner.py — Phase 4 strategy runner.

Runs all 34 strategies (29 existing + 5 PassiveLiquidity) on every market's
prepared DataFrame. Executes trades using the IDENTICAL execution engine from
Phase 2 (same COMMISSION_RT, HOLD_BARS, ATR stop/target).

Key design:
  - Loads prepared parquets from results/phase3/ (or EURUSD cache)
  - Runs each strategy independently on the full dataset
  - Splits results by regime label to get per-regime statistics
  - Streams one market at a time, then one strategy at a time
  - Caches per-market×strategy results as parquets in results/phase4/runs/

Output per (market, strategy): parquet with trade log + per-regime summary.
"""

import sys
import gc
import warnings
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

_HERE = Path(__file__).resolve().parent
for p in [str(_HERE), str(_HERE / "v12_validate")]:
    if p not in sys.path:
        sys.path.insert(0, p)

from p2_execution_engine import HOLD_BARS
from p2_transport_os import COMMISSION_RT, BASE_RISK_PCT, classify_q_global_p2
from strategy_library import get_all_strategies
from p4_passive_liquidity import get_pl_strategies

PHASE3_DIR = _HERE / "results" / "phase3"
PHASE4_DIR = _HERE / "results" / "phase4"
CACHE_DIR  = _HERE / "cache"

REGIMES_5 = ["Deep_Incoherent","Mod_Incoherent","Transition","Weak_Coherent","Strong_Coherent"]

Q05 = -1.0
Q95 =  1.73

MARKET_ORDER = ["EURUSD","BTCUSDT","ETHUSDT","XAUUSD","NAS100","USOIL","UKOIL"]

# Execution constants (IDENTICAL to Phase 2)
ATR_STOP   = 1.5
ATR_TARGET = 2.5


def get_full_registry() -> Dict[str, dict]:
    """Return all 34 strategies (29 base + 5 PassiveLiquidity)."""
    reg = get_all_strategies()
    reg.update(get_pl_strategies())
    return reg


# ═══════════════════════════════════════════════════════════════════════════
# Data loaders
# ═══════════════════════════════════════════════════════════════════════════

def load_market_df(symbol: str) -> pd.DataFrame:
    """Load prepared DataFrame for a market."""
    if symbol == "EURUSD":
        return _load_eurusd()
    path = PHASE3_DIR / f"prepared_{symbol}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Prepared parquet not found: {path}")
    df = pd.read_parquet(path)
    # Ensure regime column exists
    if "regime" not in df.columns and "tr_Q" in df.columns:
        df["regime"] = df["tr_Q"].apply(
            lambda q: classify_q_global_p2(q, Q05, Q95)
        )
    return df


def _load_eurusd() -> pd.DataFrame:
    """Concatenate EURUSD monthly cache parquets into one DataFrame."""
    files = sorted(CACHE_DIR.glob("ohlc_transport_*.parquet"))
    if not files:
        raise FileNotFoundError("No EURUSD cache parquets found")
    frames = []
    for f in files:
        chunk = pd.read_parquet(f)
        frames.append(chunk)
    df = pd.concat(frames)
    df = df[~df.index.duplicated(keep="first")]
    df = df.sort_index()
    # Add regime if missing
    if "regime" not in df.columns and "tr_Q" in df.columns:
        df["regime"] = df["tr_Q"].apply(
            lambda q: classify_q_global_p2(q, Q05, Q95)
        )
    # Add vwap proxy if missing
    if "vwap" not in df.columns:
        close = df["close"]
        vol   = df.get("volume", pd.Series(1.0, index=df.index))
        typical = (df["high"] + df["low"] + close) / 3
        df["vwap"] = (typical * vol).rolling(20).sum() / (vol.rolling(20).sum() + 1e-12)
    return df


# ═══════════════════════════════════════════════════════════════════════════
# Single-strategy execution
# ═══════════════════════════════════════════════════════════════════════════

def run_strategy_on_df(
    df: pd.DataFrame,
    strategy_name: str,
    strategy_fn,
) -> pd.DataFrame:
    """
    Execute one strategy on a prepared DataFrame bar-by-bar.
    Uses IDENTICAL execution constants from Phase 2.
    Returns trade log DataFrame.
    """
    n = len(df)
    if n == 0:
        return pd.DataFrame()

    try:
        signals = strategy_fn(df).values.astype(np.int8)
    except Exception as e:
        return pd.DataFrame()

    close  = df["close"].values
    high   = df["high"].values
    low    = df["low"].values
    atr    = df.get("atr_14", pd.Series(np.nan, index=df.index)).values
    Q_vals = df.get("tr_Q",   pd.Series(np.nan, index=df.index)).values
    regimes = df["regime"].values if "regime" in df.columns else np.array(["Mod_Incoherent"] * n)

    trades: List[dict] = []
    in_trade   = False
    direction  = 0
    entry_price= 0.0
    entry_bar  = -1
    stop_price = 0.0
    tgt_price  = 0.0
    entry_q    = 0.0
    entry_reg  = ""

    for i in range(n):
        if in_trade:
            elapsed = i - entry_bar
            h = float(high[i]); l = float(low[i]); c = float(close[i])
            stop_hit = target_hit = timeout = False

            if direction == 1:
                if l <= stop_price:   stop_hit   = True; ep = stop_price
                elif h >= tgt_price:  target_hit = True; ep = tgt_price
            else:
                if h >= stop_price:   stop_hit   = True; ep = stop_price
                elif l <= tgt_price:  target_hit = True; ep = tgt_price

            if elapsed >= HOLD_BARS and not stop_hit and not target_hit:
                timeout = True; ep = c

            if stop_hit or target_hit or timeout:
                gross = direction * (ep - entry_price) / (entry_price + 1e-12)
                net   = gross - COMMISSION_RT / (entry_price + 1e-12)
                trades.append({
                    "strategy"   : strategy_name,
                    "entry_bar"  : entry_bar,
                    "exit_bar"   : i,
                    "exit_ts"    : df.index[i],
                    "regime"     : entry_reg,
                    "direction"  : direction,
                    "entry_price": entry_price,
                    "exit_price" : ep,
                    "gross_ret"  : gross,
                    "net_ret"    : net,
                    "duration_bars": elapsed,
                    "stop_hit"   : stop_hit,
                    "target_hit" : target_hit,
                    "timeout"    : timeout,
                    "entry_Q"    : entry_q,
                })
                in_trade = False

        if not in_trade:
            sig = int(signals[i])
            if sig != 0:
                a = float(atr[i]) if not np.isnan(atr[i]) else 0.0
                c = float(close[i])
                if a > 0 and c > 0:
                    in_trade    = True
                    direction   = sig
                    entry_price = c
                    entry_bar   = i
                    stop_price  = c - sig * ATR_STOP   * a
                    tgt_price   = c + sig * ATR_TARGET * a
                    entry_q     = float(Q_vals[i]) if not np.isnan(Q_vals[i]) else 0.0
                    entry_reg   = str(regimes[i])

    return pd.DataFrame(trades) if trades else pd.DataFrame()


# ═══════════════════════════════════════════════════════════════════════════
# Per-regime trade metrics
# ═══════════════════════════════════════════════════════════════════════════

def _pf(wins, losses):
    w = wins.sum();  l = abs(losses.sum())
    return w / (l + 1e-12) if l > 0 else (99.0 if w > 0 else 0.0)


def compute_regime_metrics(trades: pd.DataFrame, symbol: str, strategy: str, family: str) -> List[dict]:
    """Break trade log by regime and compute stats for each cell."""
    if trades is None or len(trades) == 0:
        return []
    rows = []
    all_regimes = list(REGIMES_5) + ["ALL"]
    for regime in all_regimes:
        if regime == "ALL":
            sub = trades
        else:
            sub = trades[trades["regime"] == regime]
        if len(sub) == 0:
            rows.append(_empty_row(symbol, strategy, family, regime))
            continue
        rets = sub["net_ret"].dropna().values
        if len(rets) == 0:
            rows.append(_empty_row(symbol, strategy, family, regime))
            continue
        wins   = rets[rets > 0]; losses = rets[rets < 0]
        n      = len(rets)
        pf     = _pf(pd.Series(wins), pd.Series(losses))
        wr     = len(wins) / n
        expect = float(rets.mean())
        std    = float(rets.std()) if n > 1 else 1e-12
        sharpe = expect / (std + 1e-12) * np.sqrt(n)
        dstd   = float(losses.std()) if len(losses) > 1 else 1e-12
        sortino= expect / (dstd + 1e-12) * np.sqrt(n)
        equity = np.cumsum(rets)
        dd     = float((np.maximum.accumulate(equity) - equity).max()) if len(equity) > 0 else 0.0
        avg_dur= float(sub["duration_bars"].mean()) if "duration_bars" in sub.columns else 0.0
        sf     = float(sub["stop_hit"].mean())   if "stop_hit"   in sub.columns else 0.0
        tf     = float(sub["target_hit"].mean()) if "target_hit" in sub.columns else 0.0
        rows.append({
            "symbol"        : symbol,
            "strategy"      : strategy,
            "family"        : family,
            "regime"        : regime,
            "trade_count"   : n,
            "win_rate"      : wr,
            "profit_factor" : pf,
            "sharpe"        : sharpe,
            "sortino"       : sortino,
            "expectancy"    : expect,
            "total_return"  : float(equity[-1]) if len(equity) > 0 else 0.0,
            "max_drawdown"  : dd,
            "avg_duration"  : avg_dur,
            "stop_freq"     : sf,
            "target_freq"   : tf,
        })
    return rows


def _empty_row(symbol, strategy, family, regime):
    return {"symbol": symbol, "strategy": strategy, "family": family,
            "regime": regime, "trade_count": 0, "win_rate": 0.0,
            "profit_factor": 0.0, "sharpe": 0.0, "sortino": 0.0,
            "expectancy": 0.0, "total_return": 0.0, "max_drawdown": 0.0,
            "avg_duration": 0.0, "stop_freq": 0.0, "target_freq": 0.0}


# ═══════════════════════════════════════════════════════════════════════════
# Full market runner
# ═══════════════════════════════════════════════════════════════════════════

def run_all_strategies_for_market(
    symbol: str,
    verbose: bool = True,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Run all 34 strategies on one market.
    Returns (all_metrics_df, all_pl_trades_df).

    all_metrics_df: rows = (strategy × regime), columns = stats
    all_pl_trades_df: trade log for PassiveLiquidity strategies only
    """
    runs_dir = PHASE4_DIR / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    cache_path = runs_dir / f"metrics_{symbol}.parquet"
    pl_cache   = runs_dir / f"pl_trades_{symbol}.parquet"

    # Load market data
    try:
        df = load_market_df(symbol)
    except Exception as e:
        if verbose: print(f"  [{symbol}] ERROR loading: {e}")
        return pd.DataFrame(), pd.DataFrame()

    if verbose:
        print(f"  [{symbol}] {len(df)} bars, regimes: "
              + " ".join(f"{r[:4]}={v}" for r, v in df["regime"].value_counts().items()),
              flush=True)

    registry = get_full_registry()
    all_metric_rows: List[dict] = []
    pl_trade_frames: List[pd.DataFrame] = []

    for name, meta in registry.items():
        fn     = meta["fn"]
        family = meta["family"]

        trades = run_strategy_on_df(df, name, fn)
        rows   = compute_regime_metrics(trades, symbol, name, family)
        all_metric_rows.extend(rows)

        if family == "PassiveLiquidity" and len(trades) > 0:
            trades["symbol"] = symbol
            pl_trade_frames.append(trades)

        if verbose:
            n = len(trades)
            pf = rows[-1]["profit_factor"] if rows else 0.0
            print(f"    {name:<30} trades={n:>5}  PF(ALL)={pf:.3f}", flush=True)

    metrics_df  = pd.DataFrame(all_metric_rows)
    pl_trades_df= pd.concat(pl_trade_frames, ignore_index=True) if pl_trade_frames else pd.DataFrame()

    metrics_df.to_parquet(cache_path, index=False)
    if len(pl_trades_df) > 0:
        pl_trades_df.to_parquet(pl_cache, index=False)

    return metrics_df, pl_trades_df


def load_cached_metrics(symbol: str) -> Optional[pd.DataFrame]:
    path = PHASE4_DIR / "runs" / f"metrics_{symbol}.parquet"
    return pd.read_parquet(path) if path.exists() else None


def load_cached_pl_trades(symbol: str) -> Optional[pd.DataFrame]:
    path = PHASE4_DIR / "runs" / f"pl_trades_{symbol}.parquet"
    return pd.read_parquet(path) if path.exists() else None
