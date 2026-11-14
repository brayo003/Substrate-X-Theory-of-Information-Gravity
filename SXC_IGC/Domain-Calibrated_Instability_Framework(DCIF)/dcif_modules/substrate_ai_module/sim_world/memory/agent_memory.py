from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Iterable, Mapping, Sequence


from ..core.contracts import freeze_value
from ..core.ids import EntityId, RevisionId, TickId, WorldId
from .memory import BaseMemoryStore, MemoryEvent

def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    val = hash(s) % (2**32)
    return abs(val)



@dataclass(frozen=True, slots=True)
class AgentMemoryRecord:
    record_id: str
    owner_entity_id: EntityId
    kind: str
    content: Any
    timestamp: datetime
    tick_id: TickId | None = None
    revision_id: RevisionId | None = None
    tags: tuple[str, ...] = field(default_factory=tuple)
    confidence: float = 1.0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "record_id", str(self.record_id))
        object.__setattr__(self, "kind", str(self.kind))
        object.__setattr__(self, "tags", tuple(str(tag) for tag in self.tags))
        object.__setattr__(self, "confidence", float(self.confidence))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))


def _record_id(world_id: WorldId, owner_entity_id: EntityId, kind: str, content: Any, timestamp: datetime, index: int) -> str:
    seed = f"{world_id.value}|{owner_entity_id.value}|{kind}|{repr(content)}|{timestamp.isoformat()}|{index}"
    return f"id_{deterministic_hash(seed)}"


@dataclass
class AgentMemory(BaseMemoryStore):
    owner_entity_id: EntityId | None = None
    memory_id: str = ""
    records: dict[str, AgentMemoryRecord] = field(default_factory=dict)
    _history: list[AgentMemoryRecord] = field(default_factory=list, repr=False)
    _forgotten: set[str] = field(default_factory=set, repr=False)

    def __post_init__(self) -> None:
        if self.owner_entity_id is None:
            raise ValueError("agent memory requires an owner entity id")
        if not self.memory_id:
            seed = f"{self.world_id.value}|{self.owner_entity_id.value}|agent-memory"
            self.memory_id = str(deterministic_hash(seed))

    def remember(
        self,
        kind: str,
        content: Any,
        *,
        tick_id: TickId | None = None,
        revision_id: RevisionId | None = None,
        tags: Sequence[str] | None = None,
        confidence: float = 1.0,
        metadata: Mapping[str, Any] | None = None,
    ) -> AgentMemoryRecord:
        timestamp = datetime.now(timezone.utc)
        record = AgentMemoryRecord(
            record_id=_record_id(self.world_id, self.owner_entity_id, kind, content, timestamp, len(self._history) + 1),
            owner_entity_id=self.owner_entity_id,
            kind=kind,
            content=content,
            timestamp=timestamp,
            tick_id=tick_id,
            revision_id=revision_id,
            tags=tuple(tags or ()),
            confidence=confidence,
            metadata={} if metadata is None else dict(metadata),
        )
        self.records[record.record_id] = record
        self._history.append(record)
        self._forgotten.discard(record.record_id)
        self._emit(
            memory_kind="agent",
            action="remember",
            reference_id=record.record_id,
            revision_id=revision_id,
            tick_id=tick_id,
            entity_id=self.owner_entity_id,
            payload={
                "kind": kind,
                "content": record.content,
                "tags": record.tags,
                "confidence": record.confidence,
            },
            metadata=record.metadata,
        )
        return record

    def forget(
        self,
        record_id: str | None = None,
        *,
        kind: str | None = None,
        predicate: Callable[[AgentMemoryRecord], bool] | None = None,
    ) -> tuple[AgentMemoryRecord, ...]:
        selected: list[AgentMemoryRecord] = []
        for record in self._history:
            if record.record_id in self._forgotten:
                continue
            if record_id is not None and record.record_id != record_id:
                continue
            if kind is not None and record.kind != kind:
                continue
            if predicate is not None and not predicate(record):
                continue
            selected.append(record)
        for record in selected:
            self._forgotten.add(record.record_id)
            self._emit(
                memory_kind="agent",
                action="forget",
                reference_id=record.record_id,
                revision_id=record.revision_id,
                tick_id=record.tick_id,
                entity_id=self.owner_entity_id,
                payload={"kind": record.kind},
                metadata=record.metadata,
            )
        return tuple(selected)

    def recall(
        self,
        kind: str | None = None,
        *,
        tags: Sequence[str] | None = None,
        query: str | None = None,
        include_forgotten: bool = False,
    ) -> tuple[AgentMemoryRecord, ...]:
        tag_set = set(tags or ())
        results: list[AgentMemoryRecord] = []
        for record in self._history:
            if not include_forgotten and record.record_id in self._forgotten:
                continue
            if kind is not None and record.kind != kind:
                continue
            if tag_set and not tag_set.issubset(set(record.tags)):
                continue
            if query is not None and query.lower() not in self._flatten(record).lower():
                continue
            results.append(record)
        return tuple(results)

    def search(self, query: str, *, include_forgotten: bool = False) -> tuple[AgentMemoryRecord, ...]:
        return self.recall(query=query, include_forgotten=include_forgotten)

    def latest(self, kind: str | None = None) -> AgentMemoryRecord | None:
        for record in reversed(self._history):
            if record.record_id in self._forgotten:
                continue
            if kind is not None and record.kind != kind:
                continue
            return record
        return None

    def history(self) -> tuple[AgentMemoryRecord, ...]:
        return tuple(self._history)

    def _flatten(self, record: AgentMemoryRecord) -> str:
        return " ".join(
            [
                record.kind,
                repr(record.content),
                " ".join(record.tags),
                repr(dict(record.metadata)),
            ]
        )
