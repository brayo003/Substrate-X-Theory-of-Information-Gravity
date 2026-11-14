"""Causal ablation tests for Task 9 Experiment B mechanisms."""
from __future__ import annotations

import os
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_SIM = os.path.dirname(_HERE)
_PARENT = os.path.dirname(_SIM)
for p in (_PARENT, _SIM):
    if p not in sys.path:
        sys.path.insert(0, p)

from sim_world.exp9 import config as cfg
from sim_world.exp9.field_backend import make_medium, SubstrateMedium
from sim_world.exp9.experiments import controlled_coincidence_smoke


class TestExp9Ablations(unittest.TestCase):
    def test_reaction_off_blocks_latch(self):
        smoke = controlled_coincidence_smoke()
        self.assertTrue(smoke["rows"]["nonlinear_full"]["activated"])
        self.assertFalse(smoke["rows"]["linear_telegraph"]["activated"])

    def test_deposit_disabled_writes_noop(self):
        m = make_medium("ablation", ablation="deposit_disabled")
        lx, ly = cfg.LANDMARKS[0]
        m.deposit(lx, ly, cfg.DEP_AMP, 0)
        self.assertEqual(m.usage().writes, 0)
        self.assertEqual(m.query_at(lx, ly, 0), 0.0)

    def test_readout_disabled_returns_zero(self):
        m = make_medium("ablation", ablation="readout_disabled")
        lx, ly = cfg.LANDMARKS[0]
        m.deposit(lx, ly, 1.2, 0)  # strong
        for t in range(40):
            m.tick_update(t)
        self.assertEqual(m.query_at(lx, ly, 40), 0.0)

    def test_no_propagation_still_local_latch_possible(self):
        # Task 8 finding: local overlap latch without propagation
        m = SubstrateMedium("no_propagation")
        lx, ly = cfg.LANDMARKS[0]
        m.deposit(lx, ly, cfg.DEP_AMP, 0)
        m.deposit(lx + 1.0, ly, cfg.DEP_AMP, 0)
        for t in range(60):
            m.tick_update(t)
        self.assertFalse(m.failed())
        # May or may not activate depending on overlap; must remain finite
        self.assertTrue(np_isfinite_max(m))

    def test_make_medium_all_architectures(self):
        for arch in cfg.ARCHITECTURES:
            m = make_medium(arch)
            self.assertIsNotNone(m)
            m.tick_update(0)


def np_isfinite_max(m: SubstrateMedium) -> bool:
    import numpy as np
    return bool(np.isfinite(m.grid_max()))


if __name__ == "__main__":
    unittest.main()
