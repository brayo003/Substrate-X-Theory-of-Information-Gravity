"""
live/tests/test_determinism_audit.py

Determinism audit for the historical backfill / replay system.

Requirement (from spec)
-----------------------
Verify that:

    Cold Start
        Historical replay  →  Engine state

    matches

    Continuous live execution

for the same candle history.  The resulting Q, Regime, Strategy, and
internal pipeline state must be identical.

Test strategy
-------------
We do NOT need a live Binance connection.  The test constructs a
synthetic sequence of OHLCV candles and drives two independent
pipelines through them via two different routes:

  Path A — "Continuous live" (direct):
      candles fed one-by-one directly into CandleBuilder.on_trade()
      then IndicatorPipeline.add_candle() — exactly what BinanceStream
      does for live ticks.

  Path B — "Cold start / replay" (via HistoricalReplayer):
      The same sequence is packaged as REST candle dicts and passed to
      HistoricalReplayer.replay() — exactly what StartupBackfill does on
      startup.

After both paths process the same N candles, we assert that:
  1. pipeline_A.get_df()["tr_Q"]    == pipeline_B.get_df()["tr_Q"]     (all rows)
  2. pipeline_A.get_df()["regime"]  == pipeline_B.get_df()["regime"]   (all rows)
  3. Last Q values are identical (not NaN).
  4. Last regime labels are identical.
  5. Duplicate-suppression: running replay() a second time with the same
     candles does NOT add new bars to the pipeline.

How to run
----------
    cd finance_module
    python -m pytest live/tests/test_determinism_audit.py -v

Or standalone:
    python live/tests/test_determinism_audit.py
"""

import sys
import math
import time
import unittest
from pathlib import Path

# ── Path setup ─────────────────────────────────────────────────────────────
_ROOT = Path(__file__).resolve().parents[2]   # finance_module/
for _p in [str(_ROOT), str(_ROOT / "v12_validate")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pandas as pd
import numpy as np

from live.market.candle_builder    import CandleBuilder, IndicatorPipeline
from live.market.historical_replay import HistoricalReplayer


# ── Synthetic candle factory ────────────────────────────────────────────────

_CANDLE_MS = 5 * 60 * 1_000   # 5-min candles


def _make_synthetic_candles(n: int, base_price: float = 50_000.0) -> list:
    """
    Return a list of ``n`` candle dicts in the shape expected by
    ``fetch_completed_klines()`` (i.e. what HistoricalReplayer.replay()
    consumes).

    Uses a simple random-walk price so indicators have meaningful values.
    Seed is fixed for reproducibility.
    """
    rng = np.random.default_rng(seed=42)
    t0  = int(pd.Timestamp("2026-01-01", tz="UTC").timestamp() * 1_000)

    candles = []
    price = base_price
    for i in range(n):
        ots_ms = t0 + i * _CANDLE_MS
        cts_ms = ots_ms + _CANDLE_MS - 1

        # Random-walk close
        ret    = rng.normal(0, 0.002)
        close  = price * (1 + ret)
        high   = close * (1 + abs(rng.normal(0, 0.001)))
        low    = close * (1 - abs(rng.normal(0, 0.001)))
        open_  = price

        # Enforce OHLC sanity
        high   = max(high, open_, close)
        low    = min(low,  open_, close)
        volume = abs(rng.normal(100, 30))

        candles.append(dict(
            open_ts_ms  = ots_ms,
            close_ts_ms = cts_ms,
            timestamp   = pd.Timestamp(ots_ms, unit="ms", tz="UTC"),
            open        = float(open_),
            high        = float(high),
            low         = float(low),
            close       = float(close),
            volume      = float(volume),
            complete    = True,
        ))
        price = close

    return candles


# ── Path A helper — "direct live injection" ────────────────────────────────

def _run_path_a(candles: list) -> IndicatorPipeline:
    """
    Simulate continuous live execution:
        CandleBuilder.on_trade() for each OHLCV tick
        → CandleBuilder.get_completed_candles()
        → IndicatorPipeline.add_candle()

    This is exactly what BinanceStream does with live aggTrade events.
    Returns the populated pipeline after all candles are processed.
    """
    builder  = CandleBuilder("BTCUSDT_A")
    pipeline = IndicatorPipeline("BTCUSDT_A")

    for candle in candles:
        ots_ms = candle["open_ts_ms"]
        cts_ms = candle["close_ts_ms"]
        o = candle["open"]
        h = candle["high"]
        l = candle["low"]
        c = candle["close"]
        v = candle["volume"]

        # Inject the same synthetic trades as HistoricalReplayer._replay_one
        builder.on_trade(o, 0.0, ots_ms)
        builder.on_trade(h, 0.0, ots_ms + 1)
        builder.on_trade(l, 0.0, ots_ms + 2)
        builder.on_trade(c, v,   cts_ms - 1)

        # Close-trigger tick: falls in the next candle period
        builder.on_trade(c, 0.0, cts_ms + 1)

        for bar in builder.get_completed_candles():
            pipeline.add_candle(bar)

    return pipeline


# ── Path B helper — "replay" ───────────────────────────────────────────────

def _run_path_b(candles: list) -> tuple:
    """
    Simulate cold-start replay:
        HistoricalReplayer.replay(candles)

    Returns (pipeline, replayer) after replay completes.
    """
    builder  = CandleBuilder("BTCUSDT_B")
    pipeline = IndicatorPipeline("BTCUSDT_B")

    replayer = HistoricalReplayer(
        symbol   = "BTCUSDT_B",
        builder  = builder,
        pipeline = pipeline,
        engine   = None,
        logger   = None,
    )
    replayer.replay(candles)
    return pipeline, replayer


# ── Assertion helpers ──────────────────────────────────────────────────────

def _assert_series_equal(name: str, a: pd.Series, b: pd.Series):
    """Compare two series element-by-element with tolerance for floats."""
    assert len(a) == len(b), (
        f"{name}: length mismatch: A={len(a)} B={len(b)}"
    )
    for i, (va, vb) in enumerate(zip(a, b)):
        if isinstance(va, float) and isinstance(vb, float):
            if math.isnan(va) and math.isnan(vb):
                continue
            assert math.isclose(va, vb, rel_tol=1e-9, abs_tol=1e-12), (
                f"{name}[{i}]: A={va!r} != B={vb!r}"
            )
        else:
            assert va == vb, f"{name}[{i}]: A={va!r} != B={vb!r}"


# ══════════════════════════════════════════════════════════════════════════
# Test cases
# ══════════════════════════════════════════════════════════════════════════

class TestDeterminismAudit(unittest.TestCase):
    """
    Audit: cold-start replay must produce identical state to continuous live
    execution for the same candle history.
    """

    # We need 120 candles so both paths are above WARMUP_BARS=100 and the
    # indicator burn-in (EMA/rolling windows up to 50 bars) is complete.
    N_CANDLES = 130

    @classmethod
    def setUpClass(cls):
        """Generate candles once and run both paths."""
        cls.candles  = _make_synthetic_candles(cls.N_CANDLES)
        cls.pipeline_a = _run_path_a(cls.candles)
        cls.pipeline_b, cls.replayer = _run_path_b(cls.candles)

        cls.df_a = cls.pipeline_a.get_df()
        cls.df_b = cls.pipeline_b.get_df()

    # ── 1. Both pipelines must be ready ───────────────────────────────────

    def test_01_pipeline_a_ready(self):
        """Path A (direct) pipeline must be warmed."""
        r = self.pipeline_a.readiness
        self.assertTrue(r.ready, f"Pipeline A not ready: {r}")

    def test_02_pipeline_b_ready(self):
        """Path B (replay) pipeline must be warmed."""
        r = self.pipeline_b.readiness
        self.assertTrue(r.ready, f"Pipeline B not ready: {r}")

    def test_03_replay_complete_flag(self):
        """Replayer must report replay_complete=True after replay()."""
        self.assertTrue(
            self.replayer.replay_complete,
            "replayer.replay_complete is False after replay()"
        )

    def test_04_replayer_cursor_set(self):
        """Replayer cursor must point to the last candle's open_ts."""
        expected = self.candles[-1]["open_ts_ms"]
        got      = self.replayer.last_replayed_ts_ms
        self.assertEqual(
            got, expected,
            f"last_replayed_ts_ms={got} expected={expected}"
        )

    # ── 2. DataFrame shape must be identical ──────────────────────────────

    def test_05_df_not_none(self):
        """Both pipelines must return a non-None DataFrame."""
        self.assertIsNotNone(self.df_a, "Pipeline A get_df() returned None")
        self.assertIsNotNone(self.df_b, "Pipeline B get_df() returned None")

    def test_06_df_same_length(self):
        """Both DataFrames must have the same number of rows."""
        self.assertEqual(
            len(self.df_a), len(self.df_b),
            f"Row count: A={len(self.df_a)} B={len(self.df_b)}"
        )

    def test_07_df_same_columns(self):
        """Both DataFrames must have the same column set."""
        cols_a = set(self.df_a.columns)
        cols_b = set(self.df_b.columns)
        self.assertEqual(cols_a, cols_b, f"Column mismatch: {cols_a ^ cols_b}")

    # ── 3. Core Transport OS values must be identical ─────────────────────

    def test_08_tr_Q_identical(self):
        """
        tr_Q column must be bit-for-bit equal (or NaN-for-NaN) across
        all rows in both pipelines.
        This is the primary determinism contract.
        """
        _assert_series_equal("tr_Q", self.df_a["tr_Q"], self.df_b["tr_Q"])

    def test_09_regime_identical(self):
        """
        Regime labels must be identical across all rows.
        """
        _assert_series_equal("regime", self.df_a["regime"], self.df_b["regime"])

    def test_10_last_Q_not_nan(self):
        """
        The last Q value must not be NaN — pipeline is fully warmed.
        """
        q_a = float(self.df_a["tr_Q"].iloc[-1])
        q_b = float(self.df_b["tr_Q"].iloc[-1])
        self.assertFalse(math.isnan(q_a), f"Path A last tr_Q is NaN")
        self.assertFalse(math.isnan(q_b), f"Path B last tr_Q is NaN")

    def test_11_last_Q_match(self):
        """Final Q values from both paths must be equal."""
        q_a = float(self.df_a["tr_Q"].iloc[-1])
        q_b = float(self.df_b["tr_Q"].iloc[-1])
        self.assertTrue(
            math.isclose(q_a, q_b, rel_tol=1e-9),
            f"Final Q: A={q_a} B={q_b}"
        )

    def test_12_last_regime_match(self):
        """Final regime labels must be identical."""
        r_a = self.df_a["regime"].iloc[-1]
        r_b = self.df_b["regime"].iloc[-1]
        self.assertEqual(r_a, r_b, f"Final regime: A={r_a!r} B={r_b!r}")

    # ── 4. OHLCV and key indicator columns must be identical ──────────────

    def test_13_ohlcv_identical(self):
        """OHLCV values must be identical (same candles fed to both paths)."""
        for col in ("open", "high", "low", "close", "volume"):
            _assert_series_equal(col, self.df_a[col], self.df_b[col])

    def test_14_atr_identical(self):
        """ATR-14 must be identical — used for position sizing."""
        _assert_series_equal("atr_14", self.df_a["atr_14"], self.df_b["atr_14"])

    def test_15_rsi_identical(self):
        """RSI-14 must be identical."""
        _assert_series_equal("rsi_14", self.df_a["rsi_14"], self.df_b["rsi_14"])

    def test_16_macd_hist_identical(self):
        """MACD histogram must be identical."""
        _assert_series_equal(
            "macd_hist", self.df_a["macd_hist"], self.df_b["macd_hist"]
        )

    def test_17_composite_norm_identical(self):
        """composite_norm must be identical — it feeds the transport eq."""
        _assert_series_equal(
            "composite_norm",
            self.df_a["composite_norm"],
            self.df_b["composite_norm"]
        )

    # ── 5. Duplicate-suppression contract ────────────────────────────────

    def test_18_duplicate_replay_no_new_bars(self):
        """
        Running replay() a SECOND time with the same candles must not
        add any new bars to the pipeline.
        """
        before = self.pipeline_b.readiness.bars_received

        # Second replay — all candles already replayed
        self.replayer.replay(self.candles)

        after = self.pipeline_b.readiness.bars_received
        self.assertEqual(
            before, after,
            f"Duplicate replay added {after - before} extra bars "
            f"(before={before} after={after})"
        )

    # ── 6. Partial-replay (gap-fill) determinism ─────────────────────────

    def test_19_gap_fill_determinism(self):
        """
        replay_gap() with the last N candles must produce identical Q
        and regime on a third pipeline that starts from a partial history.

        We simulate: pipeline C is seeded with the first 105 candles (hot),
        then gap-filled with the remaining 25 candles via replay_gap().
        The final Q and regime must match path A.
        """
        split = 105
        candles_warm = self.candles[:split]
        candles_gap  = self.candles[split:]

        # Build pipeline C via direct injection (path A style) for first 105
        pipeline_c = _run_path_a(candles_warm)

        builder_c  = CandleBuilder("BTCUSDT_C")
        replayer_c = HistoricalReplayer(
            symbol   = "BTCUSDT_C",
            builder  = builder_c,
            pipeline = pipeline_c,
            engine   = None,
            logger   = None,
        )

        # Manually set the cursor so gap-fill knows where to start
        replayer_c._last_replayed_ts_ms = candles_warm[-1]["open_ts_ms"]
        replayer_c._replay_complete     = True

        # Gap-fill with remaining candles
        replayer_c.replay_gap(candles_gap)

        df_c = pipeline_c.get_df()
        self.assertIsNotNone(df_c, "Pipeline C get_df() returned None after gap-fill")

        q_a = float(self.df_a["tr_Q"].iloc[-1])
        q_c = float(df_c["tr_Q"].iloc[-1])
        r_a = self.df_a["regime"].iloc[-1]
        r_c = df_c["regime"].iloc[-1]

        self.assertTrue(
            math.isclose(q_a, q_c, rel_tol=1e-9),
            f"Gap-fill Q mismatch: A={q_a} C={q_c}"
        )
        self.assertEqual(r_a, r_c, f"Gap-fill regime mismatch: A={r_a!r} C={r_c!r}")

    # ── 7. Bar count sanity ────────────────────────────────────────────────

    def test_20_bar_count_equals_n_candles(self):
        """
        Both pipelines must have received exactly N_CANDLES bars.
        (The trigger tick seeds the next bar's open but does NOT complete
        an extra bar unless there's a candle for it — there isn't.)
        """
        r_a = self.pipeline_a.readiness
        r_b = self.pipeline_b.readiness
        self.assertEqual(
            r_a.bars_received, self.N_CANDLES,
            f"Path A bars_received={r_a.bars_received} expected={self.N_CANDLES}"
        )
        self.assertEqual(
            r_b.bars_received, self.N_CANDLES,
            f"Path B bars_received={r_b.bars_received} expected={self.N_CANDLES}"
        )


# ══════════════════════════════════════════════════════════════════════════
# Standalone runner
# ══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 64)
    print("Determinism Audit — Backfill/Replay vs Live Execution")
    print("=" * 64)
    print(f"Generating {TestDeterminismAudit.N_CANDLES} synthetic candles …")
    t0 = time.monotonic()

    loader = unittest.TestLoader()
    suite  = loader.loadTestsFromTestCase(TestDeterminismAudit)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    elapsed = time.monotonic() - t0
    print(f"\nCompleted in {elapsed:.2f}s")
    sys.exit(0 if result.wasSuccessful() else 1)
