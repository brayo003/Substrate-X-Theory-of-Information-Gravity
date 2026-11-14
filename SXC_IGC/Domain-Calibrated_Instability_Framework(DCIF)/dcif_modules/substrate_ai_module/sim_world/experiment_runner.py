"""
Phase 10 Experiment Runner
==========================

Rigorous repeated-trial experiment for spectral substrate advantage validation.

Four conditions:
  A. baseline  — pure need-based rules, NO substrate signal path
  B. legacy_q  — local gradient Q, sigmoid-normalised to [-1,+1]
  C. spectral  — corrected C_spectral = f_prop - f_over
  D. ablation  — time-reversal of spectral signals (same marginal, wrong timing)

Three scenarios:
  1. stable     — 50 ticks, fixed bumps, no disturbances
  2. dynamic    — 60 ticks, 2 perturbation events at ticks 15 and 35
  3. disrupted  — 60 ticks, coordination blocked ticks 20-29, field reset at 25

Primary metric: mean_final_hunger (lower = better).

Pairing: each trial uses seed = base_seed + trial_index; all four conditions
         within a trial use identical seed-derived initial conditions.

Usage:
    python experiment_runner.py                   # full experiment
    python experiment_runner.py --smoke-only       # 1 trial smoke test
    python experiment_runner.py --trials 5         # override trial count
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from dataclasses import dataclass, field, asdict
from typing import Any

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

import numpy as np

from sim_world.domains.physical_field.physical_field_dynamics import (
    initialize_field_state, evolve_field, apply_perturbation,
    compute_theoretical_q, compute_spectral_transport_observable,
)
from sim_world.domains.physical_field.physical_field_models import (
    InformationDensityField, PhysicalCoordinate,
    PropagationParameters, RelaxationParameters,
)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class ExperimentConfig:
    n_trials: int = 30
    n_ticks_stable: int = 50
    n_ticks_dynamic: int = 60
    n_ticks_disrupted: int = 60
    n_agents: int = 5
    tau: float = 3.0
    c: float = 1.0
    tau_scan_values: list = field(default_factory=lambda: [
        0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0
    ])
    tau_scan_trials: int = 10
    base_seed: int = 1000
    tau_scan_base_seed: int = 2000
    conditions: list = field(default_factory=lambda: [
        "baseline", "legacy_q", "spectral", "ablation"
    ])
    scenarios: list = field(default_factory=lambda: [
        "stable", "dynamic", "disrupted"
    ])
    # Grid
    grid_nx: int = 30
    grid_ny: int = 30
    grid_x_max: float = 50.0
    grid_y_max: float = 50.0
    dt: float = 0.05
    # Measurement coordinate for local Q (legacy_q condition)
    measure_x: float = 15.0
    measure_y: float = 12.0


# ---------------------------------------------------------------------------
# Field helpers
# ---------------------------------------------------------------------------

def _build_field(rng: np.random.Generator, tau: float, c: float,
                 cfg: ExperimentConfig) -> tuple:
    """Build initial field from seeded rng. Returns (field, prop, relax, measure_coord)."""
    state = initialize_field_state(
        x_range=(0.0, cfg.grid_x_max),
        y_range=(0.0, cfg.grid_y_max),
        nx=cfg.grid_nx,
        ny=cfg.grid_ny,
        initial_value=1.0,
        dt=cfg.dt,
    )
    field = InformationDensityField(
        state=state, information_quantity=1.0,
        physical_volume=cfg.grid_x_max * cfg.grid_y_max * 1.0,
        information_units="bits", spatial_units="m", density_units="bits/m³",
    )
    # Seed-derived bumps
    n_bumps = 4
    for _ in range(n_bumps):
        bx = float(rng.uniform(10.0, 40.0))
        by = float(rng.uniform(10.0, 40.0))
        amp = float(rng.uniform(2.0, 4.0))
        field = apply_perturbation(field, PhysicalCoordinate(bx, by, 0.0), amp, 3.0)

    prop  = PropagationParameters(c_nominal=c)
    relax = RelaxationParameters(tau_nominal=tau)
    coord = PhysicalCoordinate(x=cfg.measure_x, y=cfg.measure_y, z=0.0)
    return field, prop, relax, coord


def _reset_field(rng_seed: int, tau: float, c: float, cfg: ExperimentConfig) -> tuple:
    """Rebuild a fresh identical field from scratch using the same seed."""
    rng = np.random.default_rng(rng_seed)
    return _build_field(rng, tau, c, cfg)


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

@dataclass
class Agent:
    name: str
    x: float
    y: float
    hunger: float
    energy: float
    stress: float
    _initial_stress: float = field(init=False)
    hunger_spike_count: int = field(default=0, init=False)
    total_hunger_reduced: float = field(default=0.0, init=False)
    total_energy_spent: float = field(default=0.0, init=False)

    def __post_init__(self) -> None:
        self._initial_stress = self.stress

    # ------------------------------------------------------------------
    # Decision functions — one per condition
    # ------------------------------------------------------------------

    def decide_baseline(self) -> str:
        """Pure need-based. NO substrate signal. No cooperation, no building."""
        if self.hunger > 0.8:  return "forage"
        if self.energy < 0.15: return "rest"
        if self.hunger > 0.5:  return "forage"
        if self.energy < 0.4:  return "rest"
        return "explore"

    def decide_with_signal(self, signal: float,
                           coordination_blocked: bool = False) -> str:
        """Continuous substrate-influenced decision."""
        coord = 0.5 * (1.0 + max(-1.0, min(1.0, signal)))
        if self.hunger > 0.8:  return "forage"
        if self.energy < 0.15: return "rest"
        need_pressure = (self.hunger + self.stress) / 2.0
        threshold = 0.3 + 0.4 * need_pressure
        if not coordination_blocked and coord > threshold and self.stress < 0.6:
            return "cooperate"
        if self.energy > 0.5 and coord > 0.45:
            return "build"
        if self.hunger > 0.5:  return "forage"
        if self.energy < 0.4:  return "rest"
        return "explore"

    def apply_action(self, action: str, signal: float) -> None:
        coord_eff = 0.8 + 0.4 * max(0.0, signal)
        h_before = self.hunger
        e_before = self.energy

        if action == "rest":
            self.energy = min(1.0, self.energy + 0.12)
            self.stress = max(0.0, self.stress - 0.05)
        elif action == "forage":
            self.hunger = max(0.0, self.hunger - 0.18)
            self.energy = max(0.0, self.energy - 0.08)
        elif action == "explore":
            self.hunger = min(1.0, self.hunger + 0.04)
            self.energy = max(0.0, self.energy - 0.06)
            self.stress = max(0.0, self.stress - 0.02)
        elif action == "build":
            self.hunger = min(1.0, self.hunger + 0.05)
            self.energy = max(0.0, self.energy - 0.1 / coord_eff)
        elif action == "cooperate":
            self.stress = max(0.0, self.stress - 0.1 * coord_eff)
            self.hunger = min(1.0, self.hunger + 0.03)
            self.energy = max(0.0, self.energy - 0.04 / coord_eff)

        # Base hunger tick (metabolic cost)
        self.hunger = min(1.0, self.hunger + 0.02)
        if self.hunger >= 0.75:
            self.hunger_spike_count += 1

        # Track resource flow
        self.total_hunger_reduced += max(0.0, h_before - self.hunger)
        self.total_energy_spent   += max(0.0, e_before - self.energy)


def _make_agents(rng: np.random.Generator, n: int) -> list[Agent]:
    agents = []
    for i in range(n):
        agents.append(Agent(
            name=f"agent_{i}",
            x=10.0 + i * 8.0,
            y=25.0,
            hunger=float(rng.uniform(0.25, 0.45)),
            energy=float(rng.uniform(0.65, 0.85)),
            stress=float(rng.uniform(0.15, 0.30)),
        ))
    return agents


# ---------------------------------------------------------------------------
# Signal computation
# ---------------------------------------------------------------------------

def _compute_signal(condition: str, field, prop, relax, measure_coord) -> float:
    if condition == "spectral":
        obs = compute_spectral_transport_observable(field, prop, relax)
        return float(obs.c_spectral)
    elif condition == "legacy_q":
        q_obs = compute_theoretical_q(field, prop, relax, measure_coord)
        # Sigmoid normalisation — bounded for any Q value
        return float(2.0 / (1.0 + math.exp(-q_obs.q_value / 5.0)) - 1.0)
    else:
        raise ValueError(f"_compute_signal called for condition {condition}")


# ---------------------------------------------------------------------------
# Single trial
# ---------------------------------------------------------------------------

def run_trial(
    seed: int,
    condition: str,
    scenario: str,
    tau: float,
    cfg: ExperimentConfig,
) -> dict[str, Any]:
    """
    Run one complete trial. Fully self-contained — no shared mutable state.

    Returns a dict of metrics.
    """
    n_ticks = {
        "stable":    cfg.n_ticks_stable,
        "dynamic":   cfg.n_ticks_dynamic,
        "disrupted": cfg.n_ticks_disrupted,
    }[scenario]

    # Build RNG — identical initial conditions for all conditions within a trial
    rng = np.random.default_rng(seed)
    field, prop, relax, measure_coord = _build_field(rng, tau, cfg.c, cfg)
    # Build agents with SAME rng (rng is now advanced past bumps; reproducible)
    agents = _make_agents(rng, cfg.n_agents)

    # Pre-compute ablation signal series (time-reversal of spectral signals)
    ablation_signals: list[float] = []
    if condition == "ablation":
        # Pre-run identical field with identical agents to collect spectral signals
        rng2 = np.random.default_rng(seed)
        f2, p2, r2, mc2 = _build_field(rng2, tau, cfg.c, cfg)
        agents2 = _make_agents(rng2, cfg.n_agents)
        rng_dist2 = np.random.default_rng(seed + 10_000)  # disturbance rng

        # Scenario 2 disturbance positions (same seed)
        dist_positions = []
        if scenario in ("dynamic", "disrupted"):
            dist_positions = [
                (float(rng_dist2.uniform(5.0, 45.0)), float(rng_dist2.uniform(5.0, 45.0)))
                for _ in range(4)
            ]

        for t in range(n_ticks):
            sig2 = _compute_signal("spectral", f2, p2, r2, mc2)
            ablation_signals.append(sig2)
            for a in agents2:
                action2 = a.decide_with_signal(sig2)
                a.apply_action(action2, sig2)
                amp2 = (a.hunger + a.stress) / 2.0 * 1.5
                f2 = apply_perturbation(f2, PhysicalCoordinate(a.x, a.y, 0.0), amp2, 3.0)
            if scenario == "dynamic":
                if t == 15 and len(dist_positions) >= 2:
                    f2 = apply_perturbation(f2, PhysicalCoordinate(dist_positions[0][0], dist_positions[0][1], 0.0), 2.0, 4.0)
                    f2 = apply_perturbation(f2, PhysicalCoordinate(dist_positions[1][0], dist_positions[1][1], 0.0), 2.0, 4.0)
                if t == 35 and len(dist_positions) >= 4:
                    f2 = apply_perturbation(f2, PhysicalCoordinate(dist_positions[2][0], dist_positions[2][1], 0.0), 2.0, 4.0)
                    f2 = apply_perturbation(f2, PhysicalCoordinate(dist_positions[3][0], dist_positions[3][1], 0.0), 2.0, 4.0)
            f2 = evolve_field(f2, p2, r2)
        # Time-reversal
        ablation_signals = list(reversed(ablation_signals))

    # Disturbance positions for this trial's scenario
    rng_dist = np.random.default_rng(seed + 10_000)
    dist_positions = []
    if scenario in ("dynamic", "disrupted"):
        dist_positions = [
            (float(rng_dist.uniform(5.0, 45.0)), float(rng_dist.uniform(5.0, 45.0)))
            for _ in range(4)
        ]

    # Bookkeeping
    action_counts: dict[str, int] = {
        a: 0 for a in ["rest", "forage", "explore", "build", "cooperate"]
    }

    # Main simulation loop
    for tick in range(n_ticks):
        coordination_blocked = (scenario == "disrupted" and 20 <= tick <= 29)

        # Field reset at tick 25 for disrupted scenario
        if scenario == "disrupted" and tick == 25:
            rng_reset = np.random.default_rng(seed)
            field, prop, relax, measure_coord = _build_field(rng_reset, tau, cfg.c, cfg)

        # Compute signal
        if condition == "baseline":
            signal = 0.0  # unused in baseline decision
        elif condition == "ablation":
            signal = ablation_signals[tick]
        else:
            signal = _compute_signal(condition, field, prop, relax, measure_coord)

        # Agent decisions
        for agent in agents:
            if condition == "baseline":
                action = agent.decide_baseline()
                agent.apply_action(action, 0.0)
            else:
                action = agent.decide_with_signal(signal, coordination_blocked)
                agent.apply_action(action, signal)
            action_counts[action] += 1

        # Agents perturb field (all conditions: coupling is always active)
        for agent in agents:
            amp = (agent.hunger + agent.stress) / 2.0 * 1.5
            field = apply_perturbation(
                field, PhysicalCoordinate(agent.x, agent.y, 0.0), amp, 3.0
            )

        # Scenario disturbances
        if scenario == "dynamic":
            if tick == 15 and len(dist_positions) >= 2:
                field = apply_perturbation(field, PhysicalCoordinate(dist_positions[0][0], dist_positions[0][1], 0.0), 2.0, 4.0)
                field = apply_perturbation(field, PhysicalCoordinate(dist_positions[1][0], dist_positions[1][1], 0.0), 2.0, 4.0)
            if tick == 35 and len(dist_positions) >= 4:
                field = apply_perturbation(field, PhysicalCoordinate(dist_positions[2][0], dist_positions[2][1], 0.0), 2.0, 4.0)
                field = apply_perturbation(field, PhysicalCoordinate(dist_positions[3][0], dist_positions[3][1], 0.0), 2.0, 4.0)

        field = evolve_field(field, prop, relax)

    # Collect metrics
    n = len(agents)
    total_at = cfg.n_agents * n_ticks

    mean_final_hunger = sum(a.hunger for a in agents) / n
    mean_final_energy = sum(a.energy for a in agents) / n
    mean_final_stress = sum(a.stress for a in agents) / n
    task_success_rate = sum(1 for a in agents if a.hunger_spike_count == 0) / n
    mean_stress_reduction = sum(a._initial_stress - a.stress for a in agents) / n

    total_hunger_reduced = sum(a.total_hunger_reduced for a in agents)
    resource_efficiency = total_hunger_reduced / total_at

    # Validate — no numerical errors
    valid = all(0.0 <= a.hunger <= 1.0 and 0.0 <= a.energy <= 1.0 for a in agents)

    return {
        "seed":               seed,
        "condition":          condition,
        "scenario":           scenario,
        "tau":                tau,
        "n_ticks":            n_ticks,
        "n_agents":           cfg.n_agents,
        "valid":              valid,
        # PRIMARY
        "mean_final_hunger":  round(mean_final_hunger, 6),
        # SECONDARY
        "mean_final_energy":  round(mean_final_energy, 6),
        "mean_final_stress":  round(mean_final_stress, 6),
        "task_success_rate":  round(task_success_rate, 6),
        "coordination_rate":  round(action_counts["cooperate"] / total_at, 6),
        "build_rate":         round(action_counts["build"] / total_at, 6),
        "forage_rate":        round(action_counts["forage"] / total_at, 6),
        "rest_rate":          round(action_counts["rest"] / total_at, 6),
        "explore_rate":       round(action_counts["explore"] / total_at, 6),
        "resource_efficiency":round(resource_efficiency, 6),
        "mean_stress_reduction": round(mean_stress_reduction, 6),
        "action_counts":      action_counts,
    }


# ---------------------------------------------------------------------------
# Experiment orchestration
# ---------------------------------------------------------------------------

def run_experiment(cfg: ExperimentConfig, smoke_only: bool = False) -> list[dict]:
    """Run the full repeated-trial experiment. Returns list of raw trial dicts."""
    n_trials = 1 if smoke_only else cfg.n_trials
    all_trials: list[dict] = []
    total = n_trials * len(cfg.conditions) * len(cfg.scenarios)
    done = 0
    t0 = time.time()

    for scenario in cfg.scenarios:
        for condition in cfg.conditions:
            for trial_idx in range(n_trials):
                seed = cfg.base_seed + trial_idx
                result = run_trial(seed, condition, scenario, cfg.tau, cfg)
                all_trials.append(result)
                done += 1
                if done % 20 == 0 or smoke_only:
                    elapsed = time.time() - t0
                    print(f"  [{done}/{total}] {scenario}/{condition} seed={seed} "
                          f"hunger={result['mean_final_hunger']:.3f} "
                          f"elapsed={elapsed:.1f}s")

    return all_trials


def run_tau_scan(cfg: ExperimentConfig, smoke_only: bool = False) -> list[dict]:
    """Run tau calibration scan: spectral condition, scenario 1, repeated trials."""
    n_trials = 1 if smoke_only else cfg.tau_scan_trials
    scan_trials: list[dict] = []
    for tau in cfg.tau_scan_values:
        for trial_idx in range(n_trials):
            seed = cfg.tau_scan_base_seed + trial_idx
            result = run_trial(seed, "spectral", "stable", tau, cfg)
            scan_trials.append(result)
        mean_h = sum(r["mean_final_hunger"] for r in scan_trials
                     if r["tau"] == tau) / n_trials
        mean_c = sum(r["coordination_rate"] for r in scan_trials
                     if r["tau"] == tau) / n_trials
        print(f"  tau={tau:.2f}  mean_hunger={mean_h:.3f}  "
              f"coordination={mean_c:.1%}")
    return scan_trials


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def _aggregate(trials: list[dict], condition: str, scenario: str,
               metric: str) -> dict:
    vals = [t[metric] for t in trials
            if t["condition"] == condition
            and t["scenario"] == scenario
            and t.get("valid", True)]
    if not vals:
        return {"n": 0, "mean": None, "std": None, "min": None, "max": None}
    arr = np.array(vals)
    return {
        "n":    len(arr),
        "mean": float(np.mean(arr)),
        "std":  float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0,
        "min":  float(np.min(arr)),
        "max":  float(np.max(arr)),
    }


def build_summary(trials: list[dict], tau_scan: list[dict],
                  cfg: ExperimentConfig) -> dict:
    summary: dict[str, Any] = {"config": asdict(cfg), "conditions": {}, "tau_scan": {}}
    for scenario in cfg.scenarios:
        summary["conditions"][scenario] = {}
        for condition in cfg.conditions:
            summary["conditions"][scenario][condition] = {
                metric: _aggregate(trials, condition, scenario, metric)
                for metric in ["mean_final_hunger", "mean_final_energy",
                                "mean_final_stress", "task_success_rate",
                                "coordination_rate", "build_rate", "forage_rate",
                                "resource_efficiency"]
            }
    for tau in cfg.tau_scan_values:
        tau_trials = [t for t in tau_scan if t["tau"] == tau]
        h_vals = [t["mean_final_hunger"] for t in tau_trials]
        c_vals = [t["coordination_rate"] for t in tau_trials]
        summary["tau_scan"][str(tau)] = {
            "n":           len(h_vals),
            "mean_hunger": float(np.mean(h_vals)) if h_vals else None,
            "std_hunger":  float(np.std(h_vals, ddof=1)) if len(h_vals) > 1 else 0.0,
            "mean_coord":  float(np.mean(c_vals)) if c_vals else None,
        }
    return summary


def print_summary_table(summary: dict, cfg: ExperimentConfig) -> None:
    for scenario in cfg.scenarios:
        print(f"\n  Scenario: {scenario}")
        print(f"  {'condition':>12}  {'hunger(mean)':>12}  {'hunger(std)':>11}  "
              f"{'task_ok%':>8}  {'coord%':>7}  {'forage%':>7}")
        print("  " + "-" * 72)
        for cond in cfg.conditions:
            h = summary["conditions"][scenario][cond]["mean_final_hunger"]
            t = summary["conditions"][scenario][cond]["task_success_rate"]
            c = summary["conditions"][scenario][cond]["coordination_rate"]
            f = summary["conditions"][scenario][cond]["forage_rate"]
            print(f"  {cond:>12}  {h['mean']:>12.4f}  {h['std']:>11.4f}  "
                  f"{t['mean']:>8.1%}  {c['mean']:>7.1%}  {f['mean']:>7.1%}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 10 experiment runner")
    parser.add_argument("--smoke-only", action="store_true",
                        help="Run 1-trial smoke test only")
    parser.add_argument("--trials", type=int, default=None,
                        help="Override number of trials")
    args = parser.parse_args()

    cfg = ExperimentConfig()
    if args.trials is not None:
        cfg.n_trials = args.trials
        cfg.tau_scan_trials = max(1, args.trials // 3)

    # Run existing modal validation tests
    print("\n--- Modal Validation Tests ---")
    try:
        from sim_world.domains.physical_field.test_modal_validation import run_all
        results = run_all()
        passed = sum(1 for v in results.values() if v == "PASS")
        print(f"  Modal tests: {passed}/{len(results)} passed\n")
    except Exception as e:
        print(f"  Modal tests failed to run: {e}\n")

    print("=" * 70)
    print(f"  PHASE 10 EXPERIMENT RUNNER")
    print(f"  Mode: {'SMOKE TEST (1 trial)' if args.smoke_only else f'FULL ({cfg.n_trials} trials)'}")
    print(f"  Conditions: {cfg.conditions}")
    print(f"  Scenarios:  {cfg.scenarios}")
    print(f"  Tau (main): {cfg.tau}")
    print(f"  Seeds:      {cfg.base_seed} to {cfg.base_seed + cfg.n_trials - 1}")
    print("=" * 70)

    t_start = time.time()

    # Main experiment
    print("\n--- Main Experiment ---")
    trials = run_experiment(cfg, smoke_only=args.smoke_only)

    # Tau scan
    print("\n--- Tau Scan ---")
    tau_scan = run_tau_scan(cfg, smoke_only=args.smoke_only)

    elapsed = time.time() - t_start
    print(f"\n  Total elapsed: {elapsed:.1f}s")

    # Build summary
    summary = build_summary(trials, tau_scan, cfg)

    # Print summary table
    print("\n--- Summary ---")
    print_summary_table(summary, cfg)

    # Save
    raw_path   = os.path.join(_HERE, "phase10_raw_trials.json")
    jsonl_path = os.path.join(_HERE, "phase10_raw_trials.jsonl")
    sum_path   = os.path.join(_HERE, "phase10_summary.json")

    all_data = trials + tau_scan
    with open(raw_path, "w") as f:
        json.dump(all_data, f, indent=2)
    with open(jsonl_path, "w") as f:
        for t in all_data:
            f.write(json.dumps(t) + "\n")
    with open(sum_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n  Raw trials  → {raw_path}  ({len(all_data)} records)")
    print(f"  JSONL       → {jsonl_path}")
    print(f"  Summary     → {sum_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
