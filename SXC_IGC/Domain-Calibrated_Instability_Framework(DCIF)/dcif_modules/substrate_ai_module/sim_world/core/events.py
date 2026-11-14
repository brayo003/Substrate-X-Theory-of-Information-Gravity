from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping

from .contracts import freeze_value
from .ids import EntityId, EventId, RevisionId, TickId, WorldId


def _freeze_path(path: tuple[str, ...] | None) -> tuple[str, ...]:
    if path is None:
        return ()
    return tuple(str(part) for part in path)


def _hash_payload(payload: Mapping[str, Any] | None) -> str:
    frozen = freeze_value({} if payload is None else dict(payload))
    return repr(frozen)


def _set_path(state: dict[str, Any], path: tuple[str, ...], value: Any) -> None:
    if not path:
        raise ValueError("state path must not be empty")
    cursor = state
    for key in path[:-1]:
        next_value = cursor.get(key)
        if not isinstance(next_value, dict):
            next_value = {}
            cursor[key] = next_value
        cursor = next_value
    cursor[path[-1]] = freeze_value(value)


def _remove_path(state: dict[str, Any], path: tuple[str, ...]) -> None:
    if not path:
        raise ValueError("state path must not be empty")
    cursor = state
    for key in path[:-1]:
        next_value = cursor.get(key)
        if not isinstance(next_value, dict):
            return
        cursor = next_value
    cursor.pop(path[-1], None)


def _merge_dict(target: dict[str, Any], patch: Mapping[str, Any]) -> dict[str, Any]:
    for key, value in patch.items():
        if isinstance(value, Mapping):
            existing = target.get(key)
            if isinstance(existing, Mapping):
                target[key] = _merge_dict(dict(existing), value)
            else:
                target[key] = _merge_dict({}, value)
        else:
            target[key] = freeze_value(value)
    return target


@dataclass(frozen=True, slots=True)
class StateEvent:
    event_id: EventId
    revision_id: RevisionId | None
    tick_id: TickId | None
    entity_id: EntityId | None
    timestamp: datetime
    kind: str
    subject: str
    patch: Mapping[str, Any] = field(default_factory=dict)
    remove_paths: tuple[tuple[str, ...], ...] = field(default_factory=tuple)
    state_hash_before: str = ""
    state_hash_after: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "patch", freeze_value(dict(self.patch)))
        object.__setattr__(self, "remove_paths", tuple(_freeze_path(path) for path in self.remove_paths))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))

    @classmethod
    def from_transition(
        cls,
        *,
        world_id: WorldId,
        revision_id: RevisionId | None,
        tick_id: TickId | None,
        subject: str,
        patch: Mapping[str, Any],
        remove_paths: tuple[tuple[str, ...], ...] = (),
        state_before: Mapping[str, Any] | None = None,
        index: int = 0,
        metadata: Mapping[str, Any] | None = None,
        entity_id: EntityId | None = None,
    ) -> "StateEvent":
        payload = {
            "subject": subject,
            "patch": dict(patch),
            "remove_paths": [list(path) for path in remove_paths],
            "index": index,
        }
        seed_revision = revision_id or RevisionId.new(world_id, tick_id, index, payload)
        event_id = EventId.new(seed_revision, index, payload)
        before_hash = _hash_payload(state_before)
        after_state = cls._apply_preview(dict(state_before or {}), patch, remove_paths)
        after_hash = _hash_payload(after_state)
        return cls(
            event_id=event_id,
            revision_id=revision_id,
            tick_id=tick_id,
            entity_id=entity_id,
            timestamp=datetime.now(timezone.utc),
            kind="transition",
            subject=subject,
            patch=dict(patch),
            remove_paths=remove_paths,
            state_hash_before=before_hash,
            state_hash_after=after_hash,
            metadata={} if metadata is None else dict(metadata),
        )

    @staticmethod
    def _apply_preview(
        state: Mapping[str, Any] | None,
        patch: Mapping[str, Any],
        remove_paths: tuple[tuple[str, ...], ...],
    ) -> dict[str, Any]:
        result = dict(state or {})
        _merge_dict(result, patch)
        for path in remove_paths:
            _remove_path(result, path)
        return result

    def apply_to(self, state: Mapping[str, Any]) -> dict[str, Any]:
        next_state = dict(state)
        _merge_dict(next_state, self.patch)
        for path in self.remove_paths:
            _remove_path(next_state, path)
        return next_state
