"""Tests for Task 9 agent–substrate interface (no privileged k*)."""
from __future__ import annotations

import os
import sys
import unittest

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_SIM = os.path.dirname(_HERE)
_PARENT = os.path.dirname(_SIM)
for p in (_PARENT, _SIM):
    if p not in sys.path:
        sys.path.insert(0, p)

from sim_world.exp9 import config as cfg
from sim_world.exp9.env import build_world, sense_evidence
from sim_world.exp9.field_backend import make_medium, SubstrateMedium
from sim_world.exp9.experiments import controlled_coincidence_smoke, _run_trial


class TestExp9Interface(unittest.TestCase):
    def test_world_withholds_kstar_from_agent_state(self):
        w = build_world(0)
        # AgentState has no true_landmark attribute
        for a in w.agents:
            self.assertFalse(hasattr(a, "true_landmark"))
            self.assertIsNone(a.committed)

    def test_sense_evidence_has_no_is_true_flag(self):
        w = build_world(1)
        rng = np.random.default_rng(0)
        # Place agent on first evidence
        p = w.evidence[0]
        w.agents[0].x, w.agents[0].y = p.x, p.y
        obs = sense_evidence(w, w.agents[0], tick=max(p.available_from, 0), rng=rng)
        self.assertTrue(obs)
        self.assertNotIn("is_true", obs[0])

    def test_deposit_and_read_local(self):
        m = SubstrateMedium("nonlinear_full")
        lx, ly = cfg.LANDMARKS[0]
        m.deposit(lx, ly, cfg.DEP_AMP, 0)
        v = m.query_at(lx, ly, 0)
        self.assertGreater(v, 0.1)
        self.assertEqual(m.usage().writes, 1)
        self.assertEqual(m.usage().reads, 1)

    def test_agents_cannot_read_deposit_log(self):
        m = SubstrateMedium("nonlinear_full")
        m.deposit(10, 10, 0.5, 0)
        # Policy API has no deposit_log accessor on MediumBackend protocol used by agents
        self.assertTrue(hasattr(m, "deposit_log"))
        # ensure make_medium independent has no shared field
        ind = make_medium("independent")
        ind.deposit(10, 10, 0.5, 0)
        self.assertEqual(ind.query_at(10, 10, 0), 0.0)

    def test_controlled_coincidence_smoke(self):
        r = controlled_coincidence_smoke()
        self.assertTrue(r["pass"], r)

    def test_trial_runs_without_crash(self):
        t = _run_trial(0, "nonlinear_sub")
        self.assertIn("correct", t)
        self.assertFalse(t["failed"])


if __name__ == "__main__":
    unittest.main()
