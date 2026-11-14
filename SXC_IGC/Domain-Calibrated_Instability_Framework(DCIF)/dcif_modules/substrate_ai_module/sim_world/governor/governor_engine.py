from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping


from ..core.contracts import GovernanceDecision, freeze_value
from .governor_context import GovernorContext
from .governor_history import GovernorHistory, GovernorHistoryRecord
from .governor_policy import AcceptPolicy, BranchPolicy, GovernorPolicy, RejectPolicy, RetryPolicy, RollbackPolicy, SlowDownPolicy, _revision_id
from ..core.ids import EventId, RevisionId, TickId, WorldId

def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    val = hash(s) % (2**32)
    return abs(val)



def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _event_timestamp(context: GovernorContext, event_type: str, policy_name: str, disposition: str, index: int) -> datetime:
    seed = "|".join(
        [
            str(context.world_id.value),
            "" if context.tick_id is None else str(context.tick_id.value),
            "" if context.revision is None else str(getattr(context.revision, "value", context.revision)),
            event_type,
            policy_name,
            disposition,
            str(index),
        ]
    )
    seed_uuid = deterministic_hash("sim_world.governor.event|" + seed)
    seconds = seed_uuid % 86400
    micros = (seed_uuid // 86400) % 1_000_000
    return datetime(2000, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=seconds, microseconds=micros)


def _event_id(context: GovernorContext, event_type: str, policy_name: str, disposition: str, index: int) -> EventId:
    revision = RevisionId.new(
        context.world_id,
        context.tick_id,
        index,
        {
            "event_type": event_type,
            "policy_name": policy_name,
            "disposition": disposition,
            "policy_version": context.policy_version,
        },
    )
    return EventId.new(revision, index, {"event_type": event_type, "policy_name": policy_name, "disposition": disposition})


def _summary(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, Mapping):
        return freeze_value({str(key): _summary(inner) for key, inner in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_summary(item) for item in value)
    if hasattr(value, "value"):
        return str(getattr(value, "value"))
    return value


@dataclass(frozen=True, slots=True)
class GovernorEvent:
    event_id: EventId
    world_id: WorldId
    event_type: str
    timestamp: datetime
    tick_id: TickId | None
    revision: RevisionId | None
    policy_name: str
    disposition: str
    decision: GovernanceDecision
    payload: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_type", str(self.event_type))
        object.__setattr__(self, "policy_name", str(self.policy_name))
        object.__setattr__(self, "disposition", str(self.disposition))
        object.__setattr__(self, "payload", freeze_value(dict(self.payload)))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))


@dataclass
class GovernorEngine:
    policy_version: str = "1.0"
    policies: tuple[GovernorPolicy, ...] = field(default_factory=tuple)
    history_store: GovernorHistory = field(default_factory=GovernorHistory)
    events: list[GovernorEvent] = field(default_factory=list)
    last_decision: GovernanceDecision | None = field(default=None, init=False, repr=False)
    last_policy_name: str = field(default="", init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.policies:
            self.policies = (
                AcceptPolicy(version=self.policy_version),
                RetryPolicy(version=self.policy_version),
                RetryPolicy(version=self.policy_version),
                BranchPolicy(version=self.policy_version),
                SlowDownPolicy(version=self.policy_version),
                AcceptPolicy(version=self.policy_version),
            )

    def evaluate(self, context: GovernorContext) -> GovernanceDecision:
        if context.policy_version and context.policy_version != self.policy_version:
            context = GovernorContext(
                world_id=context.world_id,
                tick_id=context.tick_id,
                revision=context.revision,
                policy_version=context.policy_version,
                simulation_diagnostics=context.simulation_diagnostics,
                planner_diagnostics=context.planner_diagnostics,
                transport_observation=context.transport_observation,
                verification_report=context.verification_report,
                renderer_report=context.renderer_report,
                kernel_status=context.kernel_status,
                correlation_id=context.correlation_id,
                metadata=context.metadata,
            )

        chosen_policy: GovernorPolicy | None = None
        decision: GovernanceDecision | None = None
        for policy in self.policies:
            candidate = policy(context)
            if candidate is not None:
                chosen_policy = policy
                decision = candidate
                self._emit("PolicyTriggered", context, policy_name=policy.name, decision=candidate, payload={"policy_version": policy.version})
                break

        if decision is None:
            accept_policy = AcceptPolicy(version=self.policy_version)
            chosen_policy = accept_policy
            decision = accept_policy.build_decision(context)
            self._emit("PolicyTriggered", context, policy_name=accept_policy.name, decision=decision, payload={"policy_version": accept_policy.version, "fallback": True})

        self._emit("DecisionMade", context, policy_name=chosen_policy.name, decision=decision, payload={"limits": dict(decision.limits)})
        if decision.disposition == "ACCEPT":
            self._emit("DecisionAccepted", context, policy_name=chosen_policy.name, decision=decision, payload={"accepted": True})
        else:
            self._emit("DecisionRejected", context, policy_name=chosen_policy.name, decision=decision, payload={"accepted": False})

        self.history_store.append(
            decision=decision,
            policy_name=chosen_policy.name,
            world_id=context.world_id,
            tick_id=context.tick_id,
            revision=context.revision,
            inputs=decision.input_ids,
            metadata={
                "decision_event_types": tuple(event.event_type for event in self.events[-3:]),
                "policy_version": chosen_policy.version,
            },
        )
        self.last_decision = decision
        self.last_policy_name = chosen_policy.name
        return decision

    def history(self) -> tuple[GovernorHistoryRecord, ...]:
        return self.history_store.history()

    def capability_report(self) -> Mapping[str, Any]:
        return freeze_value(
            {
                "policy_version": self.policy_version,
                "policies": tuple(policy.name for policy in self.policies),
                "history_size": len(self.history_store.records),
            }
        )

    def _emit(
        self,
        event_type: str,
        context: GovernorContext,
        *,
        policy_name: str,
        decision: GovernanceDecision,
        payload: Mapping[str, Any] | None = None,
    ) -> GovernorEvent:
        event = GovernorEvent(
            event_id=_event_id(context, event_type, policy_name, decision.disposition, len(self.events) + 1),
            world_id=context.world_id,
            event_type=event_type,
            timestamp=_event_timestamp(context, event_type, policy_name, decision.disposition, len(self.events) + 1),
            tick_id=context.tick_id,
            revision=_revision_id(context.revision),
            policy_name=policy_name,
            disposition=decision.disposition,
            decision=decision,
            payload={} if payload is None else dict(payload),
            metadata={
                "policy_version": decision.policy_version,
                "correlation_id": decision.correlation_id,
            },
        )
        self.events.append(event)
        return event
