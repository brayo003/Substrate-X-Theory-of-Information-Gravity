"""Unit / smoke tests for Task 8 computational expressivity."""
from __future__ import annotations

import os
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_SIM = os.path.dirname(_HERE)
_PARENT = os.path.dirname(_SIM)
for _p in (_PARENT, _SIM):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from sim_world.exp8 import config as cfg
from sim_world.exp8.field_core import FieldSim, activated, pair_sites
from sim_world.exp8.experiments import run_A_trial, run_B_trial, run_C_trial, run_D_hysteresis
from sim_world.exp8.numerical_validation import run_numerical_suite
from sim_world.exp8.baselines import symbolic_coincidence
from sim_world.exp8.classify import classify_operations


class TestExp8FieldCore(unittest.TestCase):
    def test_decoder_ignores_deposit_log(self):
        sim = FieldSim("nonlinear_full")
        sim.deposit(25.0, 25.0, 0.01, 0)
        # Manually corrupt deposit_log — decoder must still use field only
        sim.deposit_log.append({"x": 25, "y": 25, "amp": 99, "tick": 0})
        self.assertFalse(activated(sim, 25.0, 25.0))

    def test_near_pair_activates_far_does_not(self):
        near = run_A_trial(0, "near_pair", ablation="nonlinear_full")
        far = run_A_trial(0, "far_pair", ablation="nonlinear_full")
        single = run_A_trial(0, "single", ablation="nonlinear_full")
        self.assertFalse(near.get("failed"))
        self.assertEqual(near["y_pred"], 1)
        self.assertEqual(far["y_pred"], 0)
        self.assertEqual(single["y_pred"], 0)

    def test_linear_near_pair_does_not_latch(self):
        t = run_A_trial(0, "near_pair", ablation="linear_telegraph")
        self.assertFalse(t.get("failed"))
        self.assertEqual(t["y_pred"], 0)

    def test_readout_only_no_evolution_and_no_false_latch(self):
        t = run_A_trial(0, "near_pair", ablation="readout_only")
        self.assertEqual(t.get("n_steps", 0), 0)
        # High-basin thr must not fire on instantaneous overlap alone
        self.assertEqual(t["y_pred"], 0)


class TestExp8TemporalSpatial(unittest.TestCase):
    def test_temporal_window_edges(self):
        t0 = run_B_trial(1, delay=0, ablation="nonlinear_full")
        t40 = run_B_trial(1, delay=40, ablation="nonlinear_full")
        self.assertEqual(t0["y_pred"], 1)
        self.assertEqual(t40["y_pred"], 0)

    def test_equal_mass_cluster_vs_dispersed(self):
        c = run_C_trial(2, "cluster", "nonlinear_full")
        d = run_C_trial(2, "dispersed", "nonlinear_full")
        self.assertEqual(c["total_mass"], d["total_mass"])
        self.assertEqual(c["y_pred"], 1)
        self.assertEqual(d["y_pred"], 0)


class TestExp8NumericalAndClassify(unittest.TestCase):
    def test_numerical_suite(self):
        r = run_numerical_suite()
        self.assertTrue(r["all_pass"], msg=str(r))

    def test_symbolic_baseline(self):
        a, b, _ = pair_sites(0, cfg.A_NEAR_SEP)
        self.assertEqual(symbolic_coincidence([a, b]), 1)
        af, bf, _ = pair_sites(0, cfg.A_FAR_SEP)
        self.assertEqual(symbolic_coincidence([af, bf]), 0)

    def test_classify_structure(self):
        # Minimal stub
        stub = {
            "A": {"primary_metrics": {"near_pair": {"f1": 0.9, "fp": 0, "tn": 8},
                                      "far_pair": {"f1": 1.0, "fp": 0, "tn": 8}},
                  "summary_by_ablation": {
                      "nonlinear_full": {"near_pair": {"accuracy": 1.0, "p_activate": 1.0}},
                      "linear_telegraph": {"near_pair": {"accuracy": 0.0, "p_activate": 0.0}},
                      "readout_only": {"near_pair": {"accuracy": 0.0, "p_activate": 0.0}},
                  },
                  "response_surface_nl": {"cells": [
                      {"p_activate": 0.0}, {"p_activate": 1.0},
                  ]}},
            "B": {"integration_window": {
                "0": {"p_activate": 1.0}, "20": {"p_activate": 1.0}, "40": {"p_activate": 0.0},
            }, "trials": []},
            "C": {"summary": {
                "nonlinear_full": {
                    "cluster": {"accuracy": 1.0, "p_activate": 1.0},
                    "dispersed": {"accuracy": 1.0, "p_activate": 0.0},
                    "triangle": {"accuracy": 1.0, "p_activate": 1.0},
                },
                "linear_telegraph": {"cluster": {"accuracy": 0.0, "p_activate": 0.0}},
            }},
            "D": {"nl_mean_forward_amp": 0.55, "hysteresis": [
                {"ablation": "nonlinear_full", "forward_activation_amp": 0.55,
                 "reverse_drop_neg_amp": 0.9, "still_high_after_strong": 1},
            ]},
            "E": {"summary": {}, "limitation": "scalar"},
            "F": {"completion_lift_nl": 0.1, "summary": {}},
            "numerical": {"all_pass": True},
            "behavioural_bridge": None,
        }
        c = classify_operations(stub)
        self.assertGreaterEqual(c["A_coincidence"]["category"], 3)
        self.assertIn("_meta", c)


class TestExp8HysteresisSmoke(unittest.TestCase):
    def test_hysteresis_runs(self):
        h = run_D_hysteresis(0, "nonlinear_full")
        self.assertFalse(h.get("failed"))
        self.assertIsNotNone(h.get("forward_activation_amp"))


if __name__ == "__main__":
    unittest.main()
