"""
p1_checkpoint.py — Checkpoint manager for Phase 1 incremental pipeline.

Maintains a JSON manifest at checkpoints/checkpoint_manifest.json.
All writes are atomic (write to .tmp, rename over final).

Directories created on first use:
  checkpoints/   — manifest + per-stage completion flags
  cache/         — pre-built OHLC+transport parquet files (one per month)
  intermediate/  — per-strategy trade parquet files
"""

import json
import os
import time
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent

CHECKPOINT_DIR  = BASE_DIR / "checkpoints"
CACHE_DIR       = BASE_DIR / "cache"
INTERMEDIATE_DIR= BASE_DIR / "intermediate"
RESULTS_DIR     = BASE_DIR / "results" / "phase1"

MANIFEST_PATH   = CHECKPOINT_DIR / "checkpoint_manifest.json"


def ensure_dirs():
    """Create all required directories."""
    for d in [CHECKPOINT_DIR, CACHE_DIR, INTERMEDIATE_DIR,
              RESULTS_DIR, RESULTS_DIR / "plots"]:
        d.mkdir(parents=True, exist_ok=True)


def _atomic_write(path: Path, data: str):
    """Write data atomically: write to .tmp then rename."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(data, encoding="utf-8")
    tmp.replace(path)


def load_manifest() -> Dict[str, Any]:
    """Load manifest from disk, or return empty manifest."""
    if MANIFEST_PATH.exists():
        try:
            return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "version": "1.0",
        "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "last_updated": None,
        "pipeline": {
            "data_cache_complete": False,
            "q_series_complete": False,
            "q_quantiles": None,
            "strategies_complete": [],
            "stats_complete": False,
            "regime_analysis_complete": False,
            "allocator_complete": False,
            "heatmap_complete": False,
            "report_complete": False,
        },
        "data_stats": {},
        "strategy_trade_counts": {},
    }


def save_manifest(manifest: Dict[str, Any]):
    """Save manifest atomically."""
    ensure_dirs()
    manifest["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    _atomic_write(MANIFEST_PATH, json.dumps(manifest, indent=2, default=str))


def mark_cache_complete(manifest: Dict, stats: Dict):
    manifest["pipeline"]["data_cache_complete"] = True
    manifest["data_stats"] = stats
    save_manifest(manifest)


def mark_q_series_complete(manifest: Dict, q_quantiles: Dict):
    manifest["pipeline"]["q_series_complete"] = True
    manifest["pipeline"]["q_quantiles"] = q_quantiles
    save_manifest(manifest)


def mark_strategy_complete(manifest: Dict, strategy_name: str, trade_count: int):
    done = manifest["pipeline"]["strategies_complete"]
    if strategy_name not in done:
        done.append(strategy_name)
    manifest["strategy_trade_counts"][strategy_name] = trade_count
    save_manifest(manifest)


def mark_stats_complete(manifest: Dict):
    manifest["pipeline"]["stats_complete"] = True
    save_manifest(manifest)


def mark_regime_analysis_complete(manifest: Dict):
    manifest["pipeline"]["regime_analysis_complete"] = True
    save_manifest(manifest)


def mark_allocator_complete(manifest: Dict):
    manifest["pipeline"]["allocator_complete"] = True
    save_manifest(manifest)


def mark_heatmap_complete(manifest: Dict):
    manifest["pipeline"]["heatmap_complete"] = True
    save_manifest(manifest)


def mark_report_complete(manifest: Dict):
    manifest["pipeline"]["report_complete"] = True
    save_manifest(manifest)


def is_strategy_done(manifest: Dict, strategy_name: str) -> bool:
    return strategy_name in manifest["pipeline"]["strategies_complete"]


def cache_path_for_month(year: int, month: int) -> Path:
    """Parquet path for one month of OHLC+transport data."""
    return CACHE_DIR / f"ohlc_transport_{year}_{month:02d}.parquet"


def intermediate_path_for_strategy(strategy_name: str) -> Path:
    """Parquet path for one strategy's accumulated trade log."""
    safe = strategy_name.replace("/", "_").replace(" ", "_")
    return INTERMEDIATE_DIR / f"trades_{safe}.parquet"


def q_series_path() -> Path:
    """Parquet path for full Q series (timestamp + Q + regime)."""
    return CACHE_DIR / "q_series_full.parquet"


def append_trades_to_intermediate(strategy_name: str, new_trades_df):
    """Append new trades to strategy's intermediate parquet file."""
    import pandas as pd
    path = intermediate_path_for_strategy(strategy_name)
    if path.exists() and len(new_trades_df) > 0:
        existing = pd.read_parquet(path)
        combined = pd.concat([existing, new_trades_df], ignore_index=True)
        combined.to_parquet(path, index=False)
    elif len(new_trades_df) > 0:
        new_trades_df.to_parquet(path, index=False)


def load_all_trades() -> "pd.DataFrame":
    """Load and concatenate all intermediate strategy trade files."""
    import pandas as pd
    frames = []
    for p in sorted(INTERMEDIATE_DIR.glob("trades_*.parquet")):
        try:
            df = pd.read_parquet(p)
            if len(df) > 0:
                frames.append(df)
        except Exception as e:
            print(f"  WARNING: could not read {p}: {e}")
    if not frames:
        import pandas as pd
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def pipeline_status(manifest: Dict) -> str:
    """Return a readable status string."""
    p = manifest["pipeline"]
    lines = [
        f"  data_cache_complete     : {p['data_cache_complete']}",
        f"  q_series_complete       : {p['q_series_complete']}",
        f"  strategies_complete     : {len(p['strategies_complete'])} done",
        f"  stats_complete          : {p['stats_complete']}",
        f"  regime_analysis_complete: {p['regime_analysis_complete']}",
        f"  allocator_complete      : {p['allocator_complete']}",
        f"  heatmap_complete        : {p['heatmap_complete']}",
        f"  report_complete         : {p['report_complete']}",
    ]
    return "\n".join(lines)
