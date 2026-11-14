"""
performance_profiler.py — Measure runtime, memory, and CPU overhead of the transport layer.
"""
import time
import tracemalloc
import numpy as np
import pandas as pd
import json
from typing import Dict


def profile_transport_layer(
    composite: pd.Series,
    c: float = 1.0,
    tau: float = 5.0,
    n_repeats: int = 5,
) -> Dict:
    """
    Measure wall-clock time and memory for compute_transport_from_series.

    Parameters
    ----------
    composite  : the normalized stress field Series to profile on
    n_repeats  : number of timing repetitions to average

    Returns
    -------
    dict with timing and memory metrics
    """
    from v12_validate.transport_layer import (
        compute_transport_from_series,
        compute_Q_vectorized,
    )

    n_bars = len(composite)
    s_arr  = composite.values.astype(np.float64)

    # ── Full pipeline timing ───────────────────────────────────────────────
    times_full = []
    for _ in range(n_repeats):
        t0 = time.perf_counter()
        _ = compute_transport_from_series(composite, c=c, tau=tau)
        times_full.append(time.perf_counter() - t0)

    # ── Q-only (algebraic, no PDE) timing ─────────────────────────────────
    times_q_only = []
    for _ in range(n_repeats):
        t0 = time.perf_counter()
        _ = compute_Q_vectorized(s_arr, c=c, tau=tau)
        times_q_only.append(time.perf_counter() - t0)

    # ── Memory profiling ──────────────────────────────────────────────────
    tracemalloc.start()
    _ = compute_transport_from_series(composite, c=c, tau=tau)
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    t_full_mean  = float(np.mean(times_full))
    t_q_mean     = float(np.mean(times_q_only))

    results = {
        'n_bars'                      : n_bars,
        'n_repeats'                   : n_repeats,
        # Full pipeline (PDE + Q + regime)
        'full_pipeline_total_sec'     : t_full_mean,
        'full_pipeline_per_bar_us'    : t_full_mean / n_bars * 1e6,
        'full_pipeline_bars_per_sec'  : n_bars / t_full_mean,
        'full_pipeline_std_sec'       : float(np.std(times_full)),
        # Q-only (algebraic)
        'q_only_total_sec'            : t_q_mean,
        'q_only_per_bar_us'           : t_q_mean / n_bars * 1e6,
        'q_only_bars_per_sec'         : n_bars / t_q_mean,
        # Memory
        'peak_memory_mb'              : peak_mem / 1024 / 1024,
        'current_memory_mb'           : current_mem / 1024 / 1024,
        # Overhead relative to n_bars
        'overhead_vs_5min_realtime'   : _realtime_overhead_pct(t_full_mean, n_bars),
    }
    return results


def _realtime_overhead_pct(total_sec: float, n_bars: int) -> float:
    """
    What fraction of real market time does the computation consume?
    Assuming 5-min bars and real-time operation.
    """
    real_time_sec = n_bars * 5 * 60  # 5 min per bar in seconds
    return float(total_sec / real_time_sec * 100.0)


def profile_full_pipeline(
    ticks: pd.DataFrame,
    c: float = 1.0,
    tau: float = 5.0,
) -> Dict:
    """
    Profile the complete data-to-transport pipeline end-to-end.
    Returns timing breakdown by stage.
    """
    from v12_validate.signals import build_signals_from_ticks
    from v12_validate.engine_runner import scale_signals_to_100, build_v12_composite, run_v12
    from v12_validate.transport_layer import compute_transport_from_series

    stages = {}

    t0 = time.perf_counter()
    ohlc, raw, normalized, composite = build_signals_from_ticks(ticks)
    stages['signal_construction_sec'] = time.perf_counter() - t0

    t0 = time.perf_counter()
    scaled, _ = scale_signals_to_100(raw)
    v12_comp, _ = build_v12_composite(scaled)
    v12_df = run_v12(v12_comp)
    stages['v12_engine_sec'] = time.perf_counter() - t0

    t0 = time.perf_counter()
    transport_df = compute_transport_from_series(composite, c=c, tau=tau)
    stages['transport_layer_sec'] = time.perf_counter() - t0

    total = sum(stages.values())
    stages['total_pipeline_sec'] = total
    stages['n_ticks']            = len(ticks)
    stages['n_bars']             = len(composite)
    stages['transport_pct_of_total'] = float(stages['transport_layer_sec'] / (total + 1e-12) * 100)
    stages['bars_per_sec']       = float(len(composite) / (total + 1e-12))

    # Practical verdict
    stages['practical_for_live_trading'] = stages['transport_layer_sec'] < 1.0

    return stages


def format_performance_report(full_profile: Dict, layer_profile: Dict) -> str:
    lines = [
        "## Performance Metrics",
        "",
        f"Dataset: {full_profile.get('n_bars', '?'):,} bars "
        f"({full_profile.get('n_ticks', '?'):,} ticks)",
        "",
        "### Pipeline Stage Timing",
        f"  Signal construction : {full_profile.get('signal_construction_sec', 0):.3f} s",
        f"  V12 engine          : {full_profile.get('v12_engine_sec', 0):.3f} s",
        f"  Transport layer     : {full_profile.get('transport_layer_sec', 0):.4f} s  "
        f"({full_profile.get('transport_pct_of_total', 0):.1f}% of total)",
        f"  TOTAL               : {full_profile.get('total_pipeline_sec', 0):.3f} s",
        "",
        "### Transport Layer Detail",
        f"  Full (PDE + Q)  : {layer_profile.get('full_pipeline_per_bar_us', 0):.2f} μs/bar  "
        f"({layer_profile.get('full_pipeline_bars_per_sec', 0):,.0f} bars/s)",
        f"  Q-only (algebraic): {layer_profile.get('q_only_per_bar_us', 0):.2f} μs/bar  "
        f"({layer_profile.get('q_only_bars_per_sec', 0):,.0f} bars/s)",
        f"  Peak memory     : {layer_profile.get('peak_memory_mb', 0):.2f} MB",
        f"  Realtime overhead: {layer_profile.get('overhead_vs_5min_realtime', 0):.4f}% of bar time",
        "",
        "### Verdict",
        f"  Practical for live trading: "
        f"{'YES' if full_profile.get('practical_for_live_trading') else 'NO'}",
    ]
    return "\n".join(lines)
