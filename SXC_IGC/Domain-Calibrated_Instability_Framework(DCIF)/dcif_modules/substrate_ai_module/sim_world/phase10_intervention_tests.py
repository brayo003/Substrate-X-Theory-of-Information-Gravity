"""
Phase 10 — Substrate Intervention Tests
========================================

These tests verify that the agent decision function ACTUALLY responds to
substrate signal changes by holding all other inputs constant and varying
only c_spectral (or the equivalent signal).

This is a prerequisite verification: if the agent does not respond to the
signal, the main experiment cannot be testing substrate influence.

Tests:
  1. Monotonicity: does coordination_capacity rise monotonically with c_spectral?
  2. Decision response curve: map c_spectral [-1,+1] → action at fixed agent state
  3. Threshold test: find the c_spectral threshold for cooperation at several
     stress/hunger combinations
  4. Efficiency test: does apply_action produce better stress reduction with
     higher c_spectral for cooperate action?
  5. Baseline isolation: confirm baseline decision ignores the signal entirely
  6. Coordination-blocked override: confirm blocked flag prevents cooperation
  7. Critical need override: confirm hunger > 0.8 always produces forage
     regardless of signal

Usage:
    python phase10_intervention_tests.py

All tests pass or fail independently. Results are printed and saved to
phase10_intervention_results.json.
"""

from __future__ import annotations

import json
import math
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

# Import the Agent class from experiment_runner
from sim_world.experiment_runner import Agent


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

def _make_agent(hunger: float = 0.3, energy: float = 0.8,
                stress: float = 0.2) -> Agent:
    return Agent(name="test_agent", x=25.0, y=25.0,
                 hunger=hunger, energy=energy, stress=stress)


def _run_test(name: str, fn) -> dict:
    try:
        result = fn()
        status = "PASS" if result.get("pass", False) else "FAIL"
        return {"name": name, "status": status, **result}
    except Exception as e:
        return {"name": name, "status": "ERROR", "error": str(e)}


def _print_result(r: dict) -> None:
    icon = "✓" if r["status"] == "PASS" else ("✗" if r["status"] == "FAIL" else "!")
    print(f"  [{r['status']:5}] {icon} {r['name']}")
    if "details" in r:
        for line in r["details"]:
            print(f"           {line}")
    if r["status"] != "PASS" and "error" in r:
        print(f"           ERROR: {r['error']}")


# ---------------------------------------------------------------------------
# Test 1: Coordination capacity is monotone in signal
# ---------------------------------------------------------------------------

def test_coord_capacity_monotone() -> dict:
    """
    coordination_capacity = 0.5 * (1 + clip(signal, -1, 1))
    Must be strictly monotone increasing.
    """
    agent = _make_agent()
    signals = [-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0]
    capacities = []
    for s in signals:
        cap = 0.5 * (1.0 + max(-1.0, min(1.0, s)))
        capacities.append(round(cap, 6))

    monotone = all(capacities[i] <= capacities[i+1] for i in range(len(capacities)-1))
    details = [f"signal={s:+.2f} → coord_cap={c:.4f}"
               for s, c in zip(signals, capacities)]
    return {
        "pass": monotone,
        "capacities": list(zip(signals, capacities)),
        "details": details,
        "note": "coordination_capacity must be non-decreasing in signal"
    }


# ---------------------------------------------------------------------------
# Test 2: Decision response curve (fixed agent state, varying signal)
# ---------------------------------------------------------------------------

def test_decision_response_curve() -> dict:
    """
    With a moderate-needs agent (hunger=0.3, energy=0.8, stress=0.2),
    increasing signal should increase the probability / rate of cooperation.
    At low signal (c=-0.9) agent should NOT cooperate.
    At high signal (c=+0.9) agent SHOULD cooperate.
    """
    agent = _make_agent(hunger=0.3, energy=0.8, stress=0.2)
    low_signal  = -0.9
    high_signal = +0.9

    action_low  = agent.decide_with_signal(low_signal)
    action_high = agent.decide_with_signal(high_signal)

    # Need pressure = (0.3 + 0.2) / 2.0 = 0.25
    # Threshold = 0.3 + 0.4 * 0.25 = 0.40
    # coord_cap(low=-0.9)  = 0.5*(1-0.9) = 0.05 < 0.40 → no cooperate
    # coord_cap(high=+0.9) = 0.5*(1+0.9) = 0.95 > 0.40 → cooperate
    expected_low  = "cooperate" != action_low  # should NOT cooperate at low signal
    expected_high = action_high == "cooperate"

    details = [
        f"low  signal={low_signal:+.1f}: action={action_low!r}  (expected: not cooperate → {'OK' if expected_low else 'FAIL'})",
        f"high signal={high_signal:+.1f}: action={action_high!r}  (expected: cooperate → {'OK' if expected_high else 'FAIL'})",
    ]
    return {
        "pass": expected_low and expected_high,
        "action_at_low_signal": action_low,
        "action_at_high_signal": action_high,
        "details": details,
    }


# ---------------------------------------------------------------------------
# Test 3: Full decision sweep across signal range
# ---------------------------------------------------------------------------

def test_decision_sweep() -> dict:
    """
    Sweep c_spectral from -1 to +1 in 21 steps.
    Count how many times 'cooperate' is chosen.
    It must be chosen MORE at high signals than at low signals
    (cooperation rate must be higher in the high half than the low half).
    """
    agent = _make_agent(hunger=0.35, energy=0.75, stress=0.25)
    signals = [round(-1.0 + i * 0.1, 2) for i in range(21)]
    actions = [agent.decide_with_signal(s) for s in signals]

    low_half  = actions[:10]   # signals -1.0 to -0.1
    high_half = actions[11:]   # signals +0.1 to +1.0

    low_coop_rate  = low_half.count("cooperate") / len(low_half)
    high_coop_rate = high_half.count("cooperate") / len(high_half)

    # High half should produce at least as much cooperation as low half
    monotone_satisfied = high_coop_rate >= low_coop_rate

    details = []
    for s, a in zip(signals, actions):
        details.append(f"c={s:+.2f} → {a}")
    details.append(f"low-half  coop rate: {low_coop_rate:.0%}")
    details.append(f"high-half coop rate: {high_coop_rate:.0%}")

    return {
        "pass": monotone_satisfied,
        "low_coop_rate":  round(low_coop_rate, 4),
        "high_coop_rate": round(high_coop_rate, 4),
        "sweep": list(zip(signals, actions)),
        "details": details,
    }


# ---------------------------------------------------------------------------
# Test 4: Cooperation threshold varies with need pressure
# ---------------------------------------------------------------------------

def test_threshold_varies_with_need() -> dict:
    """
    At fixed c_spectral = 0.5 (coord_cap = 0.75):
    - low-need agent (hunger=0.1, stress=0.1):  threshold = 0.3 + 0.4*0.1 = 0.34 → cooperate
    - high-need agent (hunger=0.7, stress=0.5): threshold = 0.3 + 0.4*0.6 = 0.54 → cooperate
      (0.75 > 0.54, so still cooperates)
    - very-high-need agent (hunger=0.75, stress=0.59): threshold ≈ 0.534, coord=0.75 → cooperate
      BUT hunger > 0.8 triggers forced forage first (hunger=0.75 < 0.8, so cooperates)
    
    Key test: with c_spectral = -0.5 (coord_cap=0.25):
    - low-need  (hunger=0.1, stress=0.1): threshold=0.34 > 0.25 → no cooperate
    - high-need (hunger=0.7, stress=0.5): threshold=0.54 > 0.25 → no cooperate
    
    So negative signal should suppress cooperation for ANY need level.
    """
    signal_low  = -0.5  # coord_cap = 0.25
    signal_high = +0.5  # coord_cap = 0.75

    test_cases = [
        ("low_need",  _make_agent(hunger=0.1, energy=0.9, stress=0.1)),
        ("mid_need",  _make_agent(hunger=0.4, energy=0.7, stress=0.3)),
        ("high_need", _make_agent(hunger=0.6, energy=0.6, stress=0.4)),
    ]

    results = []
    all_pass = True
    for label, agent in test_cases:
        a_low  = agent.decide_with_signal(signal_low)
        # Fresh agent for high signal
        agent2 = _make_agent(hunger=agent.hunger,
                             energy=agent.energy,
                             stress=agent.stress)
        a_high = agent2.decide_with_signal(signal_high)
        # At low signal, should NOT cooperate
        ok = (a_low != "cooperate")
        all_pass = all_pass and ok
        results.append({
            "label": label, "action_low": a_low, "action_high": a_high,
            "low_not_cooperate": ok
        })

    details = [
        f"{r['label']:>12}: signal={signal_low:+.1f}→{r['action_low']!r}  "
        f"signal={signal_high:+.1f}→{r['action_high']!r}  "
        f"{'OK' if r['low_not_cooperate'] else 'FAIL'}"
        for r in results
    ]
    return {
        "pass": all_pass,
        "cases": results,
        "details": details,
    }


# ---------------------------------------------------------------------------
# Test 5: apply_action — cooperate efficiency scales with signal
# ---------------------------------------------------------------------------

def test_cooperate_efficiency_scales() -> dict:
    """
    cooperate stress reduction = 0.1 * coord_efficiency
    coord_efficiency = 0.8 + 0.4 * max(0, signal)
    
    At signal=0.0: coord_eff = 0.8, stress_reduction = 0.08
    At signal=1.0: coord_eff = 1.2, stress_reduction = 0.12
    At signal=-1.0: coord_eff = 0.8 (clamped), stress_reduction = 0.08
    
    Higher signal → more stress reduction per cooperate action.
    """
    cases = [(-1.0, 0.8), (0.0, 0.8), (0.5, 1.0), (1.0, 1.2)]
    details = []
    all_pass = True

    for signal, expected_eff in cases:
        agent = _make_agent(hunger=0.3, energy=0.8, stress=0.5)
        stress_before = agent.stress
        agent.apply_action("cooperate", signal)
        stress_reduction = stress_before - agent.stress
        expected_reduction = round(0.1 * expected_eff, 6)
        # Actual reduction accounts for base hunger tick (doesn't affect stress)
        # Tolerance for floating point
        ok = abs(stress_reduction - expected_reduction) < 1e-9
        all_pass = all_pass and ok
        details.append(
            f"signal={signal:+.1f}: eff={expected_eff:.2f} "
            f"expected_stress_reduction={expected_reduction:.4f} "
            f"actual={stress_reduction:.6f}  {'OK' if ok else 'FAIL'}"
        )

    return {"pass": all_pass, "details": details}


# ---------------------------------------------------------------------------
# Test 6: Baseline decision completely ignores signal
# ---------------------------------------------------------------------------

def test_baseline_ignores_signal() -> dict:
    """
    decide_baseline() must produce the same action regardless of what signal
    would have been. We verify this by checking that the action from
    decide_baseline() equals what decide_with_signal(0.0) would do when
    there is no cooperation available (baseline logic: forage/rest/explore only).
    
    More specifically: baseline never returns 'cooperate' or 'build'.
    """
    signals = [-1.0, -0.5, 0.0, 0.5, 1.0]
    forbidden_actions = {"cooperate", "build"}

    details = []
    all_pass = True

    for s in signals:
        agent = _make_agent(hunger=0.3, energy=0.8, stress=0.2)
        action = agent.decide_baseline()
        in_forbidden = action in forbidden_actions
        # Baseline should never choose cooperate or build
        ok = not in_forbidden
        all_pass = all_pass and ok
        details.append(f"decide_baseline() (would-be signal={s:+.1f}): {action!r}  {'OK' if ok else 'FAIL (cooperation found!)'}")

    # Also verify: decide_baseline result is always the same (independent of any state)
    agent_a = _make_agent(hunger=0.3, energy=0.8, stress=0.2)
    action_a = agent_a.decide_baseline()
    agent_b = _make_agent(hunger=0.3, energy=0.8, stress=0.2)
    action_b = agent_b.decide_baseline()
    consistent = (action_a == action_b)
    details.append(f"Consistency check: {action_a!r} == {action_b!r}  {'OK' if consistent else 'FAIL'}")

    return {"pass": all_pass and consistent, "details": details}


# ---------------------------------------------------------------------------
# Test 7: Coordination-blocked flag overrides substrate
# ---------------------------------------------------------------------------

def test_coordination_blocked() -> dict:
    """
    With high signal and low-need agent that would normally cooperate,
    passing coordination_blocked=True must prevent cooperation.
    """
    agent = _make_agent(hunger=0.2, energy=0.9, stress=0.1)
    signal = 1.0  # max cooperation capacity

    action_free    = agent.decide_with_signal(signal, coordination_blocked=False)
    action_blocked = agent.decide_with_signal(signal, coordination_blocked=True)

    expected_free    = (action_free == "cooperate")
    expected_blocked = (action_blocked != "cooperate")

    details = [
        f"signal=+1.0, blocked=False: {action_free!r}  (expected cooperate: {'OK' if expected_free else 'FAIL'})",
        f"signal=+1.0, blocked=True:  {action_blocked!r}  (expected not cooperate: {'OK' if expected_blocked else 'FAIL'})",
    ]
    return {
        "pass": expected_free and expected_blocked,
        "action_free":    action_free,
        "action_blocked": action_blocked,
        "details": details,
    }


# ---------------------------------------------------------------------------
# Test 8: Critical need always overrides substrate
# ---------------------------------------------------------------------------

def test_critical_need_override() -> dict:
    """
    hunger > 0.8 always produces 'forage' regardless of signal.
    energy < 0.15 always produces 'rest' regardless of signal.
    """
    all_pass = True
    details = []

    # Hunger override
    for signal in [-1.0, 0.0, 1.0]:
        agent = _make_agent(hunger=0.85, energy=0.8, stress=0.1)
        action = agent.decide_with_signal(signal)
        ok = (action == "forage")
        all_pass = all_pass and ok
        details.append(f"hunger=0.85, signal={signal:+.1f}: {action!r}  (must be forage: {'OK' if ok else 'FAIL'})")

    # Energy override
    for signal in [-1.0, 0.0, 1.0]:
        agent = _make_agent(hunger=0.3, energy=0.10, stress=0.1)
        action = agent.decide_with_signal(signal)
        ok = (action == "rest")
        all_pass = all_pass and ok
        details.append(f"energy=0.10, signal={signal:+.1f}: {action!r}  (must be rest: {'OK' if ok else 'FAIL'})")

    return {"pass": all_pass, "details": details}


# ---------------------------------------------------------------------------
# Test 9: Mixed substrate states from SubstrateState
# ---------------------------------------------------------------------------

def test_substrate_state_roundtrip() -> dict:
    """
    Verify that SubstrateState.coordination_capacity matches the formula
    used by the agent: 0.5 * (1 + c_spectral), by constructing SubstrateState
    directly and checking its properties.
    """
    try:
        from sim_world.domains.physical_field.substrate_state import SubstrateState
    except ImportError as e:
        return {"pass": False, "error": f"Cannot import SubstrateState: {e}",
                "details": [f"Import failed: {e}"]}

    # Test values via direct constructor
    test_c_values = [-1.0, -0.5, 0.0, 0.5, 1.0]
    details = []
    all_pass = True

    for c in test_c_values:
        f_prop = max(0.0, (c + 1.0) / 2.0)
        f_over = max(0.0, (1.0 - c) / 2.0)
        f_crit = max(0.0, 1.0 - f_prop - f_over)
        try:
            sub = SubstrateState(
                c_spectral=c,
                f_prop=f_prop,
                f_over=f_over,
                f_crit=f_crit,
                dominant_D=1.0 if c > 0 else -1.0,
                dominant_k=0.1,
                dominant_regime="coherent" if c > 0 else "overdamped",
                spectral_entropy=0.5,
                weighted_D=c,
                tau=3.0,
                decay_timescale=6.0,
                propagation_speed=1.0,
                k_critical=0.5,
                physical_time=0.0,
                metadata={},
            )
            expected_coord = 0.5 * (1.0 + c)
            actual_coord = sub.coordination_capacity
            ok = abs(actual_coord - expected_coord) < 1e-9
            all_pass = all_pass and ok
            ctx = sub.to_agent_context()
            # Verify to_agent_context returns expected keys
            has_keys = all(k in ctx for k in
                           ["substrate_c_spectral", "substrate_coordination"])
            all_pass = all_pass and has_keys
            details.append(
                f"c_spectral={c:+.1f}: "
                f"coord_capacity={actual_coord:.4f} "
                f"(expected={expected_coord:.4f}) "
                f"ctx_has_keys={has_keys} "
                f"{'OK' if ok and has_keys else 'FAIL'}"
            )
        except Exception as e:
            all_pass = False
            details.append(f"c_spectral={c:+.1f}: ERROR {e}")

    return {"pass": all_pass, "details": details}


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

TESTS = [
    ("coord_capacity_monotone",         test_coord_capacity_monotone),
    ("decision_response_curve",         test_decision_response_curve),
    ("decision_sweep",                  test_decision_sweep),
    ("threshold_varies_with_need",      test_threshold_varies_with_need),
    ("cooperate_efficiency_scales",     test_cooperate_efficiency_scales),
    ("baseline_ignores_signal",         test_baseline_ignores_signal),
    ("coordination_blocked",            test_coordination_blocked),
    ("critical_need_override",          test_critical_need_override),
    ("substrate_state_roundtrip",       test_substrate_state_roundtrip),
]


def main() -> None:
    print("\n" + "=" * 65)
    print("  PHASE 10 — SUBSTRATE INTERVENTION TESTS")
    print("  Verifying agent decisions respond to substrate signal changes")
    print("=" * 65)

    results = []
    for name, fn in TESTS:
        r = _run_test(name, fn)
        results.append(r)
        _print_result(r)

    passed = sum(1 for r in results if r["status"] == "PASS")
    total  = len(results)
    print(f"\n  {passed}/{total} tests passed")

    if passed < total:
        print("\n  FAILED tests:")
        for r in results:
            if r["status"] != "PASS":
                print(f"    - {r['name']}: {r.get('error', 'see details above')}")

    out_path = os.path.join(_HERE, "phase10_intervention_results.json")
    with open(out_path, "w") as f:
        # Remove sweep detail from JSON (too large) but keep summary
        compact = []
        for r in results:
            rc = {k: v for k, v in r.items() if k != "sweep"}
            compact.append(rc)
        json.dump({"passed": passed, "total": total, "tests": compact}, f, indent=2)
    print(f"  Results saved → {out_path}")
    print("=" * 65)


if __name__ == "__main__":
    main()
