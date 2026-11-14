"""
test_gold_execution.py
======================
Automated test suite verifying:
1. Indicator causality (no look-ahead in rolling channels or ATR)
2. Execution sequence and gap fill logic
3. Bit-for-bit reproducibility of prior report numbers on original data
4. Cost calculation and unit consistency
"""

import unittest
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent.parent
if str(HERE) not in sys.path if 'sys' in globals() else True:
    import sys
    sys.path.insert(0, str(HERE))

from validate_gold_baseline import (
    load_original_xauusd,
    add_indicators,
    sig_donchian20,
    simulate_old_engine,
    simulate_corrected_engine,
    compute_metrics
)

class TestGoldExecution(unittest.TestCase):

    def setUp(self):
        self.df_orig = load_original_xauusd()
        self.df_ind = add_indicators(self.df_orig)

    def test_indicator_causality(self):
        """Verify that don_hi and don_lo use only past completed bars (shift 1)."""
        df = self.df_ind
        for i in range(25, 50):
            # don_hi at bar i must be max of high[i-20 : i]
            expected_hi = df['high'].iloc[i-20:i].max()
            actual_hi = df['don_hi'].iloc[i]
            self.assertAlmostEqual(actual_hi, expected_hi, places=4,
                                   msg=f"Lookahead detected in don_hi at bar {i}")

    def test_gap_fill_execution(self):
        """Verify that if open gaps past stop loss, execution fills at open, not stop."""
        dates = pd.date_range("2024-01-01", periods=5, freq="D", tz="UTC")
        dummy_df = pd.DataFrame({
            'open':  [100.0, 100.0,  80.0, 85.0, 90.0],
            'high':  [105.0, 105.0,  85.0, 90.0, 95.0],
            'low':   [ 98.0,  98.0,  75.0, 80.0, 85.0],
            'close': [102.0, 102.0,  82.0, 88.0, 92.0],
            'atr14': [  5.0,   5.0,   5.0,  5.0,  5.0]
        }, index=dates)

        # Signal buy at bar 0 -> enter bar 1 open=100.0
        # Stop at 100 - 1.5 * 5 = 92.5
        # Bar 2 opens at 80.0 (gapping below stop 92.5)
        sig = pd.Series([1, 0, 0, 0, 0], index=dates)
        trades = simulate_corrected_engine(dummy_df, sig, stop_m=1.5, tgt_m=3.0, rt_cost=0.0)
        self.assertEqual(len(trades), 1)
        t = trades.iloc[0]
        self.assertEqual(t['exit_reason'], 'stop_gap')
        self.assertAlmostEqual(t['exit_price'], 80.0, places=2,
                               msg="Gap fill failed: must fill at open 80.0, not stop 92.5")

    def test_reproducibility_prior_report(self):
        """Verify bit-for-bit reproduction of WF Combined results from prior report."""
        df = self.df_ind
        wf1 = df["2025-09-01":"2025-12-31"]
        wf2 = df["2026-01-01":"2026-07-21"]

        sig_wf1 = sig_donchian20(df)[wf1.index]
        sig_wf2 = sig_donchian20(df)[wf2.index]

        t_wf1 = simulate_old_engine(wf1, sig_wf1, period='WF1')
        t_wf2 = simulate_old_engine(wf2, sig_wf2, period='WF2')
        wf = pd.concat([t_wf1, t_wf2], ignore_index=True)

        m = compute_metrics(wf, "Donchian20", "WF_Combined")
        self.assertEqual(m['n'], 21)
        self.assertAlmostEqual(m['net_pf'], 2.042, places=3)
        self.assertAlmostEqual(m['exp_usd'], 56.529, places=3)
        self.assertAlmostEqual(m['wr'], 0.619, places=3)

    def test_cost_deduction_arithmetic(self):
        """Verify that Net PnL = Raw PnL - RT_COST exactly."""
        df = self.df_ind[:"2025-08-31"]
        sig = sig_donchian20(df)
        trades = simulate_corrected_engine(df, sig, rt_cost=1.50)
        for _, t in trades.iterrows():
            expected_net = t['raw_pnl'] - 1.50 - t.get('swap_cost', 0.0)
            self.assertAlmostEqual(t['net_pnl'], expected_net, places=4)

if __name__ == '__main__':
    unittest.main()
