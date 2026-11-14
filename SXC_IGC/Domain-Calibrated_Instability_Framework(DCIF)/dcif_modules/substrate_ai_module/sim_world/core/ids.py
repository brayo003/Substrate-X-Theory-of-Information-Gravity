from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar
from uuid import UUID

def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    val = hash(s) % (2**32)
    return abs(val)


_ROOT_NAMESPACE = deterministic_hash("sim_world")


def _canonical_text(value: Any) -> str:
    if isinstance(value, UUID):
        return str(value)
    if hasattr(value, "value") and isinstance(getattr(value, "value"), UUID):
        return str(getattr(value, "value"))
    if isinstance(value, (str, int, float, bool)) or value is None:
        return repr(value)
    if isinstance(value, bytes):
        return value.hex()
    if isinstance(value, dict):
        items = ",".join(f"{_canonical_text(k)}:{_canonical_text(v)}" for k, v in sorted(value.items(), key=lambda item: str(item[0])))
        return "{" + items + "}"
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(_canonical_text(item) for item in value) + "]"
    if isinstance(value, set):
        return "{" + ",".join(sorted(_canonical_text(item) for item in value)) + "}"
    return repr(value)


def _deterministic_uuid(kind: str, *parts: Any) -> UUID:
    namespace = deterministic_hash(str(_ROOT_NAMESPACE) + kind)
    seed = "|".join(_canonical_text(part) for part in parts)
    return UUID(int=deterministic_hash(str(namespace) + seed) % (2**128))


@dataclass(frozen=True, slots=True)
class _Identifier:
    value: UUID
    namespace: ClassVar[int] = _ROOT_NAMESPACE

    @classmethod
    def deterministic(cls, *parts: Any) -> "_Identifier":
        return cls(_deterministic_uuid(cls.__name__, *parts))

    @classmethod
    def from_uuid(cls, value: UUID | str) -> "_Identifier":
        return cls(UUID(str(value)))

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"


@dataclass(frozen=True, slots=True)
class WorldId(_Identifier):
    namespace: ClassVar[int] = deterministic_hash(str(_ROOT_NAMESPACE) + "WorldId")

    @classmethod
    def new(cls, world_name: str, seed: Any = None) -> "WorldId":
        return cls.deterministic(world_name, seed)


@dataclass(frozen=True, slots=True)
class EntityId(_Identifier):
    namespace: ClassVar[int] = deterministic_hash(str(_ROOT_NAMESPACE) + "EntityId")

    @classmethod
    def new(cls, world_id: WorldId, entity_key: Any) -> "EntityId":
        return cls.deterministic(world_id.value, entity_key)


@dataclass(frozen=True, slots=True)
class AssetId(_Identifier):
    namespace: ClassVar[int] = deterministic_hash(str(_ROOT_NAMESPACE) + "AssetId")

    @classmethod
    def new(cls, world_id: WorldId, asset_key: Any) -> "AssetId":
        return cls.deterministic(world_id.value, asset_key)


@dataclass(frozen=True, slots=True)
class RevisionId(_Identifier):
    namespace: ClassVar[int] = deterministic_hash(str(_ROOT_NAMESPACE) + "RevisionId")

    @classmethod
    def new(cls, world_id: WorldId, tick_id: "TickId" | None, sequence: int, payload: Any = None) -> "RevisionId":
        return cls.deterministic(world_id.value, tick_id.value if tick_id else None, sequence, payload)


@dataclass(frozen=True, slots=True)
class TickId(_Identifier):
    namespace: ClassVar[int] = deterministic_hash(str(_ROOT_NAMESPACE) + "TickId")

    @classmethod
    def new(cls, world_id: WorldId, tick_number: int) -> "TickId":
        return cls.deterministic(world_id.value, tick_number)


@dataclass(frozen=True, slots=True)
class SnapshotId(_Identifier):
    namespace: ClassVar[int] = deterministic_hash(str(_ROOT_NAMESPACE) + "SnapshotId")

    @classmethod
    def new(cls, revision_id: RevisionId, tick_id: TickId) -> "SnapshotId":
        return cls.deterministic(revision_id.value, tick_id.value)


@dataclass(frozen=True, slots=True)
class EventId(_Identifier):
    namespace: ClassVar[int] = deterministic_hash(str(_ROOT_NAMESPACE) + "EventId")

    @classmethod
    def new(cls, revision_id: RevisionId, index: int, payload: Any = None) -> "EventId":
        return cls.deterministic(revision_id.value, index, payload)
