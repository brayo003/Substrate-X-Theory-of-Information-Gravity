"""
Deterministic Substrate Demo — No LLM Required
===============================================

Runs a 50-tick A/B experiment:
  World A: τ = 0.3  (fast relaxation  → Q < 0, overdamped substrate)
  World B: τ = 3.0  (slow relaxation  → Q > 0, coherent substrate)

Agents are fully deterministic — their behavior is driven by a simple
need-based rule set that explicitly reads the Q value from the substrate.
No Ollama, no Transformers, no network calls.

Output:
  - Per-tick console table showing Q regime, agent actions, need states
  - Final summary comparing behavioral divergence between worlds
  - JSON results written to demo_results.json

The point: show that substrate Q directly causes different behavioral
outcomes even when agents are identical, initial conditions are identical,
and there is no random seed difference.
"""

from __future__ import annotations

import json
import math
import sys
import os
from dataclasses import dataclass, field, asdict
from typing import Any

# ---------------------------------------------------------------------------
# Path setup — allow running from sim_world/ directly or as a module
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

import numpy as np

from sim_world.domains.physical_field.physical_field_dynamics import (
    initialize_field_state,
    evolve_field,
    apply_perturbation,
    compute_theoretical_q,
    compute_spectral_transport_observable,
)
from sim_world.domains.physical_field.physical_field_models import (
    InformationDensityField,
    PhysicalCoordinate,
    PropagationParameters,
    RelaxationParameters,
)


# ---------------------------------------------------------------------------
# Agent: purely deterministic, reads substrate Q
# ---------------------------------------------------------------------------

ACTIONS = ["rest", "forage", "explore", "build", "cooperate"]

@dataclass
class Agent:
    name: str
    x: float
    y: float
    hunger: float = 0.4
    energy: float = 0.8
    stress: float = 0.2
    action_history: list[str] = field(default_factory=list)
    q_history: list[float] = field(default_factory=list)

    def decide(self, q_value: float, regime: str, c_spectral: float) -> str:
        """
        Deterministic rule-based decision using substrate state.

        The substrate modifies CAPABILITY, not action.  Specifically:

        coordination_capacity = 0.5 * (1 + c_spectral)   ∈ [0, 1]

        This is a continuous probability that a coordination-requiring action
        (cooperate, build) can be attempted.  The agent still selects based
        on its own needs — the substrate just modulates how much coordination
        capability is available.

        This is NOT a binary regime switch.  An agent in c_spectral=-0.3
        can still occasionally cooperate; an agent in c_spectral=+0.9 can
        still forage when hungry.
        """
        self.q_history.append(q_value)
        coordination_capacity = 0.5 * (1.0 + c_spectral)   # 0..1

        # Critical need: always overrides substrate
        if self.hunger > 0.8:
            return "forage"
        if self.energy < 0.15:
            return "rest"

        # Substrate modulates coordination threshold.
        # Agent tries to cooperate if coordination_capacity exceeds a need-adjusted threshold.
        # Threshold rises when agent is stressed or hungry (needs demand local action).
        need_pressure = (self.hunger + self.stress) / 2.0
        effective_threshold = 0.3 + 0.4 * need_pressure   # rises from 0.3 (rested) to 0.7 (stressed)

        if coordination_capacity > effective_threshold and self.stress < 0.6:
            return "cooperate"

        # Build requires both energy and moderate coordination
        if self.energy > 0.5 and coordination_capacity > 0.45:
            return "build"

        # Fallback to immediate local actions
        if self.hunger > 0.5:
            return "forage"
        if self.energy < 0.4:
            return "rest"
        return "explore"

    def apply_action(self, action: str, c_spectral: float) -> None:
        """Update needs based on action. Substrate coherence modulates efficiency."""
        # In coherent substrate, coordination actions are more effective
        # (better signal propagation = less coordination overhead)
        coord_efficiency = 0.8 + 0.4 * max(0.0, c_spectral)   # 0.8..1.2
        base_efficiency  = 1.0  # local actions unaffected by substrate

        if action == "rest":
            self.energy = min(1.0, self.energy + 0.12 * base_efficiency)
            self.stress = max(0.0, self.stress - 0.05)
        elif action == "forage":
            self.hunger = max(0.0, self.hunger - 0.18 * base_efficiency)
            self.energy = max(0.0, self.energy - 0.08)
        elif action == "explore":
            self.hunger = min(1.0, self.hunger + 0.04)
            self.energy = max(0.0, self.energy - 0.06)
            self.stress = max(0.0, self.stress - 0.02)
        elif action == "build":
            self.hunger = min(1.0, self.hunger + 0.05)
            self.energy = max(0.0, self.energy - 0.1 / coord_efficiency)
        elif action == "cooperate":
            self.stress = max(0.0, self.stress - 0.1 * coord_efficiency)
            self.hunger = min(1.0, self.hunger + 0.03)
            self.energy = max(0.0, self.energy - 0.04 / coord_efficiency)

        # Base hunger tick
        self.hunger = min(1.0, self.hunger + 0.02)
        self.action_history.append(action)

    def perturbation_strength(self) -> float:
        """How much this agent perturbs the field — driven by need intensity."""
        return (self.hunger + self.stress) / 2.0


# ---------------------------------------------------------------------------
# World: wraps kernel + field + agents
# ---------------------------------------------------------------------------

@dataclass
class WorldConfig:
    name: str
    tau: float
    c: float = 1.0
    n_agents: int = 5
    n_ticks: int = 50
    grid_nx: int = 30
    grid_ny: int = 30


@dataclass
class TickRecord:
    tick: int
    q_value: float
    regime: str
    spectral_q: float
    actions: dict[str, str]
    agent_states: dict[str, dict[str, float]]


def _make_initial_field(cfg: WorldConfig) -> InformationDensityField:
    """
    Create a spatially non-uniform initial field so that ∇ln(s) ≠ 0 from the start.

    We initialise a flat field, then immediately stamp several Gaussian bumps
    at known positions so the gradient landscape is rich before any agent acts.
    The bump amplitude is tuned so that the resulting |∇ln s|² crosses the
    Q = 0 threshold (4c²τ²|∇ln s|² = 1) for the high-τ world but not the
    low-τ world, giving us genuine regime separation from tick 0.

    Threshold condition:   |∇ln s|² > 1 / (4 c² τ²)
    For c=1, τ=0.3:  threshold = 1/(4·0.09) ≈ 2.78
    For c=1, τ=3.0:  threshold = 1/(4·9.0)  ≈ 0.028   ← much easier to exceed
    """
    field_state = initialize_field_state(
        x_range=(0.0, 50.0),
        y_range=(0.0, 50.0),
        nx=cfg.grid_nx,
        ny=cfg.grid_ny,
        initial_value=1.0,
        dt=0.05,          # smaller dt for stability
    )
    physical_volume = 50.0 * 50.0 * 1.0
    field = InformationDensityField(
        state=field_state,
        information_quantity=1.0,
        physical_volume=physical_volume,
        information_units="bits",
        spatial_units="m",
        density_units="bits/m³",
    )

    # Stamp initial structure — 4 Gaussian peaks with steep gradients
    # Width=3.0 m over a 50 m grid with 30 points (dx≈1.7m) gives sharp gradients
    bump_positions = [
        PhysicalCoordinate(x=12.0, y=12.0, z=0.0),
        PhysicalCoordinate(x=38.0, y=12.0, z=0.0),
        PhysicalCoordinate(x=12.0, y=38.0, z=0.0),
        PhysicalCoordinate(x=38.0, y=38.0, z=0.0),
    ]
    for pos in bump_positions:
        field = apply_perturbation(field, pos, perturbation_amplitude=3.0, perturbation_width=3.0)

    return field


def run_world(cfg: WorldConfig) -> list[TickRecord]:
    """Run one complete world simulation."""

    field = _make_initial_field(cfg)
    prop_params = PropagationParameters(c_nominal=cfg.c)
    relax_params = RelaxationParameters(tau_nominal=cfg.tau)

    # --- Agents with identical initial state across both worlds ---
    # Positions chosen to sit near the gradient ridges between the initial bumps
    # so that perturbations from activity reinforce the gradient structure
    agents = [
        Agent(name=f"agent_{i}", x=10.0 + i * 8.0, y=25.0,
              hunger=0.3 + i * 0.05, energy=0.8 - i * 0.04, stress=0.2 + i * 0.03)
        for i in range(cfg.n_agents)
    ]

    # Measurement point: flank of the top-left bump — steepest gradient zone
    # At dx≈1.7m, the Gaussian flank at ~1 sigma (3m from centre of bump at 12,12)
    # is where |∇ln s| is maximised
    measure_coord = PhysicalCoordinate(x=15.0, y=12.0, z=0.0)

    records: list[TickRecord] = []

    for tick in range(cfg.n_ticks):
        # 1. Compute Q at measurement point (local gradient diagnostic, kept for display)
        q_obs = compute_theoretical_q(field, prop_params, relax_params, measure_coord)
        q_value = q_obs.q_value
        regime = q_obs.regime

        # Spectral observable — corrected: background-subtracted, C_spectral computed
        spectral = compute_spectral_transport_observable(field, prop_params, relax_params)
        spectral_q = spectral.c_spectral   # C_spectral ∈ [-1, +1], no fallback needed

        # 2. Each agent decides and acts based on substrate c_spectral
        actions: dict[str, str] = {}
        for agent in agents:
            action = agent.decide(q_value, regime, spectral_q)
            agent.apply_action(action, spectral_q)
            actions[agent.name] = action

            # 3. Agent activity perturbs the field
            perturbation_amp = agent.perturbation_strength() * 1.5   # stronger coupling
            agent_coord = PhysicalCoordinate(x=agent.x, y=agent.y, z=0.0)
            field = apply_perturbation(field, agent_coord, perturbation_amp, perturbation_width=3.0)

        # 4. Evolve field forward
        field = evolve_field(field, prop_params, relax_params)

        # Record
        agent_states = {
            a.name: {"hunger": round(a.hunger, 3), "energy": round(a.energy, 3), "stress": round(a.stress, 3)}
            for a in agents
        }
        records.append(TickRecord(
            tick=tick,
            q_value=round(q_value, 4),
            regime=regime,
            spectral_q=round(spectral_q, 4),
            actions=actions,
            agent_states=agent_states,
        ))

    return records


# ---------------------------------------------------------------------------
# Analysis helpers
# ---------------------------------------------------------------------------

def action_distribution(records: list[TickRecord]) -> dict[str, int]:
    counts: dict[str, int] = {a: 0 for a in ACTIONS}
    for r in records:
        for action in r.actions.values():
            counts[action] = counts.get(action, 0) + 1
    return counts


def regime_distribution(records: list[TickRecord]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for r in records:
        counts[r.regime] = counts.get(r.regime, 0) + 1
    return counts


def final_needs(records: list[TickRecord]) -> dict[str, dict[str, float]]:
    """Return mean final needs across all agents from last tick."""
    last = records[-1].agent_states
    means = {"hunger": 0.0, "energy": 0.0, "stress": 0.0}
    for state in last.values():
        for key in means:
            means[key] += state[key]
    n = len(last)
    return {k: round(v / n, 3) for k, v in means.items()}


def cooperation_rate(records: list[TickRecord]) -> float:
    """Fraction of agent-ticks spent cooperating."""
    total = 0
    cooperate = 0
    for r in records:
        for action in r.actions.values():
            total += 1
            if action == "cooperate":
                cooperate += 1
    return round(cooperate / total, 3) if total else 0.0


def build_rate(records: list[TickRecord]) -> float:
    total = 0
    build = 0
    for r in records:
        for action in r.actions.values():
            total += 1
            if action == "build":
                build += 1
    return round(build / total, 3) if total else 0.0


def q_mean(records: list[TickRecord]) -> float:
    return round(sum(r.q_value for r in records) / len(records), 4)


# ---------------------------------------------------------------------------
# Printer
# ---------------------------------------------------------------------------

def print_tick_table(records: list[TickRecord], world_name: str, every: int = 10) -> None:
    """Print a sample of tick records as a table."""
    print(f"\n{'='*72}")
    print(f"  {world_name}  — tick sample (every {every} ticks)")
    print(f"{'='*72}")
    header = f"{'tick':>5}  {'Q':>8}  {'regime':>10}  {'actions (agent_0..4)'}"
    print(header)
    print("-" * 72)
    for r in records:
        if r.tick % every == 0:
            action_str = " | ".join(r.actions[k] for k in sorted(r.actions))
            regime_str = r.regime[:10]
            print(f"{r.tick:>5}  {r.q_value:>8.4f}  {regime_str:>10}  {action_str}")
    print("-" * 72)


def print_summary(world_name: str, records: list[TickRecord]) -> None:
    dist = action_distribution(records)
    regime = regime_distribution(records)
    needs = final_needs(records)
    coop = cooperation_rate(records)
    bld = build_rate(records)
    q_avg = q_mean(records)

    print(f"\n--- {world_name} SUMMARY ---")
    print(f"  Mean Q value       : {q_avg}")
    print(f"  Regime ticks       : {regime}")
    print(f"  Action distribution: {dist}")
    print(f"  Cooperation rate   : {coop:.1%}")
    print(f"  Build rate         : {bld:.1%}")
    print(f"  Final mean needs   : hunger={needs['hunger']}, energy={needs['energy']}, stress={needs['stress']}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    cfg_a = WorldConfig(name="World A — τ=0.5  (overdamped)", tau=0.5,  c=1.0, n_agents=5, n_ticks=50)
    cfg_b = WorldConfig(name="World B — τ=10.0 (coherent)",  tau=10.0, c=1.0, n_agents=5, n_ticks=50)

    print("\n" + "=" * 72)
    print("  SUBSTRATE DEMO: Deterministic A/B Experiment")
    print("  Same agents. Same initial needs. Same c. Only τ differs.")
    print("  Watching whether substrate Q changes emergent behavior.")
    print("=" * 72)

    print(f"\n[1/2] Running {cfg_a.name} ...")
    records_a = run_world(cfg_a)
    print("  Done.")

    print(f"\n[2/2] Running {cfg_b.name} ...")
    records_b = run_world(cfg_b)
    print("  Done.")

    # Print tick samples
    print_tick_table(records_a, cfg_a.name, every=5)
    print_tick_table(records_b, cfg_b.name, every=5)

    # Print summaries
    print_summary(cfg_a.name, records_a)
    print_summary(cfg_b.name, records_b)

    # Divergence analysis
    coop_a = cooperation_rate(records_a)
    coop_b = cooperation_rate(records_b)
    bld_a  = build_rate(records_a)
    bld_b  = build_rate(records_b)
    q_a    = q_mean(records_a)
    q_b    = q_mean(records_b)

    print("\n" + "=" * 72)
    print("  DIVERGENCE ANALYSIS")
    print("=" * 72)
    print(f"  Mean Q:            A={q_a:>8.4f}   B={q_b:>8.4f}   Δ={q_b-q_a:>+8.4f}")
    print(f"  Cooperation rate:  A={coop_a:>8.1%}   B={coop_b:>8.1%}   Δ={coop_b-coop_a:>+8.1%}")
    print(f"  Build rate:        A={bld_a:>8.1%}   B={bld_b:>8.1%}   Δ={bld_b-bld_a:>+8.1%}")

    needs_a = final_needs(records_a)
    needs_b = final_needs(records_b)
    print(f"  Final hunger:      A={needs_a['hunger']:>8.3f}   B={needs_b['hunger']:>8.3f}   Δ={needs_b['hunger']-needs_a['hunger']:>+8.3f}")
    print(f"  Final energy:      A={needs_a['energy']:>8.3f}   B={needs_b['energy']:>8.3f}   Δ={needs_b['energy']-needs_a['energy']:>+8.3f}")
    print(f"  Final stress:      A={needs_a['stress']:>8.3f}   B={needs_b['stress']:>8.3f}   Δ={needs_b['stress']-needs_a['stress']:>+8.3f}")

    regime_a = regime_distribution(records_a)
    regime_b = regime_distribution(records_b)
    total_ticks = cfg_a.n_ticks
    print(f"\n  Regime ticks A: {regime_a}  (of {total_ticks})")
    print(f"  Regime ticks B: {regime_b}  (of {total_ticks})")

    if abs(coop_b - coop_a) > 0.01 or abs(bld_b - bld_a) > 0.01:
        print("\n  ✓ BEHAVIORAL DIVERGENCE CONFIRMED")
        print("    Substrate Q causally influenced agent behavior.")
        print("    Different τ → different Q regime → different emergent action distribution.")
    else:
        print("\n  ✗ No significant divergence detected.")
        print("    Consider increasing n_agents or n_ticks for stronger signal.")

    # Save JSON results
    results = {
        "world_a": {
            "config": {"name": cfg_a.name, "tau": cfg_a.tau, "c": cfg_a.c},
            "mean_q": q_a,
            "cooperation_rate": coop_a,
            "build_rate": bld_a,
            "final_needs": needs_a,
            "regime_distribution": regime_a,
            "action_distribution": action_distribution(records_a),
        },
        "world_b": {
            "config": {"name": cfg_b.name, "tau": cfg_b.tau, "c": cfg_b.c},
            "mean_q": q_b,
            "cooperation_rate": coop_b,
            "build_rate": bld_b,
            "final_needs": needs_b,
            "regime_distribution": regime_b,
            "action_distribution": action_distribution(records_b),
        },
        "divergence": {
            "delta_q": round(q_b - q_a, 4),
            "delta_cooperation": round(coop_b - coop_a, 4),
            "delta_build": round(bld_b - bld_a, 4),
            "delta_hunger": round(needs_b["hunger"] - needs_a["hunger"], 4),
            "delta_energy": round(needs_b["energy"] - needs_a["energy"], 4),
            "delta_stress": round(needs_b["stress"] - needs_a["stress"], 4),
        }
    }

    out_path = os.path.join(_HERE, "demo_results.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved → {out_path}")
    print("=" * 72)


if __name__ == "__main__":
    main()
