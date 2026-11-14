"""
p4_passive_liquidity.py — Transport-Aware Passive Liquidity Provision

Family: PassiveLiquidity (8th strategy family, 5 strategies)

Each strategy returns {-1, 0, +1} signals exactly like every other strategy.
The existing execution engine (COMMISSION_RT, HOLD_BARS, ATR stops) handles
them identically. Transport-awareness is only in signal generation.

Transport is IMMUTABLE. These strategies READ Q and regime; never modify them.

Strategies:
  PL_TightQuote     — aggressive quoting in Mod_Incoherent
  PL_WideQuote      — passive quoting in Deep_Incoherent
  PL_RegimeAdaptive — scale aggressiveness to |Q| magnitude
  PL_AntiAdverse    — suppress when Q trends toward coherent
  PL_InventorySkew  — skew direction by Q sign
"""

import numpy as np
import pandas as pd
from typing import Dict

REGIMES_5  = ["Deep_Incoherent","Mod_Incoherent","Transition","Weak_Coherent","Strong_Coherent"]
Q05_GLOBAL = -1.0
Q95_GLOBAL =  1.73

_PL_REGISTRY: Dict[str, dict] = {}

def _register_pl(fn):
    _PL_REGISTRY[fn.__name__] = {"fn": fn, "family": "PassiveLiquidity"}
    return fn

def get_pl_strategies() -> Dict[str, dict]:
    return dict(_PL_REGISTRY)

def _regime_vec(df: pd.DataFrame) -> pd.Series:
    if "regime" in df.columns:
        return df["regime"]
    q = df.get("tr_Q", pd.Series(np.nan, index=df.index))
    def _c(v):
        if pd.isna(v): return "Mod_Incoherent"
        if abs(v) < 0.01: return "Transition"
        if v <= Q05_GLOBAL: return "Deep_Incoherent"
        if v < 0: return "Mod_Incoherent"
        if v >= Q95_GLOBAL: return "Strong_Coherent"
        return "Weak_Coherent"
    return q.apply(_c)


@_register_pl
def PL_TightQuote(df: pd.DataFrame) -> pd.Series:
    """Tight-spread quoting in Mod_Incoherent: fade small VWAP deviations."""
    sig    = pd.Series(0, index=df.index, dtype=np.int8)
    regime = _regime_vec(df)
    close  = df["close"]
    vwap   = df.get("vwap", close.rolling(20).mean())
    atr    = df.get("atr_14", (df["high"] - df["low"]).rolling(14).mean())
    active = (regime == "Mod_Incoherent")
    sig[active & (close < vwap) & ((vwap - close) < 0.5 * atr)]  =  1
    sig[active & (close > vwap) & ((close - vwap) < 0.5 * atr)]  = -1
    return sig


@_register_pl
def PL_WideQuote(df: pd.DataFrame) -> pd.Series:
    """Wide-spread passive quoting in Deep_Incoherent: capture large moves."""
    sig    = pd.Series(0, index=df.index, dtype=np.int8)
    regime = _regime_vec(df)
    close  = df["close"]
    vwap   = df.get("vwap", close.rolling(20).mean())
    atr    = df.get("atr_14", (df["high"] - df["low"]).rolling(14).mean())
    active = (regime == "Deep_Incoherent")
    sig[active & (close < vwap) & ((vwap - close) >= 0.5*atr) & ((vwap - close) < 2.0*atr)]  =  1
    sig[active & (close > vwap) & ((close - vwap) >= 0.5*atr) & ((close - vwap) < 2.0*atr)]  = -1
    return sig


@_register_pl
def PL_RegimeAdaptive(df: pd.DataFrame) -> pd.Series:
    """Adaptive quoting: active when |Q| is moderate incoherent, not near Transition."""
    sig    = pd.Series(0, index=df.index, dtype=np.int8)
    q      = df.get("tr_Q", pd.Series(0.0, index=df.index)).fillna(0)
    regime = _regime_vec(df)
    active = regime.isin(["Deep_Incoherent","Mod_Incoherent"]) & (q.abs() > 0.1) & (q.abs() < Q95_GLOBAL)
    close  = df["close"]
    mid    = close.rolling(20).mean()
    atr    = df.get("atr_14", (df["high"] - df["low"]).rolling(14).mean())
    sig[active & (close < mid) & ((mid - close) < 1.0 * atr)]  =  1
    sig[active & (close > mid) & ((close - mid) < 1.0 * atr)]  = -1
    return sig


@_register_pl
def PL_AntiAdverse(df: pd.DataFrame) -> pd.Series:
    """Anti-adverse-selection: cancel when Q trends toward coherent (dQ>0.1 in 3 bars)."""
    sig    = pd.Series(0, index=df.index, dtype=np.int8)
    q      = df.get("tr_Q", pd.Series(0.0, index=df.index)).fillna(0)
    regime = _regime_vec(df)
    dq     = q.diff(3).fillna(0)
    active = regime.isin(["Deep_Incoherent","Mod_Incoherent"]) & (dq <= 0.1)
    close  = df["close"]
    vwap   = df.get("vwap", close.rolling(20).mean())
    atr    = df.get("atr_14", (df["high"] - df["low"]).rolling(14).mean())
    sig[active & (close < vwap) & ((vwap - close) < 1.0 * atr)]  =  1
    sig[active & (close > vwap) & ((close - vwap) < 1.0 * atr)]  = -1
    return sig


@_register_pl
def PL_InventorySkew(df: pd.DataFrame) -> pd.Series:
    """Inventory-skewed quoting: lean buy when Q<0, sell when Q>0 in incoherent state."""
    sig    = pd.Series(0, index=df.index, dtype=np.int8)
    q      = df.get("tr_Q", pd.Series(0.0, index=df.index)).fillna(0)
    regime = _regime_vec(df)
    close  = df["close"]
    mid    = close.rolling(10).mean()
    atr    = df.get("atr_14", (df["high"] - df["low"]).rolling(14).mean())
    inco   = regime.isin(["Deep_Incoherent","Mod_Incoherent"])
    sig[inco & (q < 0) & (close < mid) & ((mid - close) < 1.5 * atr)]  =  1
    sig[inco & (q > 0) & (close > mid) & ((close - mid) < 1.5 * atr)]  = -1
    return sig


def simulate_pl_inventory(trades: pd.DataFrame, max_inventory: int = 3) -> pd.DataFrame:
    """Simulate inventory position over PL trade sequence for analytics."""
    if trades is None or len(trades) == 0:
        return pd.DataFrame(columns=["timestamp","inventory","inventory_pnl","regime","Q"])
    rows = []
    inventory = 0
    for _, t in trades.iterrows():
        direction  = int(t.get("direction", 0))
        net_ret    = float(t.get("net_ret", 0))
        regime     = t.get("regime","")
        q_val      = float(t.get("entry_Q", 0)) if "entry_Q" in t else 0.0
        inventory  = max(-max_inventory, min(max_inventory, inventory + direction))
        rows.append({"timestamp": t.get("exit_ts"), "inventory": inventory,
                     "inventory_pnl": net_ret * abs(inventory),
                     "regime": regime, "Q": q_val})
    return pd.DataFrame(rows)


def compute_adverse_selection_stats(trades: pd.DataFrame, symbol: str = "") -> dict:
    """Measure adverse selection rate (stop_hit) per regime for PL strategies."""
    if trades is None or len(trades) == 0:
        return {"symbol": symbol, "adverse_selection_rate": np.nan, "n_trades": 0}
    asr = float(trades["stop_hit"].mean()) if "stop_hit" in trades.columns else np.nan
    per_regime = {}
    if "regime" in trades.columns and "stop_hit" in trades.columns:
        for r in REGIMES_5:
            sub = trades[trades["regime"] == r]
            per_regime[r] = float(sub["stop_hit"].mean()) if len(sub) > 0 else np.nan
    q_adv = np.nan
    if "entry_Q" in trades.columns and "stop_hit" in trades.columns:
        adv = trades[trades["stop_hit"] == True]
        if len(adv) > 0:
            q_adv = float(adv["entry_Q"].mean())
    return {"symbol": symbol, "adverse_selection_rate": asr,
            "q_at_adverse_events": q_adv, "regime_adverse_rate": per_regime,
            "n_trades": len(trades),
            "n_adverse": int(trades["stop_hit"].sum()) if "stop_hit" in trades.columns else 0}
