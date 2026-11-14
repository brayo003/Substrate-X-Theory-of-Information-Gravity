"""
loader.py — EUR/USD historical data loader.

Reads:
  - 2023/ and 2024/ BI5 directories (LZMA-compressed, big-endian >IIIff)
  - 2025/ flat CSV

Month directories are zero-based (00 = January, 11 = December).
All timestamps returned in UTC.
"""

import lzma
import struct
import os
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------
# BI5 decoder
# ---------------------------------------------------------------------------

def _decode_bi5(raw_bytes: bytes, year: int, month_0based: int, day: int, hour: int) -> pd.DataFrame:
    """Decompress and decode a single BI5 file into a DataFrame."""
    if len(raw_bytes) == 0:
        return pd.DataFrame()
    try:
        data = lzma.decompress(raw_bytes)
    except lzma.LZMAError:
        return pd.DataFrame()

    n_ticks = len(data) // 20
    if n_ticks == 0:
        return pd.DataFrame()

    # Dukascopy BI5 record (big-endian, 20 bytes per tick):
    #   bytes  0- 3  : uint32  ms since start of hour
    #   bytes  4- 7  : uint32  ask * 100000
    #   bytes  8-11  : uint32  bid * 100000
    #   bytes 12-15  : float32 ask volume
    #   bytes 16-19  : float32 bid volume
    RECORD = struct.Struct('>IIIff')   # 20 bytes, mixed int/float
    rows = []
    base_dt = datetime(year, month_0based + 1, day, hour, 0, 0, tzinfo=timezone.utc)
    for i in range(n_ticks):
        ms, ask_i, bid_i, av, bv = RECORD.unpack_from(data, i * 20)
        ask = ask_i / 100_000.0
        bid = bid_i / 100_000.0
        ts  = base_dt + timedelta(milliseconds=ms)
        rows.append((ts, ask, bid, av, bv))

    df = pd.DataFrame(rows, columns=['timestamp', 'ask', 'bid', 'ask_vol', 'bid_vol'])
    df['mid']         = (df['ask'] + df['bid']) / 2.0
    df['spread_pips'] = (df['ask'] - df['bid']) * 10_000.0   # 4-decimal pips
    df['total_vol']   = df['ask_vol'] + df['bid_vol']
    return df


def _load_bi5_year(base_path: Path, year: int, max_files: int = None) -> pd.DataFrame:
    """Load all BI5 files under base_path/YYYY/."""
    year_dir = base_path / str(year)
    if not year_dir.exists():
        return pd.DataFrame()

    frames = []
    loaded = 0

    for month_dir in sorted(year_dir.iterdir()):
        if not month_dir.is_dir():
            continue
        try:
            month_0 = int(month_dir.name)
        except ValueError:
            continue
        if not (0 <= month_0 <= 11):
            continue

        for day_dir in sorted(month_dir.iterdir()):
            if not day_dir.is_dir():
                continue
            try:
                day = int(day_dir.name)
            except ValueError:
                continue

            for bi5_file in sorted(day_dir.glob("*h_ticks.bi5")):
                m = re.match(r'^(\d+)h_ticks\.bi5$', bi5_file.name)
                if not m:
                    continue
                hour = int(m.group(1))
                try:
                    raw = bi5_file.read_bytes()
                    df  = _decode_bi5(raw, year, month_0, day, hour)
                    if not df.empty:
                        frames.append(df)
                        loaded += 1
                except Exception:
                    continue
                if max_files and loaded >= max_files:
                    break
            if max_files and loaded >= max_files:
                break
        if max_files and loaded >= max_files:
            break

    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def _load_csv_2025(base_path: Path, max_rows: int = None) -> pd.DataFrame:
    """Load 2025 flat CSV tick data."""
    csv_path = base_path / "2025" / "eurusd_ticks_2025.csv"
    if not csv_path.exists():
        return pd.DataFrame()
    df = pd.read_csv(
        csv_path,
        parse_dates=['timestamp'],
        dtype={'ask': 'float32', 'bid': 'float32',
               'ask_volume': 'float32', 'bid_volume': 'float32'},
        low_memory=False,
        nrows=max_rows,
    )
    # normalise column names to match BI5 output
    df.rename(columns={'ask_volume': 'ask_vol', 'bid_volume': 'bid_vol'}, inplace=True)
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601', utc=True)
    df['mid']         = (df['ask'] + df['bid']) / 2.0
    df['spread_pips'] = (df['ask'] - df['bid']) * 10_000.0
    df['total_vol']   = df['ask_vol'] + df['bid_vol']
    return df


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def load_all_ticks(base_path: str | Path, max_files_per_year: int = None,
                   include_2025: bool = True,
                   max_rows_2025: int = None) -> pd.DataFrame:
    """
    Load complete EUR/USD tick history.

    Parameters
    ----------
    base_path          : path to the ``data/`` directory
    max_files_per_year : cap per year (None = load everything)
    include_2025       : whether to append the 2025 CSV

    Returns
    -------
    DataFrame with columns: timestamp, ask, bid, ask_vol, bid_vol,
                             mid, spread_pips, total_vol
    sorted by timestamp, index reset.
    """
    base_path = Path(base_path)
    frames = []

    for yr in (2023, 2024):
        print(f"  Loading {yr} BI5 data …", flush=True)
        df = _load_bi5_year(base_path, yr, max_files=max_files_per_year)
        if not df.empty:
            print(f"    {yr}: {len(df):,} ticks loaded")
            frames.append(df)

    if include_2025:
        print("  Loading 2025 CSV …", flush=True)
        df25 = _load_csv_2025(base_path, max_rows=max_rows_2025)
        if not df25.empty:
            print(f"    2025: {len(df25):,} ticks loaded")
            frames.append(df25)

    if not frames:
        raise RuntimeError("No data loaded — check base_path.")

    ticks = pd.concat(frames, ignore_index=True)
    ticks.sort_values('timestamp', inplace=True)
    ticks.reset_index(drop=True, inplace=True)

    # basic quality gate: drop rows with non-positive prices
    mask = (ticks['ask'] > 0) & (ticks['bid'] > 0) & (ticks['ask'] >= ticks['bid'])
    dropped = (~mask).sum()
    if dropped:
        print(f"  Quality gate: dropped {dropped:,} bad ticks")
    ticks = ticks[mask].reset_index(drop=True)

    return ticks


def summarise_ticks(ticks: pd.DataFrame) -> dict:
    """Return a summary dict for reporting."""
    ts = ticks['timestamp']
    gaps = ts.diff().dropna()
    # trading sessions: weekdays only
    wkday = ts.dt.dayofweek
    return {
        'total_ticks'    : len(ticks),
        'start'          : ts.iloc[0].isoformat(),
        'end'            : ts.iloc[-1].isoformat(),
        'trading_days'   : ts.dt.date.nunique(),
        'median_gap_sec' : gaps.median().total_seconds(),
        'p99_gap_sec'    : gaps.quantile(0.99).total_seconds(),
        'spread_mean_pips': ticks['spread_pips'].mean(),
        'spread_p99_pips' : ticks['spread_pips'].quantile(0.99),
        'ask_min'        : ticks['ask'].min(),
        'ask_max'        : ticks['ask'].max(),
    }
