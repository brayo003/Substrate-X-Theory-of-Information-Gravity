"""
p5_engine.py — Phase 5 Chronological Replay Engine.

Replays the FROZEN Transport Operating System on 2026 out-of-sample data.
Exactly as if the OS were running live from January 1, 2026.

FROZEN components used WITHOUT modification:
  - Allocator tables (from Phase 4 results)
  - Regime thresholds (Q05=-1.0, Q95=1.73)
  - Stop policy (ATR_STOP=1.5, ATR_TARGET=2.5)
  - Scheduler (strategy per regime per market)
  - NoTrade logic
  - Risk budget
  - HOLD_BARS, COMMISSION_RT

Architecture:
  BarState is carried continuously — no resets, no future info, no lookahead.
"""

import sys
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

_HERE = Path(__file__).resolve().parent
for p in [str(_HERE), str(_HERE / "v12_validate")]:
    if p not in sys.path:
        sys.path.insert(0, p)

# ── FROZEN Phase 2/4 constants ────────────────────────────────────────────
from p2_transport_os import (
    COMMISSION_RT,
    BASE_RISK_PCT,
    classify_q_global_p2,
    REGIMES_5,
)
from p2_execution_engine import HOLD_BARS

# ── Strategy library (signals only, no tuning) ───────────────────────────
from strategy_library import get_all_strategies
from p4_passive_liquidity import get_pl_strategies

PHASE5_DIR = _HERE / "results" / "phase5"
PHASE4_DIR = _HERE / "results" / "phase4"

# ── FROZEN execution constants (IDENTICAL to Phase 2/4) ──────────────────
Q05_FROZEN = -1.0
Q95_FROZEN =  1.73
ATR_STOP   = 1.5
ATR_TARGET = 2.5

# ── FROZEN risk allocator (from Phase 2, calibrated) ─────────────────────
FROZEN_RISK_MAP = {
    "Deep_Incoherent":  0.125,   # restored: Phase-4 confirmed PF>1 strategies exist
    "Mod_Incoherent":   0.000,
    "Transition":       0.000,
    "Weak_Coherent":    0.000,
    "Strong_Coherent":  0.250,
}

MARKET_ORDER = ["EURUSD", "BTCUSDT", "ETHUSDT", "NAS100", "XAUUSD", "USOIL", "UKOIL"]


# ═══════════════════════════════════════════════════════════════════════════
# Frozen Allocator Table (from Phase 4 results)
# ═══════════════════════════════════════════════════════════════════════════

def load_frozen_allocator() -> pd.DataFrame:
    """Load Phase 4 allocator table (frozen — this is the OS scheduler)."""
    path = PHASE4_DIR / "allocator_by_market.csv"
    if not path.exists():
        raise FileNotFoundError(f"Frozen allocator table not found: {path}")
    return pd.read_csv(path)


def build_scheduler_table(allocator_df: pd.DataFrame) -> Dict[str, Dict[str, str]]:
    """
    Build scheduler: {symbol: {regime: strategy_name}}.
    If best_strategy == NO_TRADE or regime has confidence=Weak → NoTrade.
    """
    scheduler = {}
    for _, row in allocator_df.iterrows():
        sym = row["symbol"]
        regime = row["regime"]
        best = row.get("best_strategy", "NO_TRADE")
        confidence = row.get("confidence", "Weak")

        if sym not in scheduler:
            scheduler[sym] = {}

        # NoTrade if weak confidence or explicitly NO_TRADE
        if confidence == "Weak" or best == "NO_TRADE" or pd.isna(best):
            scheduler[sym][regime] = "NO_TRADE"
        else:
            scheduler[sym][regime] = str(best)

    # Fill any missing regimes with NO_TRADE
    for sym in scheduler:
        for regime in REGIMES_5:
            if regime not in scheduler[sym]:
                scheduler[sym][regime] = "NO_TRADE"

    return scheduler


def get_frozen_strategy_registry() -> Dict[str, dict]:
    """All 34 strategies (29 base + 5 PassiveLiquidity)."""
    reg = get_all_strategies()
    reg.update(get_pl_strategies())
    return reg


# ═══════════════════════════════════════════════════════════════════════════
# Bar-by-bar replay state
# ═══════════════════════════════════════════════════════════════════════════

class FrozenOSState:
    """Carries the bar state through the entire 2026 replay."""
    def __init__(self):
        self.in_trade      = False
        self.direction     = 0
        self.entry_price   = 0.0
        self.entry_bar     = -1
        self.stop_price    = 0.0
        self.tgt_price     = 0.0
        self.entry_q       = 0.0
        self.entry_regime  = ""
        self.entry_strategy= ""
        self.equity_curve  = [0.0]
        self.cum_pnl       = 0.0
        self.n_no_trade    = 0
        self.n_bars_total  = 0


# ═══════════════════════════════════════════════════════════════════════════
# Single-market replay
# ═══════════════════════════════════════════════════════════════════════════

def replay_market_2026(
    symbol: str,
    df: pd.DataFrame,
    scheduler: Dict[str, str],
    strategy_registry: Dict[str, dict],
    verbose: bool = False,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Replay the frozen OS on one market's 2026 data bar-by-bar.

    Args:
        symbol: Market symbol
        df: Prepared 2026 DataFrame with tr_Q, regime, OHLC, indicators
        scheduler: {regime: strategy_name} for this market (frozen)
        strategy_registry: {strategy_name: {"fn": callable, "family": str}}
        verbose: Print progress

    Returns:
        (trade_log_df, bar_log_df)
        trade_log_df: one row per completed trade
        bar_log_df: one row per bar (for NoTrade%, regime occupancy, equity)
    """
    n = len(df)
    if n == 0:
        return pd.DataFrame(), pd.DataFrame()

    # Pre-compute all strategy signals (frozen computation)
    strategy_signals: Dict[str, np.ndarray] = {}
    for strat_name, meta in strategy_registry.items():
        try:
            sig = meta["fn"](df).values.astype(np.int8)
            strategy_signals[strat_name] = sig
        except Exception:
            strategy_signals[strat_name] = np.zeros(n, dtype=np.int8)

    # Arrays for fast access
    close_arr   = df["close"].values.astype(np.float64)
    high_arr    = df["high"].values.astype(np.float64)
    low_arr     = df["low"].values.astype(np.float64)
    atr_arr     = df.get("atr_14", pd.Series(np.nan, index=df.index)).values.astype(np.float64)
    q_arr       = df.get("tr_Q",   pd.Series(np.nan, index=df.index)).values.astype(np.float64)
    regime_arr  = df["regime"].values

    # Bar log lists
    bar_records = []
    trade_records = []

    state = FrozenOSState()

    for i in range(n):
        state.n_bars_total += 1

        regime  = str(regime_arr[i])
        q_val   = float(q_arr[i]) if not np.isnan(q_arr[i]) else 0.0
        c_price = float(close_arr[i])
        h_price = float(high_arr[i])
        l_price = float(low_arr[i])
        atr_val = float(atr_arr[i]) if not np.isnan(atr_arr[i]) else 0.0

        # OS decision: which strategy?
        os_strategy = scheduler.get(regime, "NO_TRADE")
        risk_frac   = FROZEN_RISK_MAP.get(regime, 0.0)

        # ── Check open trade exit ─────────────────────────────────────────
        if state.in_trade:
            elapsed = i - state.entry_bar
            stop_hit = target_hit = timeout = False
            ep = c_price

            if state.direction == 1:
                if l_price <= state.stop_price:   stop_hit   = True; ep = state.stop_price
                elif h_price >= state.tgt_price:  target_hit = True; ep = state.tgt_price
            else:
                if h_price >= state.stop_price:   stop_hit   = True; ep = state.stop_price
                elif l_price <= state.tgt_price:  target_hit = True; ep = state.tgt_price

            if elapsed >= HOLD_BARS and not stop_hit and not target_hit:
                timeout = True; ep = c_price

            if stop_hit or target_hit or timeout:
                gross = state.direction * (ep - state.entry_price) / (state.entry_price + 1e-12)
                net   = gross - COMMISSION_RT / (state.entry_price + 1e-12)
                state.cum_pnl += net
                state.equity_curve.append(state.cum_pnl)

                # Get family from registry
                entry_meta = strategy_registry.get(state.entry_strategy, {})
                entry_family = entry_meta.get("family", "Unknown")

                trade_records.append({
                    "symbol"         : symbol,
                    "entry_bar"      : state.entry_bar,
                    "exit_bar"       : i,
                    "entry_ts"       : df.index[state.entry_bar],
                    "exit_ts"        : df.index[i],
                    "regime"         : state.entry_regime,
                    "strategy"       : state.entry_strategy,
                    "family"         : entry_family,
                    "direction"      : state.direction,
                    "entry_price"    : state.entry_price,
                    "exit_price"     : ep,
                    "gross_ret"      : gross,
                    "net_ret"        : net,
                    "duration_bars"  : elapsed,
                    "stop_hit"       : stop_hit,
                    "target_hit"     : target_hit,
                    "timeout"        : timeout,
                    "entry_Q"        : state.entry_q,
                    "reason"         : "stop" if stop_hit else ("target" if target_hit else "timeout"),
                })
                state.in_trade = False

        # ── Check for new entry or reversal ──────────────────────────────
        is_no_trade = (os_strategy == "NO_TRADE" or risk_frac == 0.0)

        if not is_no_trade:
            signals = strategy_signals.get(os_strategy)
            sig = int(signals[i]) if signals is not None else 0

            if sig != 0 and atr_val > 0 and c_price > 0:
                if state.in_trade:
                    if sig == state.direction:
                        # Same direction — duplicate signal, hold existing position
                        pass
                    else:
                        # Opposite direction — reversal: close current at this bar close
                        gross = state.direction * (c_price - state.entry_price) / (state.entry_price + 1e-12)
                        net   = gross - COMMISSION_RT / (state.entry_price + 1e-12)
                        state.cum_pnl += net
                        state.equity_curve.append(state.cum_pnl)
                        entry_meta   = strategy_registry.get(state.entry_strategy, {})
                        entry_family = entry_meta.get("family", "Unknown")
                        trade_records.append({
                            "symbol"         : symbol,
                            "entry_bar"      : state.entry_bar,
                            "exit_bar"       : i,
                            "entry_ts"       : df.index[state.entry_bar],
                            "exit_ts"        : df.index[i],
                            "regime"         : state.entry_regime,
                            "strategy"       : state.entry_strategy,
                            "family"         : entry_family,
                            "direction"      : state.direction,
                            "entry_price"    : state.entry_price,
                            "exit_price"     : c_price,
                            "gross_ret"      : gross,
                            "net_ret"        : net,
                            "duration_bars"  : i - state.entry_bar,
                            "stop_hit"       : False,
                            "target_hit"     : False,
                            "timeout"        : False,
                            "entry_Q"        : state.entry_q,
                            "reason"         : "reversal",
                        })
                        state.in_trade = False
                        # Fall through: open reversed position below

                if not state.in_trade:
                    state.in_trade      = True
                    state.direction     = sig
                    state.entry_price   = c_price
                    state.entry_bar     = i
                    state.stop_price    = c_price - sig * ATR_STOP   * atr_val
                    state.tgt_price     = c_price + sig * ATR_TARGET * atr_val
                    state.entry_q       = q_val
                    state.entry_regime  = regime
                    state.entry_strategy = os_strategy

        if is_no_trade:
            state.n_no_trade += 1

        # Bar log
        bar_records.append({
            "symbol"     : symbol,
            "ts"         : df.index[i],
            "regime"     : regime,
            "q_val"      : q_val,
            "os_strategy": os_strategy,
            "risk_frac"  : risk_frac,
            "no_trade"   : is_no_trade,
            "in_trade"   : state.in_trade,
            "equity"     : state.cum_pnl,
        })

    trade_log  = pd.DataFrame(trade_records)
    bar_log    = pd.DataFrame(bar_records)

    if verbose:
        n_trades  = len(trade_log)
        no_trade_pct = 100.0 * state.n_no_trade / max(state.n_bars_total, 1)
        net_all = trade_log["net_ret"].sum() if n_trades > 0 else 0.0
        print(f"  [{symbol}] bars={state.n_bars_total} trades={n_trades} "
              f"NoTrade%={no_trade_pct:.1f}% cumPnL={net_all:.4f}", flush=True)

    return trade_log, bar_log


# ═══════════════════════════════════════════════════════════════════════════
# Full 2026 replay across all markets
# ═══════════════════════════════════════════════════════════════════════════

def run_phase5_replay(
    all_data: Dict[str, pd.DataFrame],
    markets: List[str] = None,
    verbose: bool = True,
) -> Tuple[Dict[str, pd.DataFrame], Dict[str, pd.DataFrame]]:
    """
    Run the frozen OS replay on all 2026 markets.

    Returns:
        all_trade_logs: {symbol: trade_log_df}
        all_bar_logs:   {symbol: bar_log_df}
    """
    if markets is None:
        markets = MARKET_ORDER

    PHASE5_DIR.mkdir(parents=True, exist_ok=True)

    # Load frozen allocator
    allocator_df  = load_frozen_allocator()
    scheduler_all = build_scheduler_table(allocator_df)
    registry      = get_frozen_strategy_registry()

    if verbose:
        print(f"\n  Frozen OS: {len(allocator_df)} allocator rows loaded", flush=True)
        print(f"  Strategy registry: {len(registry)} strategies", flush=True)

    all_trade_logs: Dict[str, pd.DataFrame] = {}
    all_bar_logs:   Dict[str, pd.DataFrame] = {}

    for sym in markets:
        df = all_data.get(sym)
        if df is None or len(df) == 0:
            print(f"  [{sym}] No data — skipping", flush=True)
            continue

        if verbose:
            print(f"\n  [{sym}] Replaying frozen OS on {len(df)} bars …", flush=True)

        # Get this market's frozen scheduler
        market_scheduler = scheduler_all.get(sym, {})
        # Fill missing regimes with NO_TRADE
        for r in REGIMES_5:
            if r not in market_scheduler:
                market_scheduler[r] = "NO_TRADE"

        if verbose:
            for r in REGIMES_5:
                strat = market_scheduler.get(r, "NO_TRADE")
                family = registry.get(strat, {}).get("family", "—") if strat != "NO_TRADE" else "NoTrade"
                print(f"    Frozen scheduler: {r:<20} → {strat} [{family}]", flush=True)

        trade_log, bar_log = replay_market_2026(
            symbol=sym,
            df=df,
            scheduler=market_scheduler,
            strategy_registry=registry,
            verbose=verbose,
        )

        all_trade_logs[sym] = trade_log
        all_bar_logs[sym]   = bar_log

    return all_trade_logs, all_bar_logs


def save_replay_results(
    all_trade_logs: Dict[str, pd.DataFrame],
    all_bar_logs:   Dict[str, pd.DataFrame],
):
    """Cache replay results to parquet files."""
    cache_dir = PHASE5_DIR / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    for sym, df in all_trade_logs.items():
        if len(df) > 0:
            df.to_parquet(cache_dir / f"trades_2026_{sym}.parquet", index=False)

    for sym, df in all_bar_logs.items():
        if len(df) > 0:
            df.to_parquet(cache_dir / f"barlogs_2026_{sym}.parquet", index=False)

    print(f"  Replay results cached to {cache_dir}", flush=True)


def load_cached_replay_results() -> Tuple[Dict[str, pd.DataFrame], Dict[str, pd.DataFrame]]:
    """Load cached replay results if available."""
    cache_dir = PHASE5_DIR / "cache"
    trade_logs = {}
    bar_logs   = {}

    for fp in sorted(cache_dir.glob("trades_2026_*.parquet")):
        sym = fp.stem.replace("trades_2026_", "")
        trade_logs[sym] = pd.read_parquet(fp)

    for fp in sorted(cache_dir.glob("barlogs_2026_*.parquet")):
        sym = fp.stem.replace("barlogs_2026_", "")
        bar_logs[sym] = pd.read_parquet(fp)

    return trade_logs, bar_logs


if __name__ == "__main__":
    from p5_data_loader import load_all_markets_2026
    print("Phase 5 — Engine Test")
    data = load_all_markets_2026(verbose=True)
    trade_logs, bar_logs = run_phase5_replay(data, verbose=True)
    print(f"\nReplay complete. Markets: {list(trade_logs.keys())}")
    for sym, tl in trade_logs.items():
        print(f"  {sym}: {len(tl)} trades")
