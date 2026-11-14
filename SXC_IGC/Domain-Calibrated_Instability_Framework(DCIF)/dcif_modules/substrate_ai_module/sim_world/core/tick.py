from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping


from .contracts import TickContext, freeze_value
from .ids import RevisionId, TickId, WorldId

def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    val = hash(s) % (2**32)
    return abs(val)



@dataclass(slots=True)
class TickClock:
    world_id: WorldId
    _tick_number: int = 0

    def _timestamp_for(self, tick_id: TickId, state_revision: RevisionId | None, parent_revision: RevisionId | None, correlation_id: str | None) -> datetime:
        seed = "|".join(
            [
                str(self.world_id.value),
                str(tick_id.value),
                "" if state_revision is None else str(state_revision.value),
                "" if parent_revision is None else str(parent_revision.value),
                correlation_id or "",
            ]
        )
        seed_hash = deterministic_hash("sim_world.tick|{seed}")
        seconds = seed_hash % 86400
        micros = (seed_hash // 86400) % 1_000_000
        return datetime(2000, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=seconds, microseconds=micros)

    def next_tick_id(self) -> TickId:
        self._tick_number += 1
        return TickId.new(self.world_id, self._tick_number)

    def peek_next_tick_id(self) -> TickId:
        return TickId.new(self.world_id, self._tick_number + 1)

    def create_context(
        self,
        *,
        state_revision: RevisionId | None,
        parent_revision: RevisionId | None,
        correlation_id: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> TickContext:
        tick_id = self.next_tick_id()
        return TickContext(
            world_id=self.world_id,
            tick_id=tick_id,
            state_revision=state_revision,
            parent_revision=parent_revision,
            timestamp=self._timestamp_for(tick_id, state_revision, parent_revision, correlation_id),
            correlation_id=correlation_id or str(tick_id.value),
            metadata={} if metadata is None else freeze_value(dict(metadata)),
        )

    @property
    def tick_number(self) -> int:
        return self._tick_number
