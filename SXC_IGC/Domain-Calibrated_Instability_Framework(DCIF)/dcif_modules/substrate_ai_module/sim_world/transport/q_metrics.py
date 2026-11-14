from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any, Iterable, Mapping

from ..core.contracts import RenderSnapshot
from .transport_context import TransportContext


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _snapshot_mapping(value: Any) -> Mapping[str, Any]:
    if value is None:
        return {}
    if isinstance(value, Mapping):
        return value
    if isinstance(value, RenderSnapshot):
        return value.state
    state = getattr(value, "state", None)
    if isinstance(state, Mapping):
        return state
    output = getattr(value, "output", None)
    if isinstance(output, Mapping):
        return output
    evidence = getattr(value, "evidence", None)
    if isinstance(evidence, Mapping):
        return evidence
    if isinstance(value, (list, tuple, set)):
        return {"items": tuple(value)}
    return {"value": value}


def _canonical_atom(value: Any) -> str:
    if isinstance(value, Mapping):
        return repr({str(key): _canonical_atom(inner) for key, inner in sorted(value.items(), key=lambda item: str(item[0]))})
    if isinstance(value, (list, tuple, set)):
        return repr([_canonical_atom(item) for item in value])
    return repr(value)


def _flatten(value: Any, prefix: tuple[str, ...] = ()) -> dict[tuple[str, ...], str]:
    flattened: dict[tuple[str, ...], str] = {}
    if isinstance(value, Mapping):
        for key in sorted(value.keys(), key=str):
            flattened.update(_flatten(value[key], prefix + (str(key),)))
        return flattened
    if isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            flattened.update(_flatten(item, prefix + (str(index),)))
        return flattened
    if isinstance(value, set):
        for index, item in enumerate(sorted(value, key=_canonical_atom)):
            flattened.update(_flatten(item, prefix + (str(index),)))
        return flattened
    flattened[prefix] = _canonical_atom(value)
    return flattened


def _entity_map(snapshot: Any) -> dict[str, Mapping[str, Any]]:
    state = dict(_snapshot_mapping(snapshot))
    entities = state.get("entities", {})
    if isinstance(entities, Mapping):
        return {str(entity_id): dict(entity_state) for entity_id, entity_state in entities.items()}
    return {}


def _entity_ids(snapshot: Any) -> set[str]:
    return set(_entity_map(snapshot))


def _component_signatures(snapshot: Any) -> set[str]:
    signatures: set[str] = set()
    for entity_id, entity_state in _entity_map(snapshot).items():
        components = dict(entity_state.get("components", {}))
        for component_name in sorted(components.keys(), key=str):
            signatures.add(f"{entity_id}|{component_name}|{_canonical_atom(components[component_name])}")
    return signatures


def _relationship_signatures(snapshot: Any) -> set[str]:
    signatures: set[str] = set()
    for entity_id, entity_state in _entity_map(snapshot).items():
        for relationship in entity_state.get("relationships", ()):
            if isinstance(relationship, Mapping):
                signatures.add(
                    "|".join(
                        [
                            entity_id,
                            str(relationship.get("relationship_id")),
                            str(relationship.get("relationship_type")),
                            str(relationship.get("source_id")),
                            str(relationship.get("target_id")),
                            _canonical_atom(relationship.get("metadata", {})),
                        ]
                    )
                )
            else:
                signatures.add(f"{entity_id}|{_canonical_atom(relationship)}")
    return signatures


def _topology_signatures(snapshot: Any) -> set[str]:
    signatures: set[str] = set()
    for entity_id, entity_state in _entity_map(snapshot).items():
        components = dict(entity_state.get("components", {}))
        transform = components.get("TransformComponent")
        if isinstance(transform, Mapping):
            room = transform.get("room")
            if room is not None:
                signatures.add(f"entity:{entity_id}|room:{room}")
        metadata = dict(entity_state.get("metadata", {}))
        for key in ("held_by", "inside", "contains", "parent", "child", "owner", "works_for", "married", "following"):
            if metadata.get(key) is not None:
                signatures.add(f"entity:{entity_id}|{key}:{metadata.get(key)}")
        for relationship in entity_state.get("relationships", ()):
            if isinstance(relationship, Mapping):
                signatures.add(
                    f"rel:{relationship.get('relationship_type')}:{relationship.get('source_id')}->{relationship.get('target_id')}"
                )
    return signatures


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left and not right:
        return 1.0
    union = left | right
    if not union:
        return 1.0
    return len(left & right) / len(union)


@dataclass
class QMetrics:
    def state_distance(self, previous: Any, current: Any) -> float:
        left = _flatten(_snapshot_mapping(previous))
        right = _flatten(_snapshot_mapping(current))
        if not left and not right:
            return 0.0
        keys = set(left) | set(right)
        if not keys:
            return 0.0
        changed = sum(1 for key in keys if left.get(key) != right.get(key))
        return _clamp(changed / len(keys))

    def representation_distance(self, previous: Any, current: Any) -> float:
        # Bounded similarity: difflib.SequenceMatcher.ratio() on the full
        # serialized world state is O(n^2) and pathologically slow once the
        # state grows (tens of villagers). Compare flattened key-value atomic
        # sets instead -- still captures structural divergence, ~O(n).
        left = _flatten(_snapshot_mapping(previous))
        right = _flatten(_snapshot_mapping(current))
        if not left and not right:
            return 0.0
        keys = set(left) | set(right)
        if not keys:
            return 0.0
        changed = sum(1 for key in keys if left.get(key) != right.get(key))
        return _clamp(changed / len(keys))

    def identity_preservation(self, previous: Any, current: Any) -> float:
        return _jaccard(_entity_ids(previous), _entity_ids(current))

    def topology_preservation(self, previous: Any, current: Any) -> float:
        return _jaccard(_topology_signatures(previous), _topology_signatures(current))

    def component_preservation(self, previous: Any, current: Any) -> float:
        return _jaccard(_component_signatures(previous), _component_signatures(current))

    def relationship_preservation(self, previous: Any, current: Any) -> float:
        return _jaccard(_relationship_signatures(previous), _relationship_signatures(current))

    def transition_magnitude(self, previous: Any, current: Any) -> float:
        state_distance = self.state_distance(previous, current)
        representation_distance = self.representation_distance(previous, current)
        identity_change = 1.0 - self.identity_preservation(previous, current)
        topology_change = 1.0 - self.topology_preservation(previous, current)
        component_change = 1.0 - self.component_preservation(previous, current)
        relationship_change = 1.0 - self.relationship_preservation(previous, current)
        return _clamp(
            (
                state_distance
                + representation_distance
                + identity_change
                + topology_change
                + component_change
                + relationship_change
            )
            / 6.0
        )

    def structural_consistency(self, previous: Any, current: Any) -> float:
        return _clamp(
            1.0
            - (
                self.state_distance(previous, current)
                + (1.0 - self.component_preservation(previous, current))
                + (1.0 - self.relationship_preservation(previous, current))
                + (1.0 - self.topology_preservation(previous, current))
            )
            / 4.0
        )

    def temporal_consistency(self, previous: Any, current: Any, context: TransportContext | None = None) -> float:
        consistency = 1.0 - (
            self.state_distance(previous, current) * 0.5
            + self.representation_distance(previous, current) * 0.5
        )
        if context is not None and context.previous_revision is not None and context.current_revision is not None:
            consistency *= 1.0 if context.current_revision != context.previous_revision else 0.95
        return _clamp(consistency)

    def compute_all(self, previous: Any, current: Any, *, context: TransportContext | None = None) -> Mapping[str, float]:
        return {
            "state_distance": self.state_distance(previous, current),
            "representation_distance": self.representation_distance(previous, current),
            "identity_preservation": self.identity_preservation(previous, current),
            "topology_preservation": self.topology_preservation(previous, current),
            "component_preservation": self.component_preservation(previous, current),
            "relationship_preservation": self.relationship_preservation(previous, current),
            "transition_magnitude": self.transition_magnitude(previous, current),
            "structural_consistency": self.structural_consistency(previous, current),
            "temporal_consistency": self.temporal_consistency(previous, current, context=context),
        }
