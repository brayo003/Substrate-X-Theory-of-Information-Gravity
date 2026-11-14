from __future__ import annotations

import pytest

from sim_world import (
    GovernanceDecision,
    GovernorContext,
    GovernorEngine,
    HealthComponent,
    KernelConfig,
    QObservation,
    RejectPolicy,
    RenderProfile,
    RetryPolicy,
    RollbackPolicy,
    SlowDownPolicy,
    TransformComponent,
    TransitionProposal,
    VerificationReport,
    WorldKernel,
)
from sim_world.simulation_context import PhaseDiagnostics, SimulationDiagnostics
from sim_world.planner_context import PlanningDiagnostics, PlanningPhaseReport
from sim_world.ids import TickId


def _kernel() -> WorldKernel:
    kernel = WorldKernel(
        KernelConfig(
            world_name="governor_world",
            seed="governor-seed",
            initial_state={"mode": "governor"},
        )
    )
    created_revision = kernel.current_revision.revision_id if kernel.current_revision is not None else None
    alice = kernel.entity_registry.create_entity(
        entity_type="person",
        display_name="Alice",
        created_tick=kernel.current_tick_number,
        created_revision=created_revision,
        components=[TransformComponent(room="Kitchen"), HealthComponent(current=100, maximum=100)],
    )
    kernel.entity_registry.create_entity(
        entity_type="person",
        display_name="Bob",
        created_tick=kernel.current_tick_number,
        created_revision=created_revision,
        components=[TransformComponent(room="Kitchen"), HealthComponent(current=100, maximum=100)],
    )
    kernel.entity_registry.connect_relationship(
        alice.entity_id,
        next(entity.entity_id for entity in kernel.entity_registry.list_entities() if entity.display_name == "Bob"),
        "friend",
        created_tick=kernel.current_tick_number,
        created_revision=created_revision,
    )
    return kernel


def _context(kernel: WorldKernel, **overrides) -> GovernorContext:
    return kernel.governor_context(**overrides)


def test_accept_path_and_history_recording() -> None:
    kernel = _kernel()
    engine = GovernorEngine()
    context = _context(kernel)

    decision = engine.evaluate(context)

    assert decision.disposition == "ACCEPT"
    assert decision.policy_name == "AcceptPolicy"
    assert engine.last_decision == decision
    assert engine.history()[-1].decision == decision
    assert engine.events[-1].event_type == "DecisionAccepted"


def test_reject_path() -> None:
    kernel = _kernel()
    engine = GovernorEngine()
    simulation_diagnostics = SimulationDiagnostics(
        world_id=kernel.world_id,
        tick_id=TickId.new(kernel.world_id, 1),
        tick_number=1,
        committed_revision=None,
        phase_reports=(PhaseDiagnostics("conflict", 1, rejected_count=1),),
        executed_actions=(),
        rejected_actions=(),
        conflicts=({"code": "conflict", "message": "sim conflict"},),
        metadata={"reason": "sim conflict"},
    )
    context = _context(kernel, simulation_diagnostics=simulation_diagnostics)

    decision = engine.evaluate(context)

    assert decision.disposition == "REJECT"
    assert decision.policy_name == "RejectPolicy"
    assert engine.events[-1].event_type == "DecisionRejected"


def test_retry_path() -> None:
    kernel = _kernel()
    engine = GovernorEngine()
    report = VerificationReport(
        world_id=kernel.world_id,
        snapshot_id=kernel.create_snapshot().snapshot_id,
        output_id="output-1",
        tick_id=TickId.new(kernel.world_id, 1),
        state_revision=None,
        passed=False,
        confidence=0.35,
        discrepancies=(),
        evidence={"reason": "mismatch"},
        metadata={"severity": "unknown"},
        severity="unknown",
        coverage=0.6,
    )
    context = _context(kernel, verification_report=report)

    decision = engine.evaluate(context)

    assert decision.disposition == "RETRY"
    assert decision.policy_name == "RetryPolicy"


def test_rollback_recommendation_and_kernel_integration() -> None:
    kernel = _kernel()
    first_revision = kernel.advance_tick(
        [
            TransitionProposal(
                world_id=kernel.world_id,
                tick_id=None,
                state_revision=None,
                correlation_id="tick-1",
                subject="counter",
                patch={"counter": 1},
                description="set counter",
                metadata={},
            )
        ]
    )
    second_revision = kernel.advance_tick(
        [
            TransitionProposal(
                world_id=kernel.world_id,
                tick_id=None,
                state_revision=first_revision.revision_id,
                correlation_id="tick-2",
                subject="counter",
                patch={"counter": 2},
                description="set counter again",
                metadata={},
            )
        ]
    )

    decision = kernel.govern(
        kernel_status={
            "failure": "kernel crash",
            "checkpoint_revision": first_revision.revision_id,
            "status": "failed",
        }
    )

    checkpoint_state = kernel.storage.load_revision(first_revision.revision_id).state
    assert decision.disposition == "ROLLBACK"
    assert kernel.current_state == checkpoint_state
    assert kernel.last_governance_decision == decision
    assert kernel.governance_history[-1].decision == decision
    assert second_revision.revision_id != first_revision.revision_id


def test_branch_and_slow_down_recommendations() -> None:
    kernel = _kernel()
    engine = GovernorEngine()
    branch_observation = QObservation(
        world_id=kernel.world_id,
        tick_id=TickId.new(kernel.world_id, 1),
        previous_revision=None,
        current_revision=None,
        observation_time=kernel.create_snapshot().timestamp,
        metric_values={"state_distance": 0.9},
        calibration_profile="default",
        calibration_version="1.0",
        representation_type="snapshot_transition",
        confidence=0.2,
        q_value=0.05,
        regime="critical",
        uncertainty=0.9,
        thresholds={"critical": 0.1},
        observed_pair={},
        calibration_metadata=None,
        metadata={},
    )
    slow_observation = QObservation(
        world_id=kernel.world_id,
        tick_id=TickId.new(kernel.world_id, 2),
        previous_revision=None,
        current_revision=None,
        observation_time=kernel.create_snapshot().timestamp,
        metric_values={"state_distance": 0.4},
        calibration_profile="default",
        calibration_version="1.0",
        representation_type="snapshot_transition",
        confidence=0.7,
        q_value=0.3,
        regime="warning",
        uncertainty=0.3,
        thresholds={"warning": 0.35},
        observed_pair={},
        calibration_metadata=None,
        metadata={},
    )

    branch_context = _context(kernel, transport_observation=branch_observation)
    slow_context = _context(kernel, transport_observation=slow_observation)

    branch_decision = engine.evaluate(branch_context)
    slow_decision = engine.evaluate(slow_context)

    assert branch_decision.disposition == "BRANCH"
    assert slow_decision.disposition == "SLOW_DOWN"


def test_policy_precedence_prefers_rollback_over_reject_when_checkpoint_exists() -> None:
    kernel = _kernel()
    engine = GovernorEngine()
    report = VerificationReport(
        world_id=kernel.world_id,
        snapshot_id=kernel.create_snapshot().snapshot_id,
        output_id="output-2",
        tick_id=TickId.new(kernel.world_id, 1),
        state_revision=None,
        passed=False,
        confidence=0.1,
        discrepancies=(),
        evidence={"reason": "critical mismatch"},
        metadata={"severity": "critical"},
        severity="critical",
        coverage=0.2,
    )
    context = _context(
        kernel,
        verification_report=report,
        kernel_status={"checkpoint_revision": kernel.current_revision.revision_id, "failure": "kernel failure"},
    )

    decision = engine.evaluate(context)

    assert decision.disposition == "ROLLBACK"
    assert decision.policy_name == "RollbackPolicy"


def test_deterministic_replay() -> None:
    kernel = _kernel()
    report = VerificationReport(
        world_id=kernel.world_id,
        snapshot_id=kernel.create_snapshot().snapshot_id,
        output_id="output-3",
        tick_id=TickId.new(kernel.world_id, 1),
        state_revision=None,
        passed=False,
        confidence=0.5,
        discrepancies=(),
        evidence={"reason": "mismatch"},
        metadata={"severity": "unknown"},
        severity="unknown",
        coverage=0.7,
    )
    context = _context(kernel, verification_report=report)

    engine_a = GovernorEngine()
    engine_b = GovernorEngine()

    decision_a = engine_a.evaluate(context)
    decision_b = engine_b.evaluate(context)

    assert decision_a == decision_b
    assert engine_a.history()[0] == engine_b.history()[0]

