from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping


from .contracts import RenderSnapshot, freeze_value
from .ids import SnapshotId, TickId
from .revision import Revision

def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    val = hash(s) % (2**32)
    return abs(val)



@dataclass(frozen=True, slots=True)
class SnapshotService:
    def _timestamp_for(self, *, world_id, tick_id, state_revision, parent_revision, state: Mapping[str, Any], events=()) -> datetime:
        seed = "|".join(
            [
                str(world_id.value),
                str(tick_id.value),
                str(state_revision.value),
                "" if parent_revision is None else str(parent_revision.value),
                repr(freeze_value(dict(state))),
                repr(tuple(events)),
            ]
        )
        seed_hash = deterministic_hash("sim_world.snapshot|{seed}")
        seconds = seed_hash % 86400
        micros = (seed_hash // 86400) % 1_000_000
        return datetime(2000, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=seconds, microseconds=micros)

    def create(self, revision: Revision) -> RenderSnapshot:
        tick_id = revision.tick_id or TickId.new(revision.world_id, 0)
        return RenderSnapshot(
            world_id=revision.world_id,
            snapshot_id=SnapshotId.new(revision.revision_id, tick_id),
            tick_id=revision.tick_id,
            state_revision=revision.revision_id,
            parent_revision=revision.parent_revision,
            timestamp=revision.timestamp,
            state=freeze_value(dict(revision.state)),
            events=revision.events,
            metadata=freeze_value({"state_hash": revision.state_hash}),
        )

    def create_from_state(
        self,
        *,
        world_id,
        tick_id,
        state_revision,
        parent_revision,
        state: Mapping[str, Any],
        events=(),
        metadata: Mapping[str, Any] | None = None,
    ) -> RenderSnapshot:
        timestamp = self._timestamp_for(
            world_id=world_id,
            tick_id=tick_id,
            state_revision=state_revision,
            parent_revision=parent_revision,
            state=state,
            events=events,
        )
        snapshot_id = SnapshotId.new(state_revision, tick_id)
        return RenderSnapshot(
            world_id=world_id,
            snapshot_id=snapshot_id,
            tick_id=tick_id,
            state_revision=state_revision,
            parent_revision=parent_revision,
            timestamp=timestamp,
            state=freeze_value(dict(state)),
            events=tuple(events),
            metadata={} if metadata is None else metadata,
        )
