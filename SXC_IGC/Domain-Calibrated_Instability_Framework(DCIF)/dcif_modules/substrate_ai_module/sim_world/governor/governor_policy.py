from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping


from ..core.contracts import GovernanceDecision, freeze_value
from .governor_context import GovernorContext
from ..core.ids import RevisionId, TickId, WorldId

def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    val = hash(s) % (2**32)
    return abs(val)



def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _get(value: Any, name: str, default: Any = None) -> Any:
    if value is None:
        return default
    if isinstance(value, Mapping):
        return value.get(name, default)
    return getattr(value, name, default)


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}


def _string(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def _revision_id(value: Any) -> RevisionId | None:
    if value is None:
        return None
    if isinstance(value, RevisionId):
        return value
    if hasattr(value, "revision_id"):
        candidate = getattr(value, "revision_id")
        if isinstance(candidate, RevisionId):
            return candidate
        return RevisionId.from_uuid(candidate)
    if hasattr(value, "value"):
        return RevisionId.from_uuid(getattr(value, "value"))
    return RevisionId.from_uuid(value)


def _tick_id(value: Any) -> TickId | None:
    if value is None:
        return None
    if isinstance(value, TickId):
        return value
    if hasattr(value, "tick_id"):
        candidate = getattr(value, "tick_id")
        if isinstance(candidate, TickId):
            return candidate
        return TickId.from_uuid(candidate)
    if hasattr(value, "value"):
        return TickId.from_uuid(getattr(value, "value"))
    return TickId.from_uuid(value)


def _timestamp_for(context: GovernorContext, policy_name: str, disposition: str) -> datetime:
    revision = _revision_id(context.revision)
    seed = "|".join(
        [
            str(context.world_id.value),
            "" if context.tick_id is None else str(context.tick_id.value),
            "" if revision is None else str(revision.value),
            policy_name,
            disposition,
            context.policy_version,
        ]
    )
    seed_uuid = deterministic_hash("sim_world.governor|" + seed)
    seconds = seed_uuid % 86400
    micros = (seed_uuid // 86400) % 1_000_000
    return datetime(2000, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=seconds, microseconds=micros)


def _correlation_id(context: GovernorContext, policy_name: str, disposition: str) -> str:
    if context.correlation_id:
        return context.correlation_id
    revision = _revision_id(context.revision)
    seed = "|".join(
        [
            str(context.world_id.value),
            "" if context.tick_id is None else str(context.tick_id.value),
            "" if revision is None else str(revision.value),
            policy_name,
            disposition,
            context.policy_version,
        ]
    )
    return f"id_{deterministic_hash('sim_world.governor.correlation|' + seed)}"


def _expiry_for(context: GovernorContext, policy_name: str, disposition: str) -> datetime:
    base = _timestamp_for(context, policy_name, disposition)
    tick_offset = 1 if context.tick_id is None else 1 + int(deterministic_hash(str(context.tick_id.value)) % 5)
    return base + timedelta(seconds=tick_offset)


def _input_ids(context: GovernorContext) -> Mapping[str, Any]:
    simulation = context.simulation_diagnostics
    planner = context.planner_diagnostics
    transport = context.transport_observation
    verification = context.verification_report
    renderer = context.renderer_report
    kernel_status = dict(context.kernel_status)
    return freeze_value(
        {
            "world_id": str(context.world_id.value),
            "tick_id": None if context.tick_id is None else str(context.tick_id.value),
            "revision": None if context.revision is None else str(getattr(context.revision, "value", context.revision)),
            "simulation": {
                "tick_id": _string(_get(simulation, "tick_id")),
                "committed_revision": _string(_get(simulation, "committed_revision")),
            },
            "planner": {
                "tick_id": _string(_get(planner, "tick_id")),
                "committed_revision": _string(_get(planner, "committed_revision")),
            },
            "transport": {
                "observation_id": _string(_get(transport, "observation_id")),
                "current_revision": _string(_get(transport, "current_revision")),
            },
            "verification": {
                "snapshot_id": _string(_get(verification, "snapshot_id")),
                "output_id": _string(_get(verification, "output_id")),
            },
            "renderer": {
                "request_id": _string(_get(renderer, "request_id")),
                "result_id": _string(_get(renderer, "result_id")),
            },
            "kernel_status": kernel_status,
        }
    )


def _decision(
    context: GovernorContext,
    *,
    policy_name: str,
    disposition: str,
    rationale: str,
    alternatives: tuple[str, ...],
    limits: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
    confidence: float = 1.0,
) -> GovernanceDecision:
    return GovernanceDecision(
        world_id=context.world_id,
        tick_id=context.tick_id,
        state_revision=_revision_id(context.revision),
        correlation_id=_correlation_id(context, policy_name, disposition),
        disposition=disposition,
        policy_version=context.policy_version,
        rationale=rationale,
        limits={} if limits is None else dict(limits),
        metadata={
            "policy_name": policy_name,
            "input_ids": dict(_input_ids(context)),
            **({} if metadata is None else dict(metadata)),
        },
        policy_name=policy_name,
        input_ids=_input_ids(context),
        alternatives=alternatives,
        expiry=_expiry_for(context, policy_name, disposition),
        confidence=confidence,
    )


def _has_hard_integrity_violation(context: GovernorContext) -> tuple[bool, str]:
    kernel_status = dict(context.kernel_status)
    for flag in ("wrong_snapshot", "missing_provenance", "unauthorized_target", "integrity_violation", "wrong_target"):
        if kernel_status.get(flag):
            return True, flag
    verification = context.verification_report
    if verification is not None:
        report_metadata = dict(_get(verification, "metadata", {}))
        for flag in ("wrong_snapshot", "missing_provenance", "unauthorized_target", "integrity_violation"):
            if report_metadata.get(flag):
                return True, flag
        evidence = dict(_get(verification, "evidence", {}))
        for flag in ("wrong_snapshot", "missing_provenance", "unauthorized_target", "integrity_violation"):
            if evidence.get(flag):
                return True, flag
    return False, ""


def _q_value(context: GovernorContext) -> float | None:
    transport = context.transport_observation
    if transport is None:
        return None
    value = _get(transport, "q_value")
    if value is None:
        return None
    return float(value)


def _q_regime(context: GovernorContext) -> str:
    transport = context.transport_observation
    if transport is None:
        return ""
    return _string(_get(transport, "regime"))


def _q_confidence(context: GovernorContext) -> float | None:
    transport = context.transport_observation
    if transport is None:
        return None
    value = _get(transport, "confidence")
    if value is None:
        return None
    return float(value)


def _verification_status(context: GovernorContext) -> tuple[bool | None, str, float, float]:
    report = context.verification_report
    if report is None:
        return None, "", 1.0, 0.0
    passed = _get(report, "passed")
    confidence = _get(report, "confidence", 1.0)
    severity = _string(_get(report, "severity"))
    coverage = _get(report, "coverage", 1.0)
    return (None if passed is None else bool(passed), severity, float(confidence), float(coverage))


def _simulation_conflicts(context: GovernorContext) -> tuple[Any, ...]:
    simulation = context.simulation_diagnostics
    if simulation is None:
        return ()
    conflicts = _get(simulation, "conflicts", ())
    if conflicts is None:
        conflicts = ()
    return tuple(conflicts)


def _planner_conflicts(context: GovernorContext) -> tuple[Any, ...]:
    planner = context.planner_diagnostics
    if planner is None:
        return ()
    metadata = dict(_get(planner, "metadata", {}))
    conflicts = tuple(_get(planner, "conflicts", ()))
    if conflicts:
        return conflicts
    if metadata.get("inconsistent") or metadata.get("feasibility_failure"):
        return ({"reason": "planner inconsistency", "metadata": metadata},)
    rejected_count = _get(planner, "plans_rejected", 0)
    generated = _get(planner, "plans_generated", 0)
    if int(rejected_count or 0) > 0 and int(generated or 0) == 0:
        return ({"reason": "planner rejected all plans", "metadata": metadata},)
    return ()


def _kernel_failure(context: GovernorContext) -> tuple[bool, str]:
    kernel_status = dict(context.kernel_status)
    if kernel_status.get("failure"):
        return True, _string(kernel_status.get("failure"), "kernel failure")
    if kernel_status.get("status") in {"failed", "error", "panic"}:
        return True, _string(kernel_status.get("status"))
    if kernel_status.get("exception"):
        return True, _string(kernel_status.get("exception"), "kernel failure")
    return False, ""


@dataclass(frozen=True, slots=True)
class GovernorPolicy:
    name: str
    version: str = "1.0"
    disposition: str = ""
    alternatives: tuple[str, ...] = field(default_factory=tuple)

    def __call__(self, context: GovernorContext) -> GovernanceDecision | None:
        if not self.matches(context):
            return None
        return self.build_decision(context)

    def matches(self, context: GovernorContext) -> bool:
        raise NotImplementedError

    def build_decision(self, context: GovernorContext) -> GovernanceDecision:
        raise NotImplementedError

    def decision(
        self,
        context: GovernorContext,
        *,
        rationale: str,
        limits: Mapping[str, Any] | None = None,
        metadata: Mapping[str, Any] | None = None,
        confidence: float = 1.0,
    ) -> GovernanceDecision:
        return _decision(
            context,
            policy_name=self.name,
            disposition=self.disposition,
            rationale=rationale,
            alternatives=self.alternatives,
            limits=limits,
            metadata={"policy_version": self.version, **({} if metadata is None else dict(metadata))},
            confidence=confidence,
        )


@dataclass(frozen=True, slots=True)
class RejectPolicy(GovernorPolicy):
    name: str = "RejectPolicy"
    disposition: str = "REJECT"
    alternatives: tuple[str, ...] = ("REJECT", "ROLLBACK", "RETRY")

    def matches(self, context: GovernorContext) -> bool:
        hard_violation, _ = _has_hard_integrity_violation(context)
        if hard_violation:
            return True
        if _simulation_conflicts(context):
            return True
        if _planner_conflicts(context):
            return True
        checkpoint = dict(context.kernel_status).get("checkpoint_revision") or dict(context.kernel_status).get("rollback_target_revision")
        passed, severity, _, _ = _verification_status(context)
        if passed is False and severity in {"high", "critical"} and checkpoint is None:
            return True
        return False

    def build_decision(self, context: GovernorContext) -> GovernanceDecision:
        hard_violation, reason = _has_hard_integrity_violation(context)
        if hard_violation:
            rationale = f"hard integrity violation: {reason}"
        elif _simulation_conflicts(context):
            rationale = "simulation conflict detected"
        elif _planner_conflicts(context):
            rationale = "planner inconsistency detected"
        else:
            _, severity, confidence, coverage = _verification_status(context)
            rationale = f"verification failure severity={severity or 'unknown'}"
            return self.decision(
                context,
                rationale=rationale,
                limits={"confidence": confidence, "coverage": coverage},
                metadata={"trigger": "verification_failure"},
                confidence=max(0.0, 1.0 - confidence),
            )
        return self.decision(
            context,
            rationale=rationale,
            limits={"hard_integrity": hard_violation},
            metadata={"trigger": "reject"},
            confidence=0.0,
        )


@dataclass(frozen=True, slots=True)
class RollbackPolicy(GovernorPolicy):
    name: str = "RollbackPolicy"
    disposition: str = "ROLLBACK"
    alternatives: tuple[str, ...] = ("ROLLBACK", "RETRY", "REJECT")

    def matches(self, context: GovernorContext) -> bool:
        kernel_failure, _ = _kernel_failure(context)
        if kernel_failure:
            return True
        checkpoint = dict(context.kernel_status).get("checkpoint_revision") or dict(context.kernel_status).get("rollback_target_revision")
        passed, severity, _, _ = _verification_status(context)
        return passed is False and severity == "critical" and checkpoint is not None

    def build_decision(self, context: GovernorContext) -> GovernanceDecision:
        kernel_failure, reason = _kernel_failure(context)
        kernel_status = dict(context.kernel_status)
        checkpoint = kernel_status.get("checkpoint_revision") or kernel_status.get("rollback_target_revision")
        if kernel_failure:
            rationale = f"kernel failure: {reason}"
        else:
            rationale = "critical verification failure with checkpoint"
        return self.decision(
            context,
            rationale=rationale,
            limits={
                "checkpoint_revision": None if checkpoint is None else str(getattr(checkpoint, "value", checkpoint)),
                "kernel_failure": kernel_failure,
            },
            metadata={"trigger": "rollback"},
            confidence=0.95 if checkpoint is not None else 0.8,
        )


@dataclass(frozen=True, slots=True)
class RetryPolicy(GovernorPolicy):
    name: str = "RetryPolicy"
    disposition: str = "RETRY"
    alternatives: tuple[str, ...] = ("RETRY", "REJECT")

    def matches(self, context: GovernorContext) -> bool:
        passed, severity, _, _ = _verification_status(context)
        if passed is False and severity not in {"high", "critical"}:
            return True
        return False

    def build_decision(self, context: GovernorContext) -> GovernanceDecision:
        _, severity, confidence, coverage = _verification_status(context)
        return self.decision(
            context,
            rationale=f"verification failure; retry requested (severity={severity or 'unknown'})",
            limits={"confidence": confidence, "coverage": coverage},
            metadata={"trigger": "retry"},
            confidence=_clamp(max(0.25, 1.0 - confidence)),
        )


@dataclass(frozen=True, slots=True)
class BranchPolicy(GovernorPolicy):
    name: str = "BranchPolicy"
    disposition: str = "BRANCH"
    alternatives: tuple[str, ...] = ("BRANCH", "SLOW_DOWN", "ACCEPT")

    def matches(self, context: GovernorContext) -> bool:
        q_value = _q_value(context)
        regime = _q_regime(context)
        kernel_status = dict(context.kernel_status)
        if kernel_status.get("branch_requested"):
            return True
        if q_value is None:
            return False
        return q_value <= 0.15 or regime == "critical" or (q_value <= 0.2 and bool(kernel_status.get("allow_branch", True)))

    def build_decision(self, context: GovernorContext) -> GovernanceDecision:
        q_value = _q_value(context)
        regime = _q_regime(context)
        return self.decision(
            context,
            rationale=f"branch due to q instability (regime={regime or 'unknown'}, q={q_value if q_value is not None else 'n/a'})",
            limits={"q_value": q_value, "regime": regime},
            metadata={"trigger": "branch"},
            confidence=_clamp(1.0 - (q_value or 0.0)),
        )


@dataclass(frozen=True, slots=True)
class SlowDownPolicy(GovernorPolicy):
    name: str = "SlowDownPolicy"
    disposition: str = "SLOW_DOWN"
    alternatives: tuple[str, ...] = ("SLOW_DOWN", "BRANCH", "ACCEPT")

    def matches(self, context: GovernorContext) -> bool:
        q_value = _q_value(context)
        regime = _q_regime(context)
        if q_value is None:
            return False
        return q_value <= 0.35 or regime in {"warning", "boundary"}

    def build_decision(self, context: GovernorContext) -> GovernanceDecision:
        q_value = _q_value(context)
        regime = _q_regime(context)
        q_confidence = _q_confidence(context)
        return self.decision(
            context,
            rationale=f"q instability suggests slower cadence (regime={regime or 'unknown'}, q={q_value if q_value is not None else 'n/a'})",
            limits={"q_value": q_value, "regime": regime, "confidence": q_confidence},
            metadata={"trigger": "slow_down"},
            confidence=_clamp(1.0 - (q_value or 0.0) * 0.5),
        )


@dataclass(frozen=True, slots=True)
class AcceptPolicy(GovernorPolicy):
    name: str = "AcceptPolicy"
    disposition: str = "ACCEPT"
    alternatives: tuple[str, ...] = ("ACCEPT",)

    def matches(self, context: GovernorContext) -> bool:
        return True

    def build_decision(self, context: GovernorContext) -> GovernanceDecision:
        q_value = _q_value(context)
        passed, severity, confidence, coverage = _verification_status(context)
        return self.decision(
            context,
            rationale="no policy matched; accepting control state",
            limits={
                "q_value": q_value,
                "verification_passed": passed,
                "verification_severity": severity,
                "verification_confidence": confidence,
                "verification_coverage": coverage,
            },
            metadata={"trigger": "accept"},
            confidence=1.0,
        )
