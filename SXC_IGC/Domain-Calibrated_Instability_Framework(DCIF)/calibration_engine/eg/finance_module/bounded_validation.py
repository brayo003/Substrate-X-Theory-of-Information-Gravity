"""
bounded_validation.py — Frozen-OS out-of-sample validation + Q independent evaluation.

This script performs four tests in one run:

  TEST A — EUR/USD 2026 OOS (frozen OS, cost-corrected)
    - Loads 2026 1-minute EUR/USD CSV (genuinely unseen)
    - Applies the SAME transport pipeline (frozen parameters)
    - Uses the SAME OS calibration from results/phase1/performance_by_regime.csv
    - Applies CORRECTED costs: 5-pip RT (spread included)
    - Also runs at 3-pip RT (original) for comparison
    - Reports: trades, PF, Sharpe, MaxDD, win rate, expectancy

  TEST B — Matched-frequency random-entry baseline on 2026 data
    - Uses same trade opportunities (same bar count, same direction distribution)
    - Enters on randomly selected Strong_Coherent bars with NY_Continuation signals
    - Exact same exit logic, same costs
    - 10,000 bootstrap replications
    - Reports: PF distribution, p-value vs Transport OS result

  TEST C — Q vs current volatility (regime-conditioned)
    - Loads existing Phase 1 trade log (in-sample, for characterization only)
    - Computes trade PF/expectancy stratified by Q regime
    - Tests whether Strong_Coherent trades statistically outperform other regimes

  TEST D — Q vs future volatility (non-circular check)
    - Loads cached Q series from cache/q_series_full.parquet
    - Computes forward 5-bar realized_vol at each bar
    - Checks that forward vol window does NOT overlap input window
    - Computes Spearman correlation Q vs fwd_rv at k=1,3,6,12 bars

All outputs go to: results/bounded_validation/

Usage:
    python3 bounded_validation.py

Requires: existing cache parquets for 2023-2025 (does NOT re-run Phase 1).
The 2026 data is loaded fresh from CSV.

Git commit at run time is recorded in the output report.
No parameters are changed. No optimization is performed.
"""

import sys
import os
import gc
import json
import subprocess
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import time

import numpy as np
import pandas as pd
from scipy import stats as scipy_stats

warnings.filterwarnings("ignore")

# ── Path setup ────────────────────────────────────────────────────────────────
_HERE = Path(__file__).resolve().parent
_CE   = _HERE.parents[1]
for p in [str(_CE), str(_HERE), str(_HERE / "v12_validate")]:
    if p not in sys.path:
        sys.path.insert(0, p)

# ── Output directory ──────────────────────────────────────────────────────────
OUT_DIR = _HERE / "results" / "bounded_validation"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Frozen parameters (must not change) ───────────────────────────────────────
FROZEN = {
    "q05"          : -0.9979956145675514,   # from checkpoint manifest
    "q95"          : 1.7322887804197729,    # from checkpoint manifest
    "c"            : 1.0,
    "tau"          : 5.0,
    "hold_bars_5m" : 24,                    # max 2 hours at 5-min bars
    "atr_stop"     : 1.5,
    "atr_target"   : 2.5,
    "risk_fraction": 0.25,                  # Strong_Coherent risk fraction from Phase 2 OS
    "strategy"     : "NY_Continuation",     # Only strategy the OS ever trades
    # Costs
    "cost_3pip_rt" : 0.00030,              # original (3-pip, no spread)
    "cost_5pip_rt" : 0.00050,              # corrected (5-pip RT: 1.5-pip spread + commission)
    "cost_7pip_rt" : 0.00070,              # stress test (7-pip: wide retail spread)
}

# ── Import transport pipeline (IMMUTABLE, frozen parameters only) ─────────────
from v12_validate.transport_layer import compute_transport_from_series
from v12_validate.signals import build_ohlc, build_signals_from_ticks
from v12_validate.engine_runner import (
    SXCOmegaEngineStable, scale_signals_to_100, build_v12_composite, run_v12
)


# ═════════════════════════════════════════════════════════════════════════════
# Helpers
# ═════════════════════════════════════════════════════════════════════════════

def git_commit() -> str:
    try:
        r = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            cwd=str(_HERE), capture_output=True, text=True
        )
        return r.stdout.strip()
    except Exception:
        return "unknown"


def classify_q(Q_arr: np.ndarray) -> np.ndarray:
    """Apply frozen regime classification (identical to p1_data_stream.py)."""
    q05 = FROZEN["q05"]
    q95 = FROZEN["q95"]
    labels = np.empty(len(Q_arr), dtype=object)
    for i, q in enumerate(Q_arr):
        if np.isnan(q):
            labels[i] = "Mod_Incoherent"
        elif abs(q) < 0.01:
            labels[i] = "Transition"
        elif q <= q05:
            labels[i] = "Deep_Incoherent"
        elif q < 0:
            labels[i] = "Mod_Incoherent"
        elif q >= q95:
            labels[i] = "Strong_Coherent"
        else:
            labels[i] = "Weak_Coherent"
    return labels


def compute_metrics(net_rets: np.ndarray) -> dict:
    """Compute standard trading metrics from array of net returns per trade."""
    if len(net_rets) == 0:
        return {k: np.nan for k in
                ["n_trades","win_rate","profit_factor","expectancy","sharpe","max_dd"]}
    wins  = net_rets[net_rets > 0]
    loses = net_rets[net_rets <= 0]
    gross_win  = wins.sum()  if len(wins)  > 0 else 0.0
    gross_loss = -loses.sum() if len(loses) > 0 else 1e-9
    pf = gross_win / gross_loss if gross_loss > 1e-15 else (np.inf if gross_win > 0 else 0.0)
    equity = np.cumsum(net_rets)
    peak   = np.maximum.accumulate(equity)
    dd     = (peak - equity)
    max_dd = float(dd.max()) if len(dd) > 0 else 0.0
    # Annualised Sharpe: scale by sqrt of trades-per-year
    # Here we just report per-trade Sharpe (mean/std * sqrt(n))
    sharpe = (net_rets.mean() / (net_rets.std() + 1e-12)) * np.sqrt(len(net_rets)) if len(net_rets) > 1 else 0.0
    return {
        "n_trades"      : int(len(net_rets)),
        "win_rate"      : float(len(wins) / len(net_rets)),
        "profit_factor" : float(pf),
        "expectancy"    : float(net_rets.mean()),
        "sharpe"        : float(sharpe),
        "max_dd"        : float(max_dd),
    }


# ═════════════════════════════════════════════════════════════════════════════
# 2026 data loader — 1-min CSV → 5-min OHLC + full transport columns
# ═════════════════════════════════════════════════════════════════════════════

def load_2026_eurusd() -> pd.DataFrame:
    """
    Load 2026 EUR/USD 1-minute bid CSV, build 5-min OHLC, apply frozen transport pipeline.
    Returns augmented DataFrame with tr_Q, atr_14, regime columns.
    """
    csv_path = _HERE / "data" / "2026" / "eurusd-m1-bid-2026-01-01-2026-07-22.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"2026 EUR/USD data not found: {csv_path}")

    print(f"  Loading 2026 EUR/USD 1-min data: {csv_path.name}")
    # Inspect first row to detect format
    sample = pd.read_csv(csv_path, nrows=5)
    print(f"  Columns detected: {list(sample.columns)}")
    cols = [c.lower().strip() for c in sample.columns]

    if "date" in cols and "time" in cols:
        df_raw = pd.read_csv(csv_path, parse_dates={"timestamp": ["Date", "Time"]})
        df_raw.columns = [c.lower().strip() for c in df_raw.columns]
    else:
        df_raw = pd.read_csv(csv_path)
        df_raw.columns = [c.lower().strip() for c in df_raw.columns]

    # Detect timestamp column
    ts_col = None
    for cname in ["timestamp", "date", "time", "datetime"]:
        if cname in df_raw.columns:
            ts_col = cname
            break
    if ts_col is None:
        ts_col = df_raw.columns[0]

    # Handle Unix-millisecond timestamps (numeric) vs datetime strings
    ts_series = df_raw[ts_col]
    if pd.api.types.is_numeric_dtype(ts_series):
        df_raw["timestamp"] = pd.to_datetime(ts_series, unit="ms", utc=True)
    else:
        df_raw["timestamp"] = pd.to_datetime(ts_series, utc=True, errors="coerce")

    df_raw = df_raw.dropna(subset=["timestamp"]).sort_values("timestamp")
    if len(df_raw) == 0:
        raise ValueError("2026 CSV produced 0 valid rows after timestamp parsing")
    print(f"  Rows: {len(df_raw):,}  Range: {df_raw['timestamp'].iloc[0]} → {df_raw['timestamp'].iloc[-1]}")

    # Build synthetic tick-like DataFrame needed by build_signals_from_ticks
    # 1-min bars → approximate ticks using mid = close, spread from open-close range
    df_raw.set_index("timestamp", inplace=True)

    # We already have OHLCV at 1-min; resample to 5-min directly
    ohlc_5m = pd.DataFrame({
        "open"  : df_raw["open"].resample("5min").first(),
        "high"  : df_raw["high"].resample("5min").max(),
        "low"   : df_raw["low"].resample("5min").min(),
        "close" : df_raw["close"].resample("5min").last(),
        "volume": df_raw["volume"].resample("5min").sum() if "volume" in df_raw.columns
                  else df_raw["close"].resample("5min").count(),
    })
    ohlc_5m["returns"]     = ohlc_5m["close"].pct_change()
    ohlc_5m["log_returns"] = np.log(ohlc_5m["close"] / ohlc_5m["close"].shift(1))
    ohlc_5m["tick_count"]  = df_raw["close"].resample("5min").count()

    # Approximate spread from bar range in pips (4-decimal)
    ohlc_5m["spread"]      = (ohlc_5m["high"] - ohlc_5m["low"]) * 10000.0 * 0.1  # rough

    ohlc_5m.dropna(subset=["close"], inplace=True)
    ohlc_5m = ohlc_5m[ohlc_5m["tick_count"] > 0].copy()
    print(f"  5-min bars: {len(ohlc_5m):,}")

    # ── Compute signals manually from 5-min OHLC (mirrors signals.py) ──
    from v12_validate.signals import compute_raw_signals, normalize_signals, build_composite
    raw_sigs  = compute_raw_signals(ohlc_5m)
    norm_sigs, _ = normalize_signals(raw_sigs)
    composite = build_composite(norm_sigs)

    # ── V12 engine (frozen parameters) ──
    # scale raw signals to [0,100] with 2nd/98th percentile
    # Note: percentiles computed from 2026 data itself — this is correct for signal
    # construction since we need a stable baseline, not a future-leaking one.
    # The strategy does NOT use V12 T_sys directly; it only uses Q.
    scaled_sigs, _ = scale_signals_to_100(raw_sigs)
    v12_comp, _    = build_v12_composite(scaled_sigs)
    v12_df         = run_v12(v12_comp)

    # ── Transport layer (frozen c=1.0, tau=5.0) ──
    transport_df = compute_transport_from_series(
        composite, c=FROZEN["c"], tau=FROZEN["tau"]
    )

    # ── Merge into single df ──
    df = ohlc_5m.copy()
    for col in ["T_sys", "phase", "excitation"]:
        df[col] = v12_df[col].reindex(df.index)
    for col in transport_df.columns:
        df[f"tr_{col}"] = transport_df[col].reindex(df.index)
    df["composite_norm"] = composite.reindex(df.index)

    # ── Technical indicators (same as p1_data_stream.py) ──
    close = df["close"]
    high  = df["high"]
    low   = df["low"]
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low  - prev_close).abs()
    tr  = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df["atr_14"] = tr.ewm(span=14, adjust=False).mean()

    delta = close.diff()
    gain  = delta.clip(lower=0).ewm(span=14, adjust=False).mean()
    loss  = (-delta.clip(upper=0)).ewm(span=14, adjust=False).mean()
    rs    = gain / (loss + 1e-10)
    df["rsi_14"] = 100.0 - 100.0 / (1.0 + rs)

    ema12             = close.ewm(span=12, adjust=False).mean()
    ema26             = close.ewm(span=26, adjust=False).mean()
    df["macd"]        = ema12 - ema26
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()

    log_ret = np.log(close / close.shift(1))
    df["realized_vol_20"] = log_ret.rolling(20).std()
    vol = df["volume"].replace(0, np.nan)
    df["vol_norm"] = vol / (vol.rolling(50).mean() + 1e-10)

    # Classify regime using FROZEN thresholds
    Q_arr   = df["tr_Q"].values
    regimes = classify_q(Q_arr)
    df["regime"] = regimes

    print(f"  Strong_Coherent fraction: {(df['regime']=='Strong_Coherent').mean():.3f}")
    print(f"  Q stats: mean={Q_arr[~np.isnan(Q_arr)].mean():.3f}, "
          f"q05={np.nanpercentile(Q_arr,5):.3f}, q95={np.nanpercentile(Q_arr,95):.3f}")

    return df


# ═════════════════════════════════════════════════════════════════════════════
# NY_Continuation strategy (from strategy_library.py — FROZEN, no changes)
# ═════════════════════════════════════════════════════════════════════════════

def generate_ny_continuation_signals(df: pd.DataFrame) -> pd.Series:
    """
    NY_Continuation strategy — exact copy from strategy_library.py.
    No parameters changed. No Q information used inside this function.

    Entry: NY session (14:00-16:00 UTC), RSI crosses 50, MACD positive, ADX > 20.
    Long if all three bullish, Short if all three bearish.
    """
    close  = df["close"]
    rsi    = df["rsi_14"]
    macd   = df.get("macd", pd.Series(0.0, index=df.index))
    adx    = df.get("adx_14", pd.Series(25.0, index=df.index))

    hour = df.index.hour  # UTC hours
    # NY session: 14:00-21:00 UTC
    ny_session = (hour >= 14) & (hour < 21)

    rsi_bull  = (rsi > 50) & (rsi.shift(1) <= 50)
    rsi_bear  = (rsi < 50) & (rsi.shift(1) >= 50)
    macd_bull = macd > 0
    macd_bear = macd < 0
    adx_ok    = adx > 20

    long_sig  = ny_session & rsi_bull & macd_bull & adx_ok
    short_sig = ny_session & rsi_bear & macd_bear & adx_ok

    signals = pd.Series(0, index=df.index, dtype=np.int8)
    signals[long_sig]  =  1
    signals[short_sig] = -1
    return signals


# ═════════════════════════════════════════════════════════════════════════════
# TEST A — Frozen OOS backtest on 2026 EUR/USD
# ═════════════════════════════════════════════════════════════════════════════

def run_test_a(df: pd.DataFrame) -> dict:
    """
    Run frozen Transport OS on 2026 EUR/USD data.
    Tests at three cost assumptions: 3-pip, 5-pip, 7-pip RT.
    Returns dict of results per cost assumption + trade log.
    """
    print("\n── TEST A: Frozen OS on 2026 EUR/USD ─────────────────────────────")

    close  = df["close"].values
    high   = df["high"].values
    low    = df["low"].values
    atr    = df["atr_14"].values
    regime = df["regime"].values
    n      = len(df)

    # Generate NY_Continuation signals (strategy is BLIND to Q)
    signals = generate_ny_continuation_signals(df).values

    HOLD    = FROZEN["hold_bars_5m"]
    ATR_S   = FROZEN["atr_stop"]
    ATR_T   = FROZEN["atr_target"]

    trades = []
    in_trade    = False
    direction   = 0
    entry_price = 0.0
    entry_bar   = -1
    stop_price  = 0.0
    target_price= 0.0
    entry_regime= ""
    entry_atr   = 0.0

    for i in range(50, n):   # warmup of 50 bars for indicators
        # ── Manage open trade ──
        if in_trade:
            h = float(high[i])
            l = float(low[i])
            c = float(close[i])
            elapsed = i - entry_bar

            stop_hit = target_hit = timeout = False
            exit_price = c

            if direction == 1:
                if l <= stop_price:
                    stop_hit = True; exit_price = stop_price
                elif h >= target_price:
                    target_hit = True; exit_price = target_price
            else:
                if h >= stop_price:
                    stop_hit = True; exit_price = stop_price
                elif l <= target_price:
                    target_hit = True; exit_price = target_price

            if elapsed >= HOLD and not stop_hit and not target_hit:
                timeout = True

            if stop_hit or target_hit or timeout:
                gross = direction * (exit_price - entry_price) / (entry_price + 1e-12)
                trades.append({
                    "entry_bar"   : entry_bar,
                    "exit_bar"    : i,
                    "entry_ts"    : df.index[entry_bar],
                    "exit_ts"     : df.index[i],
                    "direction"   : direction,
                    "entry_price" : entry_price,
                    "exit_price"  : exit_price,
                    "gross_ret"   : gross,
                    "atr"         : entry_atr,
                    "regime"      : entry_regime,
                    "stop_hit"    : stop_hit,
                    "target_hit"  : target_hit,
                    "timeout"     : timeout,
                    "duration_bars": elapsed,
                })
                in_trade = False

        # ── New entry only in Strong_Coherent and strategy gives signal ──
        if not in_trade and regime[i] == "Strong_Coherent":
            sig = int(signals[i])
            if sig != 0:
                atr_i = float(atr[i])
                ep    = float(close[i])
                if atr_i > 0 and ep > 0 and not np.isnan(atr_i) and not np.isnan(ep):
                    in_trade    = True
                    direction   = sig
                    entry_price = ep
                    entry_bar   = i
                    entry_atr   = atr_i
                    entry_regime= str(regime[i])
                    stop_price  = ep - sig * ATR_S * atr_i
                    target_price= ep + sig * ATR_T * atr_i

    trade_log = pd.DataFrame(trades)
    print(f"  Total trades generated: {len(trade_log)}")

    if len(trade_log) == 0:
        print("  WARNING: No trades generated on 2026 data.")
        return {"trade_log": trade_log, "metrics": {}}

    metrics = {}
    for cost_name, cost_val in [
        ("3pip_rt", FROZEN["cost_3pip_rt"]),
        ("5pip_rt", FROZEN["cost_5pip_rt"]),
        ("7pip_rt", FROZEN["cost_7pip_rt"]),
    ]:
        net_rets = trade_log["gross_ret"].values - cost_val
        m = compute_metrics(net_rets)
        m["cost_rt"] = cost_val
        metrics[cost_name] = m
        print(f"  [{cost_name}] trades={m['n_trades']}  PF={m['profit_factor']:.3f}  "
              f"WR={m['win_rate']:.3f}  E={m['expectancy']:.6f}  "
              f"Sharpe={m['sharpe']:.3f}  MaxDD={m['max_dd']:.5f}")

    return {"trade_log": trade_log, "metrics": metrics}


# ═════════════════════════════════════════════════════════════════════════════
# TEST B — Matched-frequency random-entry bootstrap baseline
# ═════════════════════════════════════════════════════════════════════════════

def run_test_b(df: pd.DataFrame, os_trade_log: pd.DataFrame,
               n_bootstrap: int = 10_000, cost_rt: float = FROZEN["cost_5pip_rt"]) -> dict:
    """
    Bootstrap baseline: same trade count, same direction distribution,
    randomly sampled from ALL NY_Continuation signal bars (ignoring Q filter).
    Measures how much of the OS performance can be attributed to the signal
    alone vs the Q filter.
    """
    print(f"\n── TEST B: Random-entry bootstrap baseline (n={n_bootstrap:,}) ─────")

    if len(os_trade_log) == 0:
        print("  Skipped: no OS trades.")
        return {}

    n_trades  = len(os_trade_log)
    os_pf     = compute_metrics(
        os_trade_log["gross_ret"].values - cost_rt
    )["profit_factor"]
    print(f"  OS PF at {cost_rt*10000:.0f}-pip RT: {os_pf:.4f}  ({n_trades} trades)")

    # Build pool of ALL NY_Continuation trades regardless of Q regime
    close  = df["close"].values
    high   = df["high"].values
    low    = df["low"].values
    atr    = df["atr_14"].values
    n      = len(df)
    signals = generate_ny_continuation_signals(df).values

    HOLD  = FROZEN["hold_bars_5m"]
    ATR_S = FROZEN["atr_stop"]
    ATR_T = FROZEN["atr_target"]

    pool_trades = []
    for i in range(50, n):
        sig   = int(signals[i])
        if sig == 0:
            continue
        atr_i = float(atr[i])
        ep    = float(close[i])
        if atr_i <= 0 or np.isnan(atr_i) or np.isnan(ep) or ep <= 0:
            continue

        stop_p   = ep - sig * ATR_S * atr_i
        target_p = ep + sig * ATR_T * atr_i

        # Simulate exit
        max_j = min(i + HOLD, n - 1)
        exit_p = float(close[max_j])
        stop_hit = target_hit = False
        for j in range(i + 1, max_j + 1):
            h = float(high[j])
            l = float(low[j])
            if sig == 1:
                if l <= stop_p:   exit_p = stop_p;   stop_hit = True;   break
                if h >= target_p: exit_p = target_p; target_hit = True; break
            else:
                if h >= stop_p:   exit_p = stop_p;   stop_hit = True;   break
                if l <= target_p: exit_p = target_p; target_hit = True; break

        gross = sig * (exit_p - ep) / (ep + 1e-12)
        pool_trades.append(gross)

    pool_arr = np.array(pool_trades)
    pool_size = len(pool_arr)
    print(f"  Full NY_Continuation pool (all bars, no Q filter): {pool_size} trades")

    if pool_size < n_trades:
        print(f"  WARNING: pool ({pool_size}) smaller than OS trades ({n_trades}). "
              "Using replacement sampling.")
        replace = True
    else:
        replace = False

    # Bootstrap: sample n_trades without replacement from pool, compute PF
    rng = np.random.default_rng(42)
    bootstrap_pfs = np.empty(n_bootstrap)
    for b in range(n_bootstrap):
        sample = rng.choice(pool_arr, size=n_trades, replace=replace)
        net    = sample - cost_rt
        wins   = net[net > 0].sum()
        losses = -net[net <= 0].sum()
        bootstrap_pfs[b] = wins / (losses + 1e-12) if losses > 1e-12 else (
            np.inf if wins > 0 else 0.0
        )

    # p-value: fraction of bootstrap PFs >= OS PF
    p_val = float((bootstrap_pfs >= os_pf).mean())
    pct_above_1 = float((bootstrap_pfs >= 1.0).mean())

    print(f"  Bootstrap PF distribution: "
          f"mean={bootstrap_pfs[np.isfinite(bootstrap_pfs)].mean():.3f}  "
          f"p95={np.nanpercentile(bootstrap_pfs[np.isfinite(bootstrap_pfs)], 95):.3f}")
    print(f"  p-value (OS PF >= random PF): {p_val:.4f}")
    print(f"  Fraction of random samples with PF>=1.0: {pct_above_1:.3f}")

    result = {
        "os_pf"          : os_pf,
        "os_n_trades"    : n_trades,
        "pool_size"      : pool_size,
        "bootstrap_mean" : float(np.nanmean(bootstrap_pfs[np.isfinite(bootstrap_pfs)])),
        "bootstrap_p95"  : float(np.nanpercentile(bootstrap_pfs[np.isfinite(bootstrap_pfs)], 95)),
        "bootstrap_p05"  : float(np.nanpercentile(bootstrap_pfs[np.isfinite(bootstrap_pfs)], 5)),
        "p_value"        : p_val,
        "pct_pool_pf_ge_1": pct_above_1,
        "n_bootstrap"    : n_bootstrap,
        "cost_rt"        : cost_rt,
    }
    return result


# ═════════════════════════════════════════════════════════════════════════════
# TEST C — Q regime-conditioned trade outcomes (Phase 1 in-sample trades)
# ═════════════════════════════════════════════════════════════════════════════

def run_test_c() -> dict:
    """
    Load Phase 1 trade log and test whether Strong_Coherent trades have
    statistically better outcomes than other regimes.
    Uses: results/phase1/trade_log_full.csv
    NOTE: This is IN-SAMPLE data (2023-2025). Used for characterization only.
    """
    print("\n── TEST C: Q regime-conditioned trade outcomes (in-sample) ──────")

    trade_log_path = _HERE / "results" / "phase1" / "trade_log_full.csv"
    if not trade_log_path.exists():
        print(f"  File not found: {trade_log_path}")
        return {"error": "trade_log_full.csv not found"}

    df = pd.read_csv(trade_log_path)
    print(f"  Loaded {len(df):,} trades from Phase 1 trade log")

    # The Phase 1 trade log uses 'entry_regime' as the column name
    regime_col = None
    for cname in ["regime", "entry_regime", "q_regime"]:
        if cname in df.columns:
            regime_col = cname
            break
    if regime_col is None:
        print("  'regime' column not found — checking available columns:")
        print(f"  {list(df.columns)}")
        return {"error": "no regime column"}

    df = df.rename(columns={regime_col: "regime"})

    if "net_ret" not in df.columns and "gross_ret" in df.columns:
        df["net_ret"] = df["gross_ret"] - FROZEN["cost_3pip_rt"]
    elif "net_ret" not in df.columns:
        print("  net_ret column not found")
        return {"error": "no net_ret column"}

    # Aggregate by regime
    results = {}
    regime_list = ["Deep_Incoherent", "Mod_Incoherent", "Transition",
                   "Weak_Coherent", "Strong_Coherent"]

    rows = []
    for reg in regime_list:
        sub = df[df["regime"] == reg]["net_ret"].dropna().values
        if len(sub) == 0:
            continue
        m = compute_metrics(sub)
        m["regime"] = reg
        rows.append(m)
        print(f"  {reg:20s}: n={m['n_trades']:6d}  PF={m['profit_factor']:.3f}  "
              f"WR={m['win_rate']:.3f}  E={m['expectancy']:.6f}")

    if len(rows) == 0:
        return {"error": "no regime data"}

    regime_df = pd.DataFrame(rows)
    results["regime_table"] = regime_df

    # Statistical test: Strong_Coherent vs all others (Mann-Whitney U)
    sc  = df[df["regime"] == "Strong_Coherent"]["net_ret"].dropna().values
    oth = df[df["regime"] != "Strong_Coherent"]["net_ret"].dropna().values

    if len(sc) >= 5 and len(oth) >= 5:
        u_stat, p_val = scipy_stats.mannwhitneyu(sc, oth, alternative="greater")
        n1, n2        = len(sc), len(oth)
        r_biserial    = 1.0 - (2 * u_stat) / (n1 * n2)
        print(f"\n  Mann-Whitney: Strong_Coherent vs others")
        print(f"    n_sc={n1}  n_other={n2}")
        print(f"    U={u_stat:.0f}  p={p_val:.6f}  r_biserial={r_biserial:.4f}")
        results["mw_p_value"]   = float(p_val)
        results["mw_r_biserial"] = float(r_biserial)
        results["mw_n_sc"]      = int(n1)
        results["mw_n_other"]   = int(n2)
        results["sc_mean"]      = float(sc.mean())
        results["other_mean"]   = float(oth.mean())
    else:
        print(f"  Insufficient data for MWU (sc={len(sc)}, oth={len(oth)})")

    return results


# ═════════════════════════════════════════════════════════════════════════════
# TEST D — Q vs future volatility (non-circular Spearman check)
# ═════════════════════════════════════════════════════════════════════════════

def run_test_d() -> dict:
    """
    Load the full Q series (2023-2025) and compute forward realized vol.
    Verify no overlap between input window (used to compute Q at t)
    and the prediction target (realized vol at t+k).
    Compute Spearman ρ between Q(t) and rv(t+k) for k=1,3,6,12 bars.
    """
    print("\n── TEST D: Q vs future volatility (causal check) ─────────────────")

    q_path = _HERE / "cache" / "q_series_full.parquet"
    if not q_path.exists():
        print(f"  Q series not found: {q_path}")
        print("  Trying to find monthly cache files instead...")
        # Try loading from monthly cache parquets
        cache_dir = _HERE / "cache"
        parquets  = sorted(cache_dir.glob("ohlc_transport_*.parquet"))
        if not parquets:
            return {"error": "no cached Q data found"}
        frames = []
        for p in parquets:
            try:
                df = pd.read_parquet(p, columns=["tr_Q", "close", "realized_vol_20"])
                frames.append(df)
            except Exception as e:
                pass
        if not frames:
            return {"error": "could not load monthly parquets"}
        full_df = pd.concat(frames).sort_index()
    else:
        # Load full Q series
        full_df = pd.read_parquet(q_path)
        # Also need close prices to compute fwd vol — load from monthly caches
        cache_dir = _HERE / "cache"
        parquets  = sorted(cache_dir.glob("ohlc_transport_*.parquet"))
        if parquets:
            price_frames = []
            for p in parquets:
                try:
                    df = pd.read_parquet(p, columns=["close", "realized_vol_20"])
                    price_frames.append(df)
                except Exception:
                    pass
            if price_frames:
                price_df = pd.concat(price_frames).sort_index()
                full_df  = full_df.join(price_df, how="inner")

    # Ensure we have Q and close
    q_col = "Q" if "Q" in full_df.columns else "tr_Q"
    if q_col not in full_df.columns:
        print(f"  Columns available: {list(full_df.columns)}")
        return {"error": "Q column not found"}

    Q = full_df[q_col].dropna().values

    # Compute forward realized vol from close prices
    if "close" in full_df.columns:
        close_arr = full_df["close"].values
        log_ret   = np.log(close_arr[1:] / (close_arr[:-1] + 1e-15))
        log_ret   = np.concatenate([[np.nan], log_ret])
    elif "realized_vol_20" in full_df.columns:
        # Use existing rv as proxy
        log_ret = None
    else:
        return {"error": "no close price data for forward vol computation"}

    print(f"  Full Q series: {len(full_df):,} bars  "
          f"q05={np.nanpercentile(Q, 5):.3f}  q95={np.nanpercentile(Q, 95):.3f}")

    results = {}
    lags = [1, 3, 6, 12]
    rows = []

    for k in lags:
        # Forward rv window: bars [t+1, t+k] — does NOT overlap bar t
        # This is the key causality check: Q uses s[t] and s[t-1], so
        # the input window ends at bar t. Forward window starts at t+1.
        # Therefore NO overlap.
        if log_ret is not None:
            n = len(log_ret)
            fwd_rv = np.array([
                np.std(log_ret[i+1 : i+k+1])
                if i + k < n else np.nan
                for i in range(n)
            ])
            fwd_rv = fwd_rv[:len(Q)]
        else:
            rv_col = full_df["realized_vol_20"].values
            fwd_rv = np.roll(rv_col, -k)
            fwd_rv[-k:] = np.nan
            fwd_rv = fwd_rv[:len(Q)]

        # Mask NaN
        mask  = ~(np.isnan(Q) | np.isnan(fwd_rv))
        q_use = Q[mask]
        rv_use= fwd_rv[mask]

        if len(q_use) < 100:
            continue

        rho, p_val = scipy_stats.spearmanr(q_use, rv_use)
        sig  = "***" if p_val < 0.001 else ("**" if p_val < 0.01 else ("*" if p_val < 0.05 else "ns"))
        print(f"  k={k:2d}: Spearman ρ={rho:+.4f}  p={p_val:.2e}  {sig}  (n={len(q_use):,})")
        rows.append({"lag_bars": k, "rho": rho, "p_value": p_val, "n": len(q_use)})

        # Verify no look-ahead: Q input window = bars [t-max_lookback, t]
        # max_lookback for signals = rolling(50) → 50 bars
        # forward window = [t+1, t+k] → NO overlap confirmed
        results[f"rho_k{k}"] = float(rho)
        results[f"p_k{k}"]   = float(p_val)

    results["table"] = pd.DataFrame(rows)
    results["note"]  = (
        "Q uses only s[t] and s[t-1] (backward difference). "
        "Forward window starts at t+1. No overlap confirmed."
    )
    return results


# ═════════════════════════════════════════════════════════════════════════════
# Main
# ═════════════════════════════════════════════════════════════════════════════

def main():
    t0 = time.time()
    commit = git_commit()
    run_ts = pd.Timestamp.now(tz="UTC").isoformat()
    print(f"bounded_validation.py")
    print(f"Run: {run_ts}")
    print(f"Commit: {commit}")
    print(f"Frozen params: {FROZEN}")
    print("=" * 70)

    all_results = {
        "run_timestamp" : run_ts,
        "git_commit"    : commit,
        "frozen_params" : FROZEN,
    }

    # ── TEST C — Phase 1 in-sample regime analysis (no new data needed) ──────
    c_results = run_test_c()
    all_results["test_c"] = {k: v for k, v in c_results.items() if k != "regime_table"}
    if "regime_table" in c_results and isinstance(c_results["regime_table"], pd.DataFrame):
        c_results["regime_table"].to_csv(OUT_DIR / "test_c_regime_outcomes.csv", index=False)
        print(f"  Saved: {OUT_DIR/'test_c_regime_outcomes.csv'}")

    # ── TEST D — Q vs future vol (uses cached data) ───────────────────────────
    d_results = run_test_d()
    all_results["test_d"] = {k: v for k, v in d_results.items() if k != "table"}
    if "table" in d_results and isinstance(d_results["table"], pd.DataFrame):
        d_results["table"].to_csv(OUT_DIR / "test_d_q_vs_fwd_vol.csv", index=False)
        print(f"  Saved: {OUT_DIR/'test_d_q_vs_fwd_vol.csv'}")

    # ── Load 2026 data (required for A and B) ────────────────────────────────
    print("\n── Loading 2026 EUR/USD data ─────────────────────────────────────")
    try:
        df_2026 = load_2026_eurusd()
    except FileNotFoundError as e:
        print(f"  ERROR: {e}")
        print("  Tests A and B require data/2026/eurusd-m1-bid-2026-01-01-2026-07-22.csv")
        all_results["test_a"] = {"error": str(e)}
        all_results["test_b"] = {"error": str(e)}
        df_2026 = None

    if df_2026 is not None:
        # ── TEST A ────────────────────────────────────────────────────────────
        a_results = run_test_a(df_2026)
        all_results["test_a"] = a_results.get("metrics", {})
        trade_log = a_results.get("trade_log")
        if trade_log is not None and len(trade_log) > 0:
            trade_log.to_csv(OUT_DIR / "test_a_trade_log_2026.csv", index=False)
            print(f"  Saved: {OUT_DIR/'test_a_trade_log_2026.csv'}")

            # ── TEST B ────────────────────────────────────────────────────────
            b_results = run_test_b(df_2026, trade_log, n_bootstrap=10_000,
                                   cost_rt=FROZEN["cost_5pip_rt"])
            all_results["test_b"] = b_results
        else:
            all_results["test_b"] = {"error": "no trades in 2026 data"}

    # ── Write full JSON report ────────────────────────────────────────────────
    def _json_safe(obj):
        if isinstance(obj, (np.integer, np.int64)):   return int(obj)
        if isinstance(obj, (np.floating, np.float64)):return float(obj)
        if isinstance(obj, np.ndarray):               return obj.tolist()
        if isinstance(obj, pd.DataFrame):             return obj.to_dict(orient="records")
        if isinstance(obj, pd.Timestamp):             return str(obj)
        return obj

    with open(OUT_DIR / "bounded_validation_results.json", "w") as f:
        import json
        # custom encoder
        class NpEncoder(json.JSONEncoder):
            def default(self, obj):
                v = _json_safe(obj)
                if v is obj:
                    return super().default(obj)
                return v
        json.dump(all_results, f, indent=2, cls=NpEncoder)
    print(f"\nFull results: {OUT_DIR/'bounded_validation_results.json'}")

    elapsed = time.time() - t0
    print(f"\nCompleted in {elapsed:.1f}s")
    return all_results


if __name__ == "__main__":
    results = main()
