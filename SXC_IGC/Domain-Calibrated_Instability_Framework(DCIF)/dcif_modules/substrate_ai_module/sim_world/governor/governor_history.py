from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping


from ..core.contracts import GovernanceDecision, freeze_value
from ..core.ids import RevisionId, TickId, WorldId

def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    val = hash(s) % (2**32)
    return abs(val)



def _timestamp_for(world_id: WorldId, tick_id: TickId | None, revision: RevisionId | None, policy_name: str, disposition: str, index: int) -> datetime:
    seed = "|".join(
        [
            str(world_id.value),
            "" if tick_id is None else str(tick_id.value),
            "" if revision is None else str(revision.value),
            policy_name,
            disposition,
            str(index),
        ]
    )
    seed_uuid = deterministic_hash("sim_world.governor_history|" + seed)
    seconds = seed_uuid % 86400
    micros = (seed_uuid // 86400) % 1_000_000
    return datetime(2000, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=seconds, microseconds=micros)


@dataclass(frozen=True, slots=True)
class GovernorHistoryRecord:
    decision: GovernanceDecision
    policy_name: str
    inputs: Mapping[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime(2000, 1, 1, tzinfo=timezone.utc))
    revision: RevisionId | None = None
    tick_id: TickId | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "policy_name", str(self.policy_name))
        object.__setattr__(self, "inputs", freeze_value(dict(self.inputs)))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))


@dataclass
class GovernorHistory:
    records: list[GovernorHistoryRecord] = field(default_factory=list)

    def append(
        self,
        *,
        decision: GovernanceDecision,
        policy_name: str,
        world_id: WorldId,
        tick_id: TickId | None,
        revision: RevisionId | None,
        inputs: Mapping[str, Any] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> GovernorHistoryRecord:
        record = GovernorHistoryRecord(
            decision=decision,
            policy_name=policy_name,
            inputs={} if inputs is None else dict(inputs),
            timestamp=_timestamp_for(world_id, tick_id, revision, policy_name, decision.disposition, len(self.records) + 1),
            revision=revision,
            tick_id=tick_id,
            metadata={} if metadata is None else dict(metadata),
        )
        self.records.append(record)
        return record

    def latest(self) -> GovernorHistoryRecord | None:
        return self.records[-1] if self.records else None

    def history(self) -> tuple[GovernorHistoryRecord, ...]:
        return tuple(self.records)

    def list_history(self) -> tuple[GovernorHistoryRecord, ...]:
        return self.history()
