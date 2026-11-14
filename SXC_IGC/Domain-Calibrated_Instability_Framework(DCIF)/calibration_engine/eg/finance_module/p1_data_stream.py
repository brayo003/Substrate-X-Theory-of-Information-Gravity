"""
p1_data_stream.py — Streaming data iterator for Phase 1 incremental pipeline.

Key design:
  - Reads one month at a time from BI5 (year 2023/2024) or chunked CSV (2025)
  - Aggregates ticks to 5-min OHLC
  - Applies the FULL existing transport pipeline (signals → composite → transport)
  - Returns a DataFrame with OHLC + all transport columns + indicators
  - Writes result to cache/ohlc_transport_YYYY_MM.parquet
  - Subsequent runs load from cache (skips recompute)

Memory behaviour: at most one month of ticks + OHLC bars in memory at a time.
A typical EUR/USD month has ~3-5M ticks → ~200k-300k rows → OHLC ~8640 5-min bars.
"""

import sys
import gc
import lzma
import struct
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Iterator, Tuple, Optional, List

import numpy as np
import pandas as pd

# ── Path setup ────────────────────────────────────────────────────────────
_HERE = Path(__file__).resolve().parent
_CE   = _HERE.parents[1]
for p in [str(_CE), str(_HERE), str(_HERE / "v12_validate")]:
    if p not in sys.path:
        sys.path.insert(0, p)

from p1_checkpoint import (
    CACHE_DIR, ensure_dirs,
    cache_path_for_month, q_series_path,
)

# ── Transport pipeline imports (IMMUTABLE) ────────────────────────────────
from v12_validate.transport_layer import (
    compute_transport_from_series,
    DEFAULT_C, DEFAULT_TAU,
)
from v12_validate.signals import build_signals_from_ticks, build_ohlc
from v12_validate.engine_runner import (
    SXCOmegaEngineStable,
    scale_signals_to_100,
    build_v12_composite,
    run_v12,
)

# ═══════════════════════════════════════════════════════════════════════════
# BI5 decoder (identical logic to loader.py, inlined for independence)
# ═══════════════════════════════════════════════════════════════════════════

_RECORD = struct.Struct(">IIIff")  # big-endian: ms, ask*1e5, bid*1e5, av, bv


def _decode_bi5(raw_bytes: bytes, year: int, month_0: int, day: int, hour: int) -> pd.DataFrame:
    if not raw_bytes:
        return pd.DataFrame()
    try:
        data = lzma.decompress(raw_bytes)
    except lzma.LZMAError:
        return pd.DataFrame()
    n = len(data) // 20
    if n == 0:
        return pd.DataFrame()
    base = datetime(year, month_0 + 1, day, hour, 0, 0, tzinfo=timezone.utc)
    rows = []
    for i in range(n):
        ms, ask_i, bid_i, av, bv = _RECORD.unpack_from(data, i * 20)
        rows.append((
            base + timedelta(milliseconds=int(ms)),
            ask_i / 1e5, bid_i / 1e5, float(av), float(bv),
        ))
    df = pd.DataFrame(rows, columns=["timestamp", "ask", "bid", "ask_vol", "bid_vol"])
    df["mid"]         = (df["ask"] + df["bid"]) / 2.0
    df["spread_pips"] = (df["ask"] - df["bid"]) * 10_000.0   # 4-decimal pips
    df["total_vol"]   = df["ask_vol"] + df["bid_vol"]
    return df


def _load_bi5_month(year_dir: Path, year: int, month_0: int) -> pd.DataFrame:
    """Load all BI5 ticks for one month (zero-based month index)."""
    month_dir = year_dir / f"{month_0:02d}"
    if not month_dir.exists():
        return pd.DataFrame()
    frames = []
    for day_dir in sorted(month_dir.iterdir()):
        if not day_dir.is_dir():
            continue
        try:
            day = int(day_dir.name)
        except ValueError:
            continue
        for bi5 in sorted(day_dir.glob("*h_ticks.bi5")):
            m = re.match(r"^(\d+)h_ticks\.bi5$", bi5.name)
            if not m:
                continue
            hour = int(m.group(1))
            try:
                raw = bi5.read_bytes()
                df = _decode_bi5(raw, year, month_0, day, hour)
                if not df.empty:
                    frames.append(df)
            except Exception:
                continue
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def _load_csv_2025_month(csv_path: Path, month_1: int) -> pd.DataFrame:
    """Load 2025 CSV rows for one calendar month (1-based)."""
    if not csv_path.exists():
        return pd.DataFrame()
    # Read in chunks to stay memory-efficient
    chunks = []
    for chunk in pd.read_csv(
        csv_path,
        parse_dates=["timestamp"],
        dtype={"ask": "float32", "bid": "float32",
               "ask_volume": "float32", "bid_volume": "float32"},
        low_memory=False,
        chunksize=500_000,
    ):
        chunk["timestamp"] = pd.to_datetime(chunk["timestamp"], utc=True, errors="coerce")
        chunk = chunk.dropna(subset=["timestamp"])
        month_mask = chunk["timestamp"].dt.month == month_1
        sub = chunk[month_mask]
        if len(sub) > 0:
            chunks.append(sub)
        # If we've passed the target month and already got data, stop early
        elif chunks and chunk["timestamp"].dt.month.iloc[-1] > month_1:
            break
    if not chunks:
        return pd.DataFrame()
    df = pd.concat(chunks, ignore_index=True)
    df.rename(columns={"ask_volume": "ask_vol", "bid_volume": "bid_vol"}, inplace=True)
    df["mid"]         = (df["ask"] + df["bid"]) / 2.0
    df["spread_pips"] = (df["ask"] - df["bid"]) * 10_000.0
    df["total_vol"]   = df["ask_vol"].fillna(0) + df["bid_vol"].fillna(0)
    return df


# ═══════════════════════════════════════════════════════════════════════════
# Transport pipeline application (per chunk)
# ═══════════════════════════════════════════════════════════════════════════

def _apply_transport_pipeline(ticks: pd.DataFrame, bar_freq: str = "5min") -> pd.DataFrame:
    """
    Apply the IMMUTABLE transport pipeline to one month of ticks.
    Returns an OHLC DataFrame augmented with transport quantities.
    """
    # Quality gate
    mask = (ticks["ask"] > 0) & (ticks["bid"] > 0) & (ticks["ask"] >= ticks["bid"])
    ticks = ticks[mask].copy()
    if len(ticks) < 100:
        return pd.DataFrame()

    # Step 1-3: OHLC + signals + composite (IMMUTABLE)
    ohlc, raw_signals, normalized_signals, composite = build_signals_from_ticks(
        ticks, freq=bar_freq
    )
    if len(ohlc) < 30:
        return pd.DataFrame()

    # Step 4: V12 engine (IMMUTABLE)
    scaled_signals, _ = scale_signals_to_100(raw_signals)
    v12_composite, _  = build_v12_composite(scaled_signals)
    v12_df            = run_v12(v12_composite)

    # Step 5: Transport layer (IMMUTABLE)
    transport_df = compute_transport_from_series(composite, c=DEFAULT_C, tau=DEFAULT_TAU)

    # Step 6: Merge
    df = ohlc.copy()
    for col in ["T_sys", "phase", "excitation"]:
        df[col] = v12_df[col].reindex(df.index)
    for col in transport_df.columns:
        df[f"tr_{col}"] = transport_df[col].reindex(df.index)
    df["composite_norm"] = composite.reindex(df.index)

    # Step 7: Technical indicators (required by strategies)
    close      = df["close"]
    high       = df["high"]
    low        = df["low"]
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

    ema12          = close.ewm(span=12, adjust=False).mean()
    ema26          = close.ewm(span=26, adjust=False).mean()
    df["macd"]     = ema12 - ema26
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_hist"]   = df["macd"] - df["macd_signal"]

    plus_dm  = high.diff().clip(lower=0)
    minus_dm = (-low.diff()).clip(lower=0)
    plus_dm  = plus_dm.where(plus_dm > minus_dm, 0.0)
    minus_dm = minus_dm.where(minus_dm > plus_dm, 0.0)
    tr_s     = tr.ewm(span=14, adjust=False).mean()
    plus_di  = 100.0 * plus_dm.ewm(span=14, adjust=False).mean() / (tr_s + 1e-10)
    minus_di = 100.0 * minus_dm.ewm(span=14, adjust=False).mean() / (tr_s + 1e-10)
    dx       = 100.0 * (plus_di - minus_di).abs() / (plus_di + minus_di + 1e-10)
    df["adx_14"] = dx.ewm(span=14, adjust=False).mean()

    log_ret           = np.log(close / close.shift(1))
    df["realized_vol_20"] = log_ret.rolling(20).std()
    df["realized_vol_5"]  = log_ret.rolling(5).std()

    vol = df["volume"].replace(0, np.nan)
    df["vol_norm"] = vol / (vol.rolling(50).mean() + 1e-10)

    return df


# ═══════════════════════════════════════════════════════════════════════════
# Month iterator — main public API
# ═══════════════════════════════════════════════════════════════════════════

def iter_months(
    data_dir: Path,
    years: List[int] = (2023, 2024, 2025),
    force_rebuild: bool = False,
    verbose: bool = True,
) -> Iterator[Tuple[int, int, pd.DataFrame]]:
    """
    Yield (year, month_1based, df) for every available month.

    If a cached parquet exists and force_rebuild=False, yields from cache.
    Otherwise builds from raw ticks, caches to disk, yields, then discards.

    Memory at peak: ~1 month ticks + 1 month OHLC bars (~400 MB worst case).
    After yield + next iteration: GC'd.
    """
    ensure_dirs()
    csv_2025 = data_dir / "2025" / "eurusd_ticks_2025.csv"

    for year in years:
        if year in (2023, 2024):
            year_dir = data_dir / str(year)
            if not year_dir.exists():
                continue
            # Discover available months from directory names
            month_dirs = sorted(
                [d for d in year_dir.iterdir() if d.is_dir()],
                key=lambda d: int(d.name) if d.name.isdigit() else 99
            )
            month_indices = sorted(set(
                int(d.name) for d in month_dirs if d.name.isdigit() and 0 <= int(d.name) <= 11
            ))
            for month_0 in month_indices:
                month_1 = month_0 + 1
                cache_p = cache_path_for_month(year, month_1)
                if cache_p.exists() and not force_rebuild:
                    if verbose:
                        print(f"  [{year}-{month_1:02d}] Loading from cache …", flush=True)
                    df = pd.read_parquet(cache_p)
                    yield year, month_1, df
                    del df
                    gc.collect()
                    continue

                if verbose:
                    print(f"  [{year}-{month_1:02d}] Building from BI5 …", flush=True)
                ticks = _load_bi5_month(year_dir, year, month_0)
                if ticks.empty:
                    if verbose:
                        print(f"    No ticks found for {year}-{month_1:02d}")
                    continue
                if verbose:
                    print(f"    {len(ticks):,} ticks", flush=True)

                df = _apply_transport_pipeline(ticks)
                del ticks
                gc.collect()

                if df.empty:
                    continue
                df.to_parquet(cache_p)
                if verbose:
                    coh = (df["tr_Q"] > 0).mean()
                    print(f"    {len(df):,} bars  Q-coherent={coh:.3f}  "
                          f"cached → {cache_p.name}", flush=True)
                yield year, month_1, df
                del df
                gc.collect()

        elif year == 2025:
            if not csv_2025.exists():
                continue
            # Discover which months are present in 2025 CSV
            # (Sample first 100k rows to find date range)
            sample = pd.read_csv(csv_2025, nrows=100_000,
                                 usecols=["timestamp"],
                                 parse_dates=["timestamp"])
            max_m = pd.to_datetime(sample["timestamp"].iloc[-1], utc=True).month
            del sample

            for month_1 in range(1, 13):
                cache_p = cache_path_for_month(year, month_1)
                if cache_p.exists() and not force_rebuild:
                    if verbose:
                        print(f"  [{year}-{month_1:02d}] Loading from cache …", flush=True)
                    df = pd.read_parquet(cache_p)
                    yield year, month_1, df
                    del df
                    gc.collect()
                    continue

                if verbose:
                    print(f"  [{year}-{month_1:02d}] Building from 2025 CSV …", flush=True)
                ticks = _load_csv_2025_month(csv_2025, month_1)
                if ticks.empty:
                    continue
                if verbose:
                    print(f"    {len(ticks):,} ticks", flush=True)

                df = _apply_transport_pipeline(ticks)
                del ticks
                gc.collect()

                if df.empty:
                    continue
                df.to_parquet(cache_p)
                if verbose:
                    coh = (df["tr_Q"] > 0).mean()
                    print(f"    {len(df):,} bars  Q-coherent={coh:.3f}  "
                          f"cached → {cache_p.name}", flush=True)
                yield year, month_1, df
                del df
                gc.collect()


def build_q_series(
    data_dir: Path,
    years: List[int] = (2023, 2024, 2025),
    force_rebuild: bool = False,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Build and cache the full Q series (timestamp + Q + regime label).
    Used to compute global quantile thresholds for 5-level regime classification.
    Returns DataFrame with columns: timestamp, Q, regime_bin (COHERENT/INCOHERENT).
    """
    q_path = q_series_path()
    if q_path.exists() and not force_rebuild:
        if verbose:
            print("  Loading cached Q series …", flush=True)
        return pd.read_parquet(q_path)

    if verbose:
        print("  Building Q series from monthly cache …", flush=True)
    frames = []
    for year, month_1, df in iter_months(data_dir, years=years, force_rebuild=False, verbose=verbose):
        sub = df[["tr_Q"]].copy()
        sub.columns = ["Q"]
        sub["year"]  = year
        sub["month"] = month_1
        frames.append(sub)
        del df
        gc.collect()

    if not frames:
        return pd.DataFrame()
    q_series = pd.concat(frames)
    q_series.sort_index(inplace=True)
    q_series.to_parquet(q_path)
    if verbose:
        print(f"  Q series: {len(q_series):,} bars  "
              f"coherent={( q_series['Q'] > 0).mean():.3f}", flush=True)
    return q_series


def compute_global_q_quantiles(q_series: pd.DataFrame) -> dict:
    """
    Compute global Q quantile thresholds for 5-level regime classification.
    These are computed once from the FULL dataset and applied consistently.
    """
    Q = q_series["Q"].dropna().values
    q05 = float(np.percentile(Q, 5))
    q95 = float(np.percentile(Q, 95))
    return {
        "q05": q05,
        "q95": q95,
        "mean_Q": float(Q.mean()),
        "std_Q":  float(Q.std()),
        "n_bars": int(len(Q)),
        "coherent_fraction": float((Q > 0).mean()),
    }


def classify_q_global(Q_arr: np.ndarray, q05: float, q95: float) -> np.ndarray:
    """
    Classify Q into 5 regimes using global quantile thresholds.

    Deep_Incoherent  : Q <= q05
    Mod_Incoherent   : q05 < Q < 0
    Transition       : |Q| < 0.01  (thin band around zero)
    Weak_Coherent    : 0 < Q < q95
    Strong_Coherent  : Q >= q95
    """
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
