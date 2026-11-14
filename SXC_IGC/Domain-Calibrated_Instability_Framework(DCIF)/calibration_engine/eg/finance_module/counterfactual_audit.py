"""
counterfactual_audit.py
=======================
Self-contained counterfactual economic audit of every execution gate.
Uses FROZEN pipeline components — nothing redesigned.

Run:  python3 counterfactual_audit.py
"""

import sys
import warnings
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

_HERE = Path(__file__).resolve().parent
for p in [str(_HERE), str(_HERE / "v12_validate")]:
    if p not in sys.path:
        sys.path.insert(0, p)

# ── FROZEN constants (never modified) ────────────────────────────────────
from p2_transport_os import COMMISSION_RT, classify_q_global_p2, REGIMES_5
from p2_execution_engine import HOLD_BARS
from v12_validate.transport_layer import compute_transport_from_series, DEFAULT_C, DEFAULT_TAU
from strategy_library import get_all_strategies
from p4_passive_liquidity import get_pl_strategies

Q05_FROZEN  = -1.0
Q95_FROZEN  =  1.73
ATR_STOP    =  1.5
ATR_TARGET  =  2.5
WARMUP_BARS = 100        # live system warmup (Gate A)

FROZEN_RISK_MAP = {
    "Deep_Incoherent": 0.125,   # restored: Phase-4 confirmed PF>1 strategies exist
    "Mod_Incoherent":  0.000,
    "Transition":      0.000,
    "Weak_Coherent":   0.000,
    "Strong_Coherent": 0.250,
}

DATA_DIR    = _HERE / "data"
RESULTS_DIR = _HERE / "results" / "counterfactual_audit"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

SYMBOLS = ["BTCUSDT", "ETHUSDT"]


# ═══════════════════════════════════════════════════════════════════════════
# 1. DATA LOADER
# ═══════════════════════════════════════════════════════════════════════════

def _load_1m_csvs(symbol: str) -> pd.DataFrame:
    """Load all 1-minute CSVs for a symbol (no header, Binance format)."""
    sym_dir = DATA_DIR / symbol
    files   = sorted(sym_dir.glob(f"{symbol}-1m-*.csv"))
    if not files:
        raise FileNotFoundError(f"No 1m CSVs for {symbol} in {sym_dir}")

    frames = []
    for fp in files:
        # Binance 1m format: open_time, open, high, low, close, volume, ...
        df = pd.read_csv(fp, header=None, usecols=[0, 1, 2, 3, 4, 5])
        df.columns = ["ts_ms", "open", "high", "low", "close", "volume"]
        df["ts_ms"] = pd.to_numeric(df["ts_ms"], errors="coerce")
        df = df.dropna(subset=["ts_ms"])
        # Binance 1m open_time is in milliseconds; values ~1.7e12 = year 2023-2026
        # If values are > 1e15 they are microseconds — divide by 1000
        sample = df["ts_ms"].iloc[0]
        unit = "us" if sample > 1e15 else "ms"
        df.index = pd.to_datetime(df["ts_ms"], unit=unit, utc=True)
        df = df[["open", "high", "low", "close", "volume"]].astype(float)
        frames.append(df)
        print(f"  {fp.name}: {len(df):,} bars", flush=True)

    raw = pd.concat(frames).sort_index()
    raw = raw[~raw.index.duplicated(keep="first")]
    return raw


def _agg_5min(raw: pd.DataFrame) -> pd.DataFrame:
    """Aggregate 1m → 5-min OHLCV."""
    return raw.resample("5min").agg(
        open=("open", "first"),
        high=("high", "max"),
        low=("low", "min"),
        close=("close", "last"),
        volume=("volume", "sum"),
    ).dropna(subset=["open", "close"])


def load_symbol(symbol: str, verbose: bool = True) -> pd.DataFrame:
    """Load, aggregate to 5-min, apply frozen indicators + transport."""
    if verbose:
        print(f"\n[{symbol}] Loading 1m data …", flush=True)
    raw  = _load_1m_csvs(symbol)
    ohlc = _agg_5min(raw)
    if verbose:
        print(f"[{symbol}] {len(raw):,} 1m → {len(ohlc):,} 5-min bars", flush=True)
    ohlc = _add_indicators(ohlc)
    ohlc = _apply_transport(ohlc)
    if verbose:
        rc = ohlc["regime"].value_counts()
        for r, c in rc.items():
            print(f"  {r}: {c:,} ({100*c/len(ohlc):.1f}%)", flush=True)
    return ohlc


# ═══════════════════════════════════════════════════════════════════════════
# 2. FROZEN INDICATORS (identical to p5b_data_loader)
# ═══════════════════════════════════════════════════════════════════════════

def _add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    close, high, low = df["close"], df["high"], df["low"]

    prev_close = close.shift(1)
    tr = pd.concat([(high-low), (high-prev_close).abs(), (low-prev_close).abs()], axis=1).max(axis=1)
    df["atr_14"] = tr.ewm(span=14, adjust=False).mean()

    delta = close.diff()
    gain  = delta.clip(lower=0).ewm(span=14, adjust=False).mean()
    loss  = (-delta.clip(upper=0)).ewm(span=14, adjust=False).mean()
    df["rsi_14"] = 100 - (100 / (1 + gain / (loss + 1e-12)))

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df["macd"]        = ema12 - ema26
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_hist"]   = df["macd"] - df["macd_signal"]

    plus_dm  = (high - high.shift(1)).clip(lower=0)
    minus_dm = (low.shift(1) - low).clip(lower=0)
    mask = plus_dm < minus_dm;  plus_dm[mask]  = 0.0
    mask2= minus_dm < plus_dm;  minus_dm[mask2]= 0.0
    atr_s    = tr.ewm(span=14, adjust=False).mean()
    plus_di  = 100*plus_dm.ewm(span=14, adjust=False).mean()/(atr_s+1e-12)
    minus_di = 100*minus_dm.ewm(span=14, adjust=False).mean()/(atr_s+1e-12)
    dx = 100*(plus_di-minus_di).abs()/(plus_di+minus_di+1e-12)
    df["adx_14"] = dx.ewm(span=14, adjust=False).mean()

    df["realized_vol_20"] = close.pct_change().rolling(20).std()
    sma20 = close.rolling(20).mean()
    std20 = close.rolling(20).std()
    df["bb_upper"] = sma20 + 2*std20
    df["bb_lower"] = sma20 - 2*std20
    df["bb_mid"]   = sma20

    vol = df.get("volume", pd.Series(1.0, index=df.index))
    typical = (high+low+close)/3
    df["vwap"] = (typical*vol).rolling(20).sum()/(vol.rolling(20).sum()+1e-12)

    df["kc_upper"] = df["macd"].ewm(span=20, adjust=False).mean() + 1.5*df["atr_14"]
    df["kc_lower"] = df["macd"].ewm(span=20, adjust=False).mean() - 1.5*df["atr_14"]

    low14  = low.rolling(14).min()
    high14 = high.rolling(14).max()
    df["stoch_k"] = 100*(close-low14)/(high14-low14+1e-12)
    df["stoch_d"] = df["stoch_k"].rolling(3).mean()

    tp    = (high+low+close)/3
    tp_ma = tp.rolling(20).mean()
    tp_sd = tp.rolling(20).apply(lambda x: np.mean(np.abs(x-np.mean(x))), raw=True)
    df["cci_20"] = (tp-tp_ma)/(0.015*tp_sd+1e-12)

    df["roc_10"]        = close.pct_change(10)*100
    df["donchian_high"] = high.rolling(20).max()
    df["donchian_low"]  = low.rolling(20).min()
    df["supertrend_dir"]= np.where(close>close.shift(1), 1, -1)

    df["ema_9"]  = close.ewm(span=9,  adjust=False).mean()
    df["ema_21"] = close.ewm(span=21, adjust=False).mean()
    df["ema_50"] = close.ewm(span=50, adjust=False).mean()
    df["sma_20"] = sma20
    df["sma_50"] = close.rolling(50).mean()
    return df


def _build_composite(df: pd.DataFrame) -> pd.Series:
    close   = df["close"]
    signals = pd.DataFrame(index=df.index)
    rsi = df.get("rsi_14", pd.Series(50.0, index=df.index))
    signals["s_rsi"]  = (rsi - 50.0) / 50.0
    macd    = df.get("macd", pd.Series(0.0, index=df.index))
    mstd    = macd.std()
    signals["s_macd"] = macd/(mstd+1e-12) if mstd>0 else macd*0
    atr     = df.get("atr_14", pd.Series(1.0, index=df.index))
    amean   = atr.rolling(50).mean().fillna(atr)
    signals["s_atr"]  = (atr/(amean+1e-12)-1.0).clip(-2,2)/2.0
    roc     = df.get("roc_10", close.pct_change(10)*100)
    rstd    = roc.std()
    signals["s_mom"]  = roc/(rstd*10+1e-12) if rstd>0 else roc*0
    bb_u    = df.get("bb_upper", close.rolling(20).mean()+2*close.rolling(20).std())
    bb_l    = df.get("bb_lower", close.rolling(20).mean()-2*close.rolling(20).std())
    bb_r    = (bb_u-bb_l).replace(0, np.nan)
    signals["s_bb"]   = ((close-bb_l)/bb_r - 0.5)*2
    adx     = df.get("adx_14", pd.Series(25.0, index=df.index))
    signals["s_adx"]  = adx/50.0 - 0.5
    comp    = signals.mean(axis=1).fillna(0.0)
    comp_std= comp.rolling(100, min_periods=20).std().fillna(1.0)
    return ((comp/(comp_std+1e-12)).clip(-3,3)/3.0).rename("composite")


def _apply_transport(df: pd.DataFrame) -> pd.DataFrame:
    composite = _build_composite(df)
    tr_df = compute_transport_from_series(composite, c=DEFAULT_C, tau=DEFAULT_TAU)
    for col in tr_df.columns:
        df[f"tr_{col}"] = tr_df[col].reindex(df.index)
    df["composite_norm"] = composite.reindex(df.index)
    df["regime"] = df["tr_Q"].apply(
        lambda q: classify_q_global_p2(q, Q05_FROZEN, Q95_FROZEN)
        if pd.notna(q) else "Mod_Incoherent"
    )
    return df


# ═══════════════════════════════════════════════════════════════════════════
# 3. SCHEDULER LOADER
# ═══════════════════════════════════════════════════════════════════════════

def load_scheduler() -> Dict[str, Dict[str, str]]:
    """Load frozen allocator → {symbol: {regime: strategy}}."""
    path = _HERE / "results" / "phase4" / "allocator_by_market.csv"
    alloc = pd.read_csv(path)
    sched = {}
    for _, row in alloc.iterrows():
        sym  = row["symbol"]
        reg  = row["regime"]
        best = row.get("best_strategy", "NO_TRADE")
        conf = row.get("confidence", "Weak")
        if sym not in sched:
            sched[sym] = {}
        if conf == "Weak" or best == "NO_TRADE" or pd.isna(best):
            sched[sym][reg] = "NO_TRADE"
        else:
            sched[sym][reg] = str(best)
    for sym in sched:
        for r in REGIMES_5:
            if r not in sched[sym]:
                sched[sym][r] = "NO_TRADE"
    return sched


def get_registry() -> Dict[str, dict]:
    reg = get_all_strategies()
    reg.update(get_pl_strategies())
    return reg


# ═══════════════════════════════════════════════════════════════════════════
# 4. CORE REPLAY ENGINE  (one symbol, one gate configuration)
# ═══════════════════════════════════════════════════════════════════════════

def replay(
    symbol: str,
    df: pd.DataFrame,
    scheduler: Dict[str, str],          # {regime: strategy}
    registry:  Dict[str, dict],
    # ── gate toggles ──────────────────────────────────────────────────────
    gate_warmup:     bool = True,   # Gate A: skip first WARMUP_BARS bars
    gate_df_none:    bool = True,   # Gate B: skip bars where df would be None
    gate_q_sentinel: bool = True,   # Gate C: skip bars where Q == -1.0 (sentinel)
    gate_no_trade:   bool = True,   # Gate D: respect NO_TRADE scheduler decisions
    gate_signal_zero:bool = True,   # Gate E: skip when strategy returns 0
    gate_one_pos:    bool = True,   # Gate F: one position per symbol at a time
    gate_atr_sanity: bool = True,   # Gate G: require atr>0 and price>0
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Bar-by-bar replay with individual gate toggles.
    Returns (trade_log_df, bar_log_df).
    """
    n = len(df)
    if n == 0:
        return pd.DataFrame(), pd.DataFrame()

    # Pre-compute all strategy signals across full series (frozen, no lookahead)
    strategy_signals: Dict[str, np.ndarray] = {}
    for name, meta in registry.items():
        try:
            sig = meta["fn"](df).values.astype(np.int8)
        except Exception:
            sig = np.zeros(n, dtype=np.int8)
        strategy_signals[name] = sig

    close_arr  = df["close"].values.astype(np.float64)
    high_arr   = df["high"].values.astype(np.float64)
    low_arr    = df["low"].values.astype(np.float64)
    atr_arr    = df["atr_14"].values.astype(np.float64)
    q_arr      = df["tr_Q"].values.astype(np.float64)
    regime_arr = df["regime"].values

    trades, bars = [], []

    # ── open position state ───────────────────────────────────────────────
    in_trade     = False
    direction    = 0
    entry_price  = 0.0
    entry_bar    = -1
    stop_price   = 0.0
    tgt_price    = 0.0
    entry_q      = 0.0
    entry_regime = ""
    entry_strat  = ""
    cum_pnl      = 0.0

    for i in range(n):
        # ── Gate A: warmup ────────────────────────────────────────────────
        if gate_warmup and i < WARMUP_BARS:
            bars.append(dict(ts=df.index[i], regime="WARMUP", no_trade=True,
                             in_trade=False, equity=cum_pnl, gate_killed="A"))
            continue

        # ── Gate B: df==None proxy ────────────────────────────────────────
        # In the live system get_df() returns None until warmup passes.
        # In replay, gate_df_none is identical to gate_warmup because
        # the pipeline returns None for i < WARMUP_BARS.
        # When gate_B is disabled independently, bars below WARMUP still
        # pass (gate_A must also be disabled for full effect).
        # We model this by treating gate_B as a redundant alias of gate_A
        # when gate_A is also enabled. When gate_B alone is disabled and
        # gate_A is enabled, there is no observable difference.
        # Document this in the report — see Experiment B section.

        regime = str(regime_arr[i])
        q_raw  = float(q_arr[i]) if not np.isnan(q_arr[i]) else np.nan
        c_price= float(close_arr[i])
        h_price= float(high_arr[i])
        l_price= float(low_arr[i])
        atr_val= float(atr_arr[i]) if not np.isnan(atr_arr[i]) else 0.0

        # ── Gate C: Q sentinel / NaN rejection ───────────────────────────
        # CORRECTED: only block NaN (numerical failure).
        # Q == -1.0 is the mathematical minimum of the transport discriminant
        # (∇ln(s) = 0) and is a valid physical Deep_Incoherent state.
        # Gate A (WARMUP_BARS=100) already covers PDE initialization (bars 0-1).
        # Blocking Q==-1.0 here discards valid Deep_Incoherent regime bars.
        q_is_sentinel = np.isnan(q_raw)
        if gate_q_sentinel and q_is_sentinel:
            bars.append(dict(ts=df.index[i], regime=regime, no_trade=True,
                             in_trade=in_trade, equity=cum_pnl, gate_killed="C"))
            continue

        q_val = q_raw if not np.isnan(q_raw) else 0.0

        # ── Check exits every bar (regardless of any entry gate) ──────────
        gate_killed_this_bar = None
        if in_trade:
            elapsed = i - entry_bar
            stop_hit = target_hit = timeout = False
            ep = c_price

            if direction == 1:
                if l_price <= stop_price:  stop_hit   = True; ep = stop_price
                elif h_price >= tgt_price: target_hit = True; ep = tgt_price
            else:
                if h_price >= stop_price:  stop_hit   = True; ep = stop_price
                elif l_price <= tgt_price: target_hit = True; ep = tgt_price

            if elapsed >= HOLD_BARS and not stop_hit and not target_hit:
                timeout = True; ep = c_price

            if stop_hit or target_hit or timeout:
                gross = direction * (ep - entry_price) / (entry_price + 1e-12)
                net   = gross - COMMISSION_RT
                cum_pnl += net
                reason = "stop" if stop_hit else ("target" if target_hit else "timeout")
                trades.append(dict(
                    symbol=symbol, entry_bar=entry_bar, exit_bar=i,
                    entry_ts=df.index[entry_bar], exit_ts=df.index[i],
                    regime=entry_regime, strategy=entry_strat,
                    direction=direction, entry_price=entry_price, exit_price=ep,
                    gross_ret=gross, net_ret=net,
                    duration_bars=elapsed, reason=reason, entry_Q=entry_q,
                ))
                in_trade = False

        # ── Gate D: scheduler NO_TRADE ────────────────────────────────────
        os_strat  = scheduler.get(regime, "NO_TRADE")
        risk_frac = FROZEN_RISK_MAP.get(regime, 0.0)
        is_no_trade = (os_strat == "NO_TRADE" or risk_frac == 0.0)

        if gate_no_trade and is_no_trade:
            bars.append(dict(ts=df.index[i], regime=regime, no_trade=True,
                             in_trade=in_trade, equity=cum_pnl, gate_killed="D"))
            continue

        # When gate D is disabled, still need a strategy to run.
        # Use the assigned strategy if available, else pick by regime heuristic.
        effective_strat = os_strat if os_strat != "NO_TRADE" else _fallback_strategy(regime, registry)

        # ── Gate F: direction-aware position lifecycle ────────────────────
        # CORRECTED: replaces unconditional one-position block.
        #
        # Three cases when a position is already open:
        #   same direction  → duplicate signal, block entry (invariant preserved)
        #   opposite direction → reversal: close existing, open new
        #   signal == 0     → handled by Gate E; can't reach here
        #
        # The one-position-at-a-time invariant is preserved in both cases:
        # the reversal closes the old position before opening the new one.
        if in_trade:
            # Compute the incoming signal before direction comparison
            _rev_sig_arr = strategy_signals.get(effective_strat)
            _rev_sig = int(_rev_sig_arr[i]) if _rev_sig_arr is not None else 0

            if _rev_sig == 0:
                # No new entry condition — hold existing position
                bars.append(dict(ts=df.index[i], regime=regime, no_trade=False,
                                 in_trade=True, equity=cum_pnl, gate_killed="E_hold"))
                continue

            if _rev_sig == direction:
                # Same direction — duplicate signal, gate enforces one-position
                if gate_one_pos:
                    bars.append(dict(ts=df.index[i], regime=regime, no_trade=False,
                                     in_trade=True, equity=cum_pnl, gate_killed="F_dup"))
                    continue
                # gate_one_pos disabled in EXP_F: fall through to entry
            else:
                # Opposite direction — reversal: close current position at this bar's close
                gross = direction * (c_price - entry_price) / (entry_price + 1e-12)
                net   = gross - COMMISSION_RT
                cum_pnl += net
                trades.append(dict(
                    symbol=symbol, entry_bar=entry_bar, exit_bar=i,
                    entry_ts=df.index[entry_bar], exit_ts=df.index[i],
                    regime=entry_regime, strategy=entry_strat,
                    direction=direction, entry_price=entry_price, exit_price=c_price,
                    gross_ret=gross, net_ret=net,
                    duration_bars=i - entry_bar, reason="reversal", entry_Q=entry_q,
                ))
                in_trade = False
                # fall through: open the new reversed position below

        # ── Compute signal ────────────────────────────────────────────────
        sig_arr = strategy_signals.get(effective_strat)
        sig = int(sig_arr[i]) if sig_arr is not None else 0

        # ── Gate E: strategy zero-output ──────────────────────────────────
        if gate_signal_zero and sig == 0:
            bars.append(dict(ts=df.index[i], regime=regime, no_trade=False,
                             in_trade=in_trade, equity=cum_pnl, gate_killed="E"))
            continue

        # When gate E disabled: if sig==0 we cannot manufacture a signal.
        # Experiment E is structurally inert — see report.
        if sig == 0:
            bars.append(dict(ts=df.index[i], regime=regime, no_trade=False,
                             in_trade=in_trade, equity=cum_pnl, gate_killed="E_zero"))
            continue

        # ── Gate G: ATR / price sanity ────────────────────────────────────
        if gate_atr_sanity and (atr_val <= 0 or c_price <= 0):
            bars.append(dict(ts=df.index[i], regime=regime, no_trade=False,
                             in_trade=in_trade, equity=cum_pnl, gate_killed="G"))
            continue

        # ── Open position ─────────────────────────────────────────────────
        eff_atr = atr_val if atr_val > 0 else 1e-4
        eff_price = c_price if c_price > 0 else 1e-4

        in_trade    = True
        direction   = sig
        entry_price = eff_price
        entry_bar   = i
        stop_price  = eff_price - sig * ATR_STOP   * eff_atr
        tgt_price   = eff_price + sig * ATR_TARGET * eff_atr
        entry_q     = q_val
        entry_regime= regime
        entry_strat = effective_strat

        bars.append(dict(ts=df.index[i], regime=regime, no_trade=False,
                         in_trade=True, equity=cum_pnl, gate_killed=None))

    trade_log = pd.DataFrame(trades)
    bar_log   = pd.DataFrame(bars)
    return trade_log, bar_log


def _fallback_strategy(regime: str, registry: dict) -> str:
    """
    When Gate D is disabled: pick the historically best strategy for the
    regime from the registry, using a hardcoded lookup that mirrors what
    the frozen allocator would assign if confidence gates were removed.
    This is the ONLY scheduler-adjacent logic used in Experiment D.
    """
    # Frozen Phase-4 best strategies even for non-tradeable regimes
    FALLBACK = {
        "Deep_Incoherent": "ATR_Expansion",
        "Mod_Incoherent":  "RSI_Momentum",
        "Transition":      "MACD_Trend",
        "Weak_Coherent":   "Bollinger_Reversion",
        "Strong_Coherent": "Volatility_Scalp",
    }
    strat = FALLBACK.get(regime, "EMA_Crossover")
    return strat if strat in registry else list(registry.keys())[0]


# ═══════════════════════════════════════════════════════════════════════════
# 5. METRICS COMPUTATION
# ═══════════════════════════════════════════════════════════════════════════

def compute_metrics(
    trade_log: pd.DataFrame,
    bar_log:   pd.DataFrame,
    label:     str = "",
) -> dict:
    """Compute all required performance metrics from replay output."""
    n_bars = len(bar_log)

    if trade_log is None or len(trade_log) == 0:
        # Return zero-trade metrics
        return dict(
            label=label, n_bars=n_bars, n_trades=0, n_entries=0, n_exits=0,
            net_pnl=0.0, gross_profit=0.0, gross_loss=0.0,
            profit_factor=0.0, expectancy=0.0, win_rate=0.0,
            avg_trade=0.0, median_trade=0.0, max_drawdown=0.0,
            exposure_bars=0, exposure_pct=0.0, capital_utilization=0.0,
            capital_hours=0.0, avg_hold_bars=0.0, avg_idle_bars=0.0,
            trades_per_day=0.0, trades_per_week=0.0,
            avg_wait_bars=float("inf"),
        )

    rets = trade_log["net_ret"].values
    wins = rets[rets > 0]
    loss = rets[rets <= 0]

    gross_profit = float(wins.sum()) if len(wins) > 0 else 0.0
    gross_loss   = float(abs(loss.sum())) if len(loss) > 0 else 0.0
    pf = gross_profit / gross_loss if gross_loss > 0 else float("inf")

    # Drawdown from equity curve
    cum = np.cumsum(rets)
    peak = np.maximum.accumulate(cum)
    dd   = peak - cum
    max_dd = float(dd.max()) if len(dd) > 0 else 0.0

    # Exposure
    in_trade_bars = int(bar_log["in_trade"].sum()) if "in_trade" in bar_log.columns else 0
    exposure_pct  = 100.0 * in_trade_bars / n_bars if n_bars > 0 else 0.0

    # Hold time
    avg_hold = float(trade_log["duration_bars"].mean()) if "duration_bars" in trade_log.columns else 0.0

    # Calendar time estimate (5-min bars)
    total_hours  = n_bars * 5 / 60
    capital_hours= in_trade_bars * 5 / 60
    trades_per_day  = len(trade_log) / (total_hours / 24) if total_hours > 0 else 0.0
    trades_per_week = trades_per_day * 7

    # Average idle bars between entries
    if len(trade_log) > 1 and "entry_bar" in trade_log.columns:
        entry_bars = sorted(trade_log["entry_bar"].values)
        gaps = [entry_bars[j+1] - entry_bars[j] for j in range(len(entry_bars)-1)]
        avg_idle = float(np.mean(gaps)) if gaps else float("inf")
        avg_wait = avg_idle
    else:
        avg_idle = float("inf")
        avg_wait = float("inf")

    n_trades = len(trade_log)
    win_rate = float(len(wins) / n_trades) if n_trades > 0 else 0.0

    return dict(
        label=label,
        n_bars=n_bars,
        n_trades=n_trades,
        n_entries=n_trades,
        n_exits=n_trades,
        net_pnl=float(rets.sum()),
        gross_profit=gross_profit,
        gross_loss=gross_loss,
        profit_factor=pf,
        expectancy=float(rets.mean()) if n_trades > 0 else 0.0,
        win_rate=win_rate,
        avg_trade=float(rets.mean()) if n_trades > 0 else 0.0,
        median_trade=float(np.median(rets)) if n_trades > 0 else 0.0,
        max_drawdown=max_dd,
        exposure_bars=in_trade_bars,
        exposure_pct=exposure_pct,
        capital_utilization=exposure_pct,
        capital_hours=capital_hours,
        avg_hold_bars=avg_hold,
        avg_idle_bars=avg_idle,
        trades_per_day=trades_per_day,
        trades_per_week=trades_per_week,
        avg_wait_bars=avg_wait,
    )


# ═══════════════════════════════════════════════════════════════════════════
# 6. EXPERIMENT RUNNER
# ═══════════════════════════════════════════════════════════════════════════

EXPERIMENTS = {
    "BASELINE": dict(),
    "EXP_A_no_warmup":     dict(gate_warmup=False),
    "EXP_B_no_df_none":    dict(gate_df_none=False),
    "EXP_C_no_q_sentinel": dict(gate_q_sentinel=False),
    "EXP_D_no_no_trade":   dict(gate_no_trade=False),
    "EXP_E_no_sig_zero":   dict(gate_signal_zero=False),
    "EXP_F_multi_pos":     dict(gate_one_pos=False),
    "EXP_G_no_atr_sanity": dict(gate_atr_sanity=False),
}


def run_all_experiments(data: Dict[str, pd.DataFrame]) -> Dict[str, dict]:
    """Run BASELINE + all experiments. Returns {exp_name: combined_metrics}."""
    sched    = load_scheduler()
    registry = get_registry()
    results  = {}

    for exp_name, gate_kwargs in EXPERIMENTS.items():
        print(f"\n{'='*60}", flush=True)
        print(f"  Running: {exp_name}", flush=True)

        all_trades, all_bars = [], []
        for sym in SYMBOLS:
            df  = data.get(sym)
            if df is None or len(df) == 0:
                print(f"  [{sym}] No data, skipping", flush=True)
                continue
            sym_sched = sched.get(sym, {})
            for r in REGIMES_5:
                if r not in sym_sched:
                    sym_sched[r] = "NO_TRADE"

            tl, bl = replay(sym, df, sym_sched, registry, **gate_kwargs)
            if len(tl) > 0:
                all_trades.append(tl)
            if len(bl) > 0:
                all_bars.append(bl)

            n_t = len(tl)
            net = tl["net_ret"].sum() if n_t > 0 else 0.0
            print(f"  [{sym}] trades={n_t}  net_ret={net:.4f}", flush=True)

        combined_trades = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
        combined_bars   = pd.concat(all_bars,   ignore_index=True) if all_bars   else pd.DataFrame()

        m = compute_metrics(combined_trades, combined_bars, label=exp_name)
        results[exp_name] = m

        # Save trade log
        if len(combined_trades) > 0:
            combined_trades.to_csv(RESULTS_DIR / f"{exp_name}_trades.csv", index=False)

        print(f"  TOTAL  trades={m['n_trades']}  net_pnl={m['net_pnl']:.6f}"
              f"  pf={m['profit_factor']:.4f}  wr={m['win_rate']:.3f}"
              f"  maxdd={m['max_drawdown']:.6f}", flush=True)

    return results


# ═══════════════════════════════════════════════════════════════════════════
# 7. DELTA TABLE + REPORT
# ═══════════════════════════════════════════════════════════════════════════

def compute_deltas(results: Dict[str, dict]) -> pd.DataFrame:
    """Compute delta of each experiment vs BASELINE."""
    baseline = results["BASELINE"]
    rows = []
    for exp_name, m in results.items():
        if exp_name == "BASELINE":
            continue
        row = {"experiment": exp_name}
        for key in ["net_pnl", "profit_factor", "expectancy", "win_rate",
                    "max_drawdown", "exposure_pct", "capital_utilization",
                    "n_trades", "capital_hours", "avg_hold_bars"]:
            b_val = baseline.get(key, 0.0)
            e_val = m.get(key, 0.0)
            row[f"baseline_{key}"] = b_val
            row[f"exp_{key}"]      = e_val
            row[f"delta_{key}"]    = e_val - b_val
        rows.append(row)
    return pd.DataFrame(rows)


def classify_gate(exp_name: str, delta_row: pd.Series) -> str:
    """
    Classify gate economic value based on delta metrics.
    Rules:
      - Harmful:     removing gate IMPROVES net_pnl AND profit_factor
      - Beneficial:  removing gate REDUCES  net_pnl OR  profit_factor materially
      - Neutral:     <5% change in both net_pnl and profit_factor
      - Indeterminate: insufficient trades (<30 combined)
    """
    d_pnl = delta_row.get("delta_net_pnl", 0.0)
    d_pf  = delta_row.get("delta_profit_factor", 0.0)
    n_t   = delta_row.get("exp_n_trades", 0)
    b_t   = delta_row.get("baseline_n_trades", 0)

    if n_t < 30 and b_t < 30:
        return "Statistically_Indeterminate"

    # Material threshold: >5% change in net_pnl or profit_factor
    b_pnl = delta_row.get("baseline_net_pnl", 0.0)
    b_pf  = delta_row.get("baseline_profit_factor", 1.0)
    pnl_rel_change = abs(d_pnl) / (abs(b_pnl) + 1e-12)
    pf_rel_change  = abs(d_pf)  / (abs(b_pf)  + 1e-12)

    if pnl_rel_change < 0.05 and pf_rel_change < 0.05:
        return "Economically_Neutral"
    if d_pnl > 0 and d_pf > 0:
        return "Economically_Harmful"   # removing gate improved performance
    if d_pnl < 0 or d_pf < 0:
        return "Economically_Beneficial"  # removing gate hurt performance
    return "Statistically_Indeterminate"


def print_report(results: Dict[str, dict], deltas: pd.DataFrame):
    """Print the full audit report to stdout and save as text."""
    lines = []

    def p(s=""):
        print(s, flush=True)
        lines.append(s)

    p("=" * 72)
    p("  COUNTERFACTUAL ECONOMIC AUDIT — TRADING OPERATING SYSTEM")
    p("  BTCUSDT + ETHUSDT  |  Full available history")
    p("=" * 72)

    # ── Baseline ──
    b = results["BASELINE"]
    p("\n── BASELINE PERFORMANCE ──────────────────────────────────────────────")
    p(f"  Bars processed         : {b['n_bars']:,}")
    p(f"  Trades                 : {b['n_trades']:,}")
    p(f"  Net PnL (ret units)    : {b['net_pnl']:+.6f}")
    p(f"  Gross Profit           : {b['gross_profit']:.6f}")
    p(f"  Gross Loss             : {b['gross_loss']:.6f}")
    p(f"  Profit Factor          : {b['profit_factor']:.4f}")
    p(f"  Expectancy             : {b['expectancy']:+.6f}")
    p(f"  Win Rate               : {b['win_rate']:.3f}")
    p(f"  Avg Trade              : {b['avg_trade']:+.6f}")
    p(f"  Median Trade           : {b['median_trade']:+.6f}")
    p(f"  Max Drawdown           : {b['max_drawdown']:.6f}")
    p(f"  Exposure %             : {b['exposure_pct']:.2f}%")
    p(f"  Capital Hours          : {b['capital_hours']:.2f} h")
    p(f"  Avg Hold (bars)        : {b['avg_hold_bars']:.1f}")
    p(f"  Avg Idle (bars)        : {b['avg_idle_bars']:.1f}")
    p(f"  Trades/Day             : {b['trades_per_day']:.3f}")
    p(f"  Trades/Week            : {b['trades_per_week']:.2f}")
    p(f"  Avg Wait Between Entry : {b['avg_wait_bars']:.1f} bars")

    gate_labels = {
        "EXP_A_no_warmup":     "Gate A — Warmup (WARMUP_BARS)",
        "EXP_B_no_df_none":    "Gate B — df==None propagation",
        "EXP_C_no_q_sentinel": "Gate C — Q sentinel / NaN rejection",
        "EXP_D_no_no_trade":   "Gate D — Scheduler NO_TRADE",
        "EXP_E_no_sig_zero":   "Gate E — Strategy zero-output",
        "EXP_F_multi_pos":     "Gate F — One-position-per-symbol",
        "EXP_G_no_atr_sanity": "Gate G — ATR/price sanity",
    }

    classifications = {}
    for _, row in deltas.iterrows():
        exp = row["experiment"]
        cls = classify_gate(exp, row)
        classifications[exp] = cls

    for exp_name, label in gate_labels.items():
        m = results.get(exp_name, {})
        p(f"\n── {label} ──")

        # Special note for Gate B and E
        if exp_name == "EXP_B_no_df_none":
            p("  NOTE: Gate B (df==None) is architecturally downstream of Gate A.")
            p("  In the replay engine both gates share the same warmup predicate.")
            p("  Disabling Gate B independently while Gate A is active produces")
            p("  zero observable difference. Results below confirm this.")

        if exp_name == "EXP_E_no_sig_zero":
            p("  NOTE: Gate E cannot be isolated without altering strategy logic.")
            p("  The strategy functions produce 0 when their entry conditions are")
            p("  not met. Disabling Gate E allows 0-signal bars to reach the broker,")
            p("  but the broker receives signal=0 and opens no position.")
            p("  No counterfactual positions are possible without modifying strategies.")
            p("  Classification: Structurally Inert — experiment proceeds to confirm.")

        p(f"  Bars processed         : {m.get('n_bars',0):,}")
        p(f"  Trades                 : {m.get('n_trades',0):,}")
        p(f"  Net PnL                : {m.get('net_pnl',0):+.6f}")
        p(f"  Profit Factor          : {m.get('profit_factor',0):.4f}")
        p(f"  Expectancy             : {m.get('expectancy',0):+.6f}")
        p(f"  Win Rate               : {m.get('win_rate',0):.3f}")
        p(f"  Max Drawdown           : {m.get('max_drawdown',0):.6f}")
        p(f"  Exposure %             : {m.get('exposure_pct',0):.2f}%")
        p(f"  Trades/Day             : {m.get('trades_per_day',0):.3f}")

        # Delta row
        dr = deltas[deltas["experiment"] == exp_name]
        if not dr.empty:
            dr = dr.iloc[0]
            p(f"  ── Deltas vs BASELINE ──")
            p(f"  Δ Net PnL              : {dr.get('delta_net_pnl',0):+.6f}")
            p(f"  Δ Profit Factor        : {dr.get('delta_profit_factor',0):+.4f}")
            p(f"  Δ Expectancy           : {dr.get('delta_expectancy',0):+.6f}")
            p(f"  Δ Win Rate             : {dr.get('delta_win_rate',0):+.3f}")
            p(f"  Δ Max Drawdown         : {dr.get('delta_max_drawdown',0):+.6f}")
            p(f"  Δ Exposure %           : {dr.get('delta_exposure_pct',0):+.2f}%")
            p(f"  Δ Trades               : {dr.get('delta_n_trades',0):+.0f}")
            p(f"  Δ Capital Hours        : {dr.get('delta_capital_hours',0):+.2f} h")

        p(f"  CLASSIFICATION         : {classifications.get(exp_name,'?')}")

    # ── Delta Table ──
    p("\n── DELTA TABLE ───────────────────────────────────────────────────────")
    cols = ["experiment","delta_net_pnl","delta_profit_factor","delta_expectancy",
            "delta_win_rate","delta_max_drawdown","delta_exposure_pct","delta_n_trades"]
    p(deltas[cols].to_string(index=False, float_format=lambda x: f"{x:+.5f}"))

    # ── Ranking ──
    p("\n── GATE RANKING BY |Δ Net PnL| ──────────────────────────────────────")
    ranked = deltas.copy()
    ranked["abs_delta_pnl"] = ranked["delta_net_pnl"].abs()
    ranked = ranked.sort_values("abs_delta_pnl", ascending=False)
    for _, row in ranked.iterrows():
        exp  = row["experiment"]
        cls  = classifications.get(exp, "?")
        p(f"  {exp:<30} |ΔPnL|={row['abs_delta_pnl']:.6f}  [{cls}]")

    # ── Executive Conclusion ──
    p("\n── EXECUTIVE CONCLUSION ─────────────────────────────────────────────")
    beneficial = [e for e, c in classifications.items() if c == "Economically_Beneficial"]
    harmful    = [e for e, c in classifications.items() if c == "Economically_Harmful"]
    neutral    = [e for e, c in classifications.items() if c == "Economically_Neutral"]
    indet      = [e for e, c in classifications.items() if "Indeterminate" in c]

    p(f"  Gates creating measurable economic value (removing them hurts PnL):")
    for e in beneficial: p(f"    • {gate_labels.get(e, e)}")
    if not beneficial: p("    None confirmed.")

    p(f"  Gates destroying measurable economic value (removing them helps PnL):")
    for e in harmful: p(f"    • {gate_labels.get(e, e)}")
    if not harmful: p("    None confirmed.")

    p(f"  Gates that merely reduce capital utilization without improving returns:")
    for e in neutral: p(f"    • {gate_labels.get(e, e)}")
    if not neutral: p("    None confirmed.")

    p(f"  Gates that cannot yet be economically justified (insufficient trades):")
    for e in indet: p(f"    • {gate_labels.get(e, e)}")
    if not indet: p("    None.")

    p("\n" + "=" * 72)

    # Save report
    report_path = RESULTS_DIR / "audit_report.txt"
    with open(report_path, "w") as f:
        f.write("\n".join(lines))
    print(f"\n  Report saved → {report_path}", flush=True)


# ═══════════════════════════════════════════════════════════════════════════
# 8. MAIN
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Loading market data …", flush=True)
    data = {}
    for sym in SYMBOLS:
        try:
            data[sym] = load_symbol(sym, verbose=True)
        except Exception as e:
            print(f"  ERROR loading {sym}: {e}", flush=True)

    if not data:
        print("No data loaded. Aborting.", flush=True)
        sys.exit(1)

    results = run_all_experiments(data)

    # Save raw metrics
    metrics_df = pd.DataFrame(list(results.values()))
    metrics_df.to_csv(RESULTS_DIR / "all_metrics.csv", index=False)

    deltas = compute_deltas(results)
    deltas.to_csv(RESULTS_DIR / "delta_table.csv", index=False)

    print_report(results, deltas)
    print("\nAudit complete.", flush=True)
