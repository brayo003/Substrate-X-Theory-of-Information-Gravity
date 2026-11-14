from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Mapping, Sequence


from ..core.contracts import freeze_value
from ..core.ids import RevisionId, TickId, WorldId
from .memory import BaseMemoryStore

def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    val = hash(s) % (2**32)
    return abs(val)



@dataclass(frozen=True, slots=True)
class KnowledgeRecord:
    knowledge_id: str
    kind: str
    statement: str
    categories: tuple[str, ...]
    tags: tuple[str, ...]
    source: str
    version: int
    confidence: float
    timestamp: datetime
    revision_id: RevisionId | None = None
    tick_id: TickId | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "knowledge_id", str(self.knowledge_id))
        object.__setattr__(self, "kind", str(self.kind))
        object.__setattr__(self, "statement", str(self.statement))
        object.__setattr__(self, "categories", tuple(str(category) for category in self.categories))
        object.__setattr__(self, "tags", tuple(str(tag) for tag in self.tags))
        object.__setattr__(self, "source", str(self.source))
        object.__setattr__(self, "confidence", float(self.confidence))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))


def _knowledge_id(world_id: WorldId, kind: str, statement: str, version: int) -> str:
    seed = f"{world_id.value}|{kind}|{statement}|{version}"
    return f"id_{deterministic_hash(seed)}"


@dataclass
class KnowledgeMemory(BaseMemoryStore):
    records: list[KnowledgeRecord] = field(default_factory=list)
    facts_index: dict[str, list[KnowledgeRecord]] = field(default_factory=dict)
    rules_index: dict[str, list[KnowledgeRecord]] = field(default_factory=dict)
    categories_index: dict[str, list[KnowledgeRecord]] = field(default_factory=dict)

    def add_fact(
        self,
        statement: str,
        *,
        categories: Sequence[str] | None = None,
        tags: Sequence[str] | None = None,
        source: str = "",
        confidence: float = 1.0,
        revision_id: RevisionId | None = None,
        tick_id: TickId | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> KnowledgeRecord:
        return self._add(
            "fact",
            statement,
            categories=categories,
            tags=tags,
            source=source,
            confidence=confidence,
            revision_id=revision_id,
            tick_id=tick_id,
            metadata=metadata,
        )

    def add_rule(
        self,
        statement: str,
        *,
        categories: Sequence[str] | None = None,
        tags: Sequence[str] | None = None,
        source: str = "",
        confidence: float = 1.0,
        revision_id: RevisionId | None = None,
        tick_id: TickId | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> KnowledgeRecord:
        return self._add(
            "rule",
            statement,
            categories=categories,
            tags=tags,
            source=source,
            confidence=confidence,
            revision_id=revision_id,
            tick_id=tick_id,
            metadata=metadata,
        )

    def add_category(
        self,
        statement: str,
        *,
        categories: Sequence[str] | None = None,
        tags: Sequence[str] | None = None,
        source: str = "",
        confidence: float = 1.0,
        revision_id: RevisionId | None = None,
        tick_id: TickId | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> KnowledgeRecord:
        return self._add(
            "category",
            statement,
            categories=categories,
            tags=tags,
            source=source,
            confidence=confidence,
            revision_id=revision_id,
            tick_id=tick_id,
            metadata=metadata,
        )

    def query(
        self,
        text: str | None = None,
        *,
        kind: str | None = None,
        categories: Sequence[str] | None = None,
        tags: Sequence[str] | None = None,
        predicate: Callable[[KnowledgeRecord], bool] | None = None,
    ) -> tuple[KnowledgeRecord, ...]:
        category_set = set(categories or ())
        tag_set = set(tags or ())
        results: list[KnowledgeRecord] = []
        for record in self.records:
            if kind is not None and record.kind != kind:
                continue
            if category_set and not category_set.issubset(set(record.categories)):
                continue
            if tag_set and not tag_set.issubset(set(record.tags)):
                continue
            if text is not None and text.lower() not in self._haystack(record).lower():
                continue
            if predicate is not None and not predicate(record):
                continue
            results.append(record)
        return tuple(results)

    def facts(self) -> tuple[KnowledgeRecord, ...]:
        return tuple(record for record in self.records if record.kind == "fact")

    def rules(self) -> tuple[KnowledgeRecord, ...]:
        return tuple(record for record in self.records if record.kind == "rule")

    def categories(self) -> tuple[KnowledgeRecord, ...]:
        return tuple(record for record in self.records if record.kind == "category")

    def lookup(self, knowledge_id: str) -> KnowledgeRecord | None:
        for record in self.records:
            if record.knowledge_id == knowledge_id:
                return record
        return None

    def _add(
        self,
        kind: str,
        statement: str,
        *,
        categories: Sequence[str] | None,
        tags: Sequence[str] | None,
        source: str,
        confidence: float,
        revision_id: RevisionId | None,
        tick_id: TickId | None,
        metadata: Mapping[str, Any] | None,
    ) -> KnowledgeRecord:
        version = sum(1 for record in self.records if record.kind == kind and record.statement == statement) + 1
        record = KnowledgeRecord(
            knowledge_id=_knowledge_id(self.world_id, kind, statement, version),
            kind=kind,
            statement=statement,
            categories=tuple(categories or ()),
            tags=tuple(tags or ()),
            source=source,
            version=version,
            confidence=confidence,
            timestamp=datetime.now(timezone.utc),
            revision_id=revision_id,
            tick_id=tick_id,
            metadata={} if metadata is None else dict(metadata),
        )
        self.records.append(record)
        if kind == "fact":
            self.facts_index.setdefault(statement, []).append(record)
        elif kind == "rule":
            self.rules_index.setdefault(statement, []).append(record)
        elif kind == "category":
            self.categories_index.setdefault(statement, []).append(record)
        self._emit(
            memory_kind="knowledge",
            action="add",
            reference_id=record.knowledge_id,
            revision_id=revision_id,
            tick_id=tick_id,
            payload={"kind": kind, "statement": statement, "version": version},
            metadata=record.metadata,
        )
        return record

    def _haystack(self, record: KnowledgeRecord) -> str:
        return " ".join([record.kind, record.statement, record.source, " ".join(record.categories), " ".join(record.tags), repr(dict(record.metadata))])
