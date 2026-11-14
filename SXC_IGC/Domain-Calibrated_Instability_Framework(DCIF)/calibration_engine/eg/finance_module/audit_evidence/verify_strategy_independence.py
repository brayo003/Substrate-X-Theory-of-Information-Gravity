"""
audit_evidence/verify_strategy_independence.py

Confirms that every strategy in strategy_library.py generates
identical signals regardless of whether Q or T_sys are present
in the input DataFrame.

This provides evidence for the claim: "If DCIF/Substrate calculations
were removed, no observable trading behavior would change in Phase 1."

Run: python audit_evidence/verify_strategy_independence.py

Evidence for: FORENSIC_AUDIT_FINAL.md §5, END_TO_END_DATA_FLOW.md §3
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_FM   = _HERE.parent
if str(_FM) not in sys.path:
    sys.path.insert(0, str(_FM))

from strategy_library import get_all_strategies

def make_synthetic_df(n: int = 500, seed: int = 42) -> pd.DataFrame:
    """
    Build a minimal synthetic OHLC + indicators DataFrame.
    Includes Q/T_sys columns to simulate the real pipeline output.
    """
    np.random.seed(seed)
    idx   = pd.date_range("2024-01-01", periods=n, freq="5min")
    close = 1.09 + np.cumsum(np.random.normal(0, 0.0002, n))
    high  = close + np.abs(np.random.normal(0, 0.0001, n))
    low   = close - np.abs(np.random.normal(0, 0.0001, n))
    op    = close + np.random.normal(0, 0.00005, n)
    vol   = np.random.lognormal(10, 0.3, n)

    close = pd.Series(close, index=idx)
    high  = pd.Series(high,  index=idx)
    low   = pd.Series(low,   index=idx)

    df = pd.DataFrame({
        "open":  op,
        "high":  high,
        "low":   low,
        "close": close,
        "volume": vol,
    }, index=idx)

    # ATR(14)
    tr = pd.concat([
        df["high"] - df["low"],
        (df["high"] - df["close"].shift(1)).abs(),
        (df["low"]  - df["close"].shift(1)).abs()
    ], axis=1).max(axis=1)
    df["atr_14"] = tr.ewm(span=14, adjust=False).mean()

    # RSI(14)
    delta = close.diff()
    gain  = delta.clip(lower=0).ewm(span=14, adjust=False).mean()
    loss  = (-delta.clip(upper=0)).ewm(span=14, adjust=False).mean()
    df["rsi_14"] = 100 - 100 / (1 + gain / (loss + 1e-10))

    # MACD
    ema12  = pd.Series(close).ewm(span=12, adjust=False).mean()
    ema26  = pd.Series(close).ewm(span=26, adjust=False).mean()
    df["macd"]        = ema12 - ema26
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_hist"]   = df["macd"] - df["macd_signal"]

    # ADX(14)
    plus_dm  = df["high"].diff().clip(lower=0)
    minus_dm = (-df["low"].diff()).clip(lower=0)
    plus_dm  = plus_dm.where(plus_dm  > minus_dm, 0.0)
    minus_dm = minus_dm.where(minus_dm > plus_dm, 0.0)
    tr_s     = tr.ewm(span=14, adjust=False).mean()
    plus_di  = 100 * plus_dm.ewm(span=14, adjust=False).mean() / (tr_s + 1e-10)
    minus_di = 100 * minus_dm.ewm(span=14, adjust=False).mean() / (tr_s + 1e-10)
    dx       = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di + 1e-10)
    df["adx_14"] = dx.ewm(span=14, adjust=False).mean()

    # Realized vol
    log_ret = np.log(pd.Series(close) / pd.Series(close).shift(1))
    df["realized_vol_20"] = log_ret.rolling(20).std()

    # --- DCIF columns (should not affect signals) ---
    df["tr_Q"]      = np.random.uniform(-1.5, 2.5, n)  # random Q values
    df["T_sys"]     = np.random.uniform(0, 2.0, n)     # random T_sys values
    df["phase"]     = np.where(df["T_sys"] > 1.0, "FIREWALL", "NOMINAL")
    df["tr_regime"] = np.where(df["tr_Q"] > 0, 1, -1)

    return df


def main():
    print("=" * 60)
    print("Strategy Independence from Q and T_sys Verification")
    print("=" * 60)
    print()

    strategies = get_all_strategies()
    print(f"Testing {len(strategies)} strategies from strategy_library.py")
    print()

    df_with_dcif = make_synthetic_df(seed=42)

    # Build a version without DCIF columns
    df_without_dcif = df_with_dcif.drop(
        columns=["tr_Q", "T_sys", "phase", "tr_regime"],
        errors="ignore"
    )

    all_pass = True
    results = []

    for name, meta in strategies.items():
        fn = meta["fn"]
        try:
            sig_with    = fn(df_with_dcif)
            sig_without = fn(df_without_dcif)
            identical   = sig_with.equals(sig_without)
            status = "PASS" if identical else "FAIL"
            if not identical:
                all_pass = False
            results.append((name, meta["family"], status))
        except Exception as e:
            results.append((name, meta["family"], f"ERROR: {e}"))
            all_pass = False

    # Print results
    print(f"{'Strategy':<35} {'Family':<15} {'Status'}")
    print("-" * 60)
    for name, family, status in results:
        print(f"{name:<35} {family:<15} {status}")

    print()
    print(f"All {len(strategies)} strategies independent of Q/T_sys: {all_pass}")
    print()

    if all_pass:
        print("CONFIRMED: Removing Q and T_sys from the input DataFrame")
        print("produces identical signals for all 28 strategies.")
        print("The DCIF/Substrate calculations have zero causal effect")
        print("on strategy entry/exit signals in Phase 1.")
    else:
        print("WARNING: Some strategies are NOT independent of Q/T_sys.")
        print("Investigate the FAIL entries above.")

    print("=" * 60)

if __name__ == "__main__":
    main()
