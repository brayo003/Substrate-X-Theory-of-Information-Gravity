from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Mapping, Sequence


from ..core.contracts import freeze_value
from ..core.ids import AssetId, EntityId, RevisionId, TickId, WorldId
from .memory import BaseMemoryStore

def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    val = hash(s) % (2**32)
    return abs(val)



@dataclass(frozen=True, slots=True)
class AssetIdentityRecord:
    asset_id: AssetId
    world_id: WorldId
    version: int
    canonical_name: str
    descriptors: Mapping[str, Any] = field(default_factory=dict)
    visual_embedding_placeholder: str = ""
    serial_number: str = ""
    manufacturer: str = ""
    creation_metadata: Mapping[str, Any] = field(default_factory=dict)
    provenance: Mapping[str, Any] = field(default_factory=dict)
    entity_id: EntityId | None = None
    created_tick: int | None = None
    created_revision: RevisionId | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        object.__setattr__(self, "canonical_name", str(self.canonical_name))
        object.__setattr__(self, "serial_number", str(self.serial_number))
        object.__setattr__(self, "manufacturer", str(self.manufacturer))
        object.__setattr__(self, "descriptors", freeze_value(dict(self.descriptors)))
        object.__setattr__(self, "creation_metadata", freeze_value(dict(self.creation_metadata)))
        object.__setattr__(self, "provenance", freeze_value(dict(self.provenance)))


def _asset_key(asset_id: AssetId, version: int) -> str:
    return f"{asset_id.value}:{version}"


@dataclass
class AssetMemory(BaseMemoryStore):
    versions: dict[AssetId, list[AssetIdentityRecord]] = field(default_factory=dict)
    by_entity: dict[EntityId, AssetId] = field(default_factory=dict)

    def remember(
        self,
        *,
        canonical_name: str,
        descriptors: Mapping[str, Any] | None = None,
        visual_embedding_placeholder: str = "",
        serial_number: str = "",
        manufacturer: str = "",
        creation_metadata: Mapping[str, Any] | None = None,
        provenance: Mapping[str, Any] | None = None,
        world_id: WorldId | None = None,
        entity_id: EntityId | None = None,
        created_tick: int | None = None,
        created_revision: RevisionId | None = None,
        asset_id: AssetId | None = None,
    ) -> AssetIdentityRecord:
        resolved_world = world_id or self.world_id
        resolved_asset_id = asset_id or AssetId.new(resolved_world, serial_number or canonical_name or entity_id or len(self.versions))
        history = self.versions.setdefault(resolved_asset_id, [])
        record = AssetIdentityRecord(
            asset_id=resolved_asset_id,
            world_id=resolved_world,
            version=len(history) + 1,
            canonical_name=canonical_name,
            descriptors={} if descriptors is None else dict(descriptors),
            visual_embedding_placeholder=visual_embedding_placeholder,
            serial_number=serial_number,
            manufacturer=manufacturer,
            creation_metadata={} if creation_metadata is None else dict(creation_metadata),
            provenance={} if provenance is None else dict(provenance),
            entity_id=entity_id,
            created_tick=created_tick,
            created_revision=created_revision,
        )
        history.append(record)
        if entity_id is not None:
            self.by_entity[entity_id] = resolved_asset_id
        self._emit(
            memory_kind="asset",
            action="remember",
            reference_id=str(resolved_asset_id.value),
            revision_id=created_revision,
            tick_id=None if created_tick is None else TickId.new(resolved_world, created_tick),
            entity_id=entity_id,
            asset_id=resolved_asset_id,
            payload={
                "canonical_name": canonical_name,
                "descriptors": record.descriptors,
                "serial_number": serial_number,
                "manufacturer": manufacturer,
                "version": record.version,
            },
            metadata={"asset_key": _asset_key(resolved_asset_id, record.version)},
        )
        return record

    def register(self, record: AssetIdentityRecord) -> AssetIdentityRecord:
        history = self.versions.setdefault(record.asset_id, [])
        history.append(record)
        if record.entity_id is not None:
            self.by_entity[record.entity_id] = record.asset_id
        self._emit(
            memory_kind="asset",
            action="register",
            reference_id=str(record.asset_id.value),
            revision_id=record.created_revision,
            tick_id=None if record.created_tick is None else TickId.new(record.world_id, record.created_tick),
            entity_id=record.entity_id,
            asset_id=record.asset_id,
            payload={"version": record.version, "canonical_name": record.canonical_name},
            metadata={"asset_key": _asset_key(record.asset_id, record.version)},
        )
        return record

    def lookup(self, asset_id: AssetId, version: int | None = None) -> AssetIdentityRecord | None:
        history = self.versions.get(asset_id)
        if not history:
            return None
        if version is None:
            return history[-1]
        for record in history:
            if record.version == version:
                return record
        return None

    def latest(self, asset_id: AssetId | None = None) -> AssetIdentityRecord | None:
        if asset_id is None:
            if not self.versions:
                return None
            latest_key = max(self.versions, key=lambda key: self.versions[key][-1].timestamp)
            return self.versions[latest_key][-1]
        return self.lookup(asset_id)

    def list(self) -> tuple[AssetIdentityRecord, ...]:
        records: list[AssetIdentityRecord] = []
        for history in self.versions.values():
            records.extend(history)
        return tuple(sorted(records, key=lambda record: (record.asset_id.value.hex, record.version)))

    def find_by_entity(self, entity_id: EntityId) -> AssetIdentityRecord | None:
        asset_id = self.by_entity.get(entity_id)
        if asset_id is None:
            return None
        return self.lookup(asset_id)

    def search(self, *, text: str | None = None, predicates: Mapping[str, Any] | None = None) -> tuple[AssetIdentityRecord, ...]:
        predicates = {} if predicates is None else dict(predicates)
        results: list[AssetIdentityRecord] = []
        for record in self.list():
            if text is not None:
                haystack = " ".join(
                    [
                        record.canonical_name,
                        record.serial_number,
                        record.manufacturer,
                        repr(dict(record.descriptors)),
                        repr(dict(record.creation_metadata)),
                        repr(dict(record.provenance)),
                    ]
                ).lower()
                if text.lower() not in haystack:
                    continue
            if predicates:
                matched = True
                for key, expected in predicates.items():
                    if key == "entity_id":
                        matched = record.entity_id == expected
                    elif getattr(record, key, None) != expected:
                        matched = False
                    if not matched:
                        break
                if not matched:
                    continue
            results.append(record)
        return tuple(results)

    def references(self) -> Mapping[str, Any]:
        return freeze_value(
            {
                "asset_ids": [str(asset_id.value) for asset_id in self.versions],
                "count": sum(len(history) for history in self.versions.values()),
            }
        )
