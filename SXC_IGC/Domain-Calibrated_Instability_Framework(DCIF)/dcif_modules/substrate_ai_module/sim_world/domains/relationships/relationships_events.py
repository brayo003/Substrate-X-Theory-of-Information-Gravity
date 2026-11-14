from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class RelationshipCreated:
    relationship_id: str
    entity_a: str
    entity_b: str
    relationship_type: str
    tick: int = 0
    event_type: str = field(default="RelationshipCreated", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "relationship_id": self.relationship_id,
            "entity_a": self.entity_a,
            "entity_b": self.entity_b,
            "relationship_type": self.relationship_type,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class RelationshipStrengthened:
    relationship_id: str
    old_strength: float
    new_strength: float
    tick: int = 0
    event_type: str = field(default="RelationshipStrengthened", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "relationship_id": self.relationship_id,
            "old_strength": self.old_strength,
            "new_strength": self.new_strength,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class RelationshipWeakened:
    relationship_id: str
    old_strength: float
    new_strength: float
    tick: int = 0
    event_type: str = field(default="RelationshipWeakened", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "relationship_id": self.relationship_id,
            "old_strength": self.old_strength,
            "new_strength": self.new_strength,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class TrustIncreased:
    relationship_id: str
    delta: float
    new_trust: float
    tick: int = 0
    event_type: str = field(default="TrustIncreased", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "relationship_id": self.relationship_id,
            "delta": self.delta,
            "new_trust": self.new_trust,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class TrustReduced:
    relationship_id: str
    delta: float
    new_trust: float
    tick: int = 0
    event_type: str = field(default="TrustReduced", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "relationship_id": self.relationship_id,
            "delta": self.delta,
            "new_trust": self.new_trust,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class RespectIncreased:
    relationship_id: str
    delta: float
    new_respect: float
    tick: int = 0
    event_type: str = field(default="RespectIncreased", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "relationship_id": self.relationship_id,
            "delta": self.delta,
            "new_respect": self.new_respect,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class RespectReduced:
    relationship_id: str
    delta: float
    new_respect: float
    tick: int = 0
    event_type: str = field(default="RespectReduced", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "relationship_id": self.relationship_id,
            "delta": self.delta,
            "new_respect": self.new_respect,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class InteractionRecorded:
    relationship_id: str
    interaction_type: str
    actor_id: str
    target_id: str
    tick: int = 0
    event_type: str = field(default="InteractionRecorded", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "relationship_id": self.relationship_id,
            "interaction_type": self.interaction_type,
            "actor_id": self.actor_id,
            "target_id": self.target_id,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class FriendshipFormed:
    relationship_id: str
    entity_a: str
    entity_b: str
    tick: int = 0
    event_type: str = field(default="FriendshipFormed", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "relationship_id": self.relationship_id,
            "entity_a": self.entity_a,
            "entity_b": self.entity_b,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class ConflictOccurred:
    relationship_id: str
    actor_id: str
    target_id: str
    tick: int = 0
    event_type: str = field(default="ConflictOccurred", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "relationship_id": self.relationship_id,
            "actor_id": self.actor_id,
            "target_id": self.target_id,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class RelationshipExpired:
    relationship_id: str
    entity_a: str
    entity_b: str
    tick: int = 0
    event_type: str = field(default="RelationshipExpired", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "relationship_id": self.relationship_id,
            "entity_a": self.entity_a,
            "entity_b": self.entity_b,
            "tick": self.tick,
        }
