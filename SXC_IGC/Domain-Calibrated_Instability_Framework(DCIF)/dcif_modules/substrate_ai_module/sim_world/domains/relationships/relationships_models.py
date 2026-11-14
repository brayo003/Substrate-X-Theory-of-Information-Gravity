from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

RELATIONSHIP_TYPES: tuple[str, ...] = (
    "Friend",
    "Family",
    "Coworker",
    "Neighbor",
    "Mentor",
    "Student",
    "Leader",
    "Follower",
    "Acquaintance",
    "Stranger",
)


@dataclass(slots=True)
class Relationship:
    relationship_id: str
    entity_a: str
    entity_b: str
    relationship_type: str = "Stranger"
    trust: float = 0.5
    respect: float = 0.5
    familiarity: float = 0.1
    affinity: float = 0.5
    interaction_history: tuple[dict[str, Any], ...] = ()
    last_interaction_tick: int = 0
    strength: float = 0.4

    def __post_init__(self) -> None:
        self.relationship_id = str(self.relationship_id)
        self.entity_a = str(self.entity_a)
        self.entity_b = str(self.entity_b)
        self.relationship_type = str(self.relationship_type)
        self.trust = max(0.0, min(1.0, float(self.trust)))
        self.respect = max(0.0, min(1.0, float(self.respect)))
        self.familiarity = max(0.0, min(1.0, float(self.familiarity)))
        self.affinity = max(0.0, min(1.0, float(self.affinity)))
        self.interaction_history = tuple(dict(item) for item in self.interaction_history)
        self.last_interaction_tick = int(self.last_interaction_tick)
        self.strength = self.calculate_strength()

    def calculate_strength(self) -> float:
        score = 0.3 * self.trust + 0.3 * self.affinity + 0.2 * self.respect + 0.2 * self.familiarity
        return round(max(0.0, min(1.0, score)), 3)

    def to_dict(self) -> dict[str, Any]:
        return {
            "relationship_id": self.relationship_id,
            "entity_a": self.entity_a,
            "entity_b": self.entity_b,
            "relationship_type": self.relationship_type,
            "trust": self.trust,
            "respect": self.respect,
            "familiarity": self.familiarity,
            "affinity": self.affinity,
            "interaction_history": [dict(item) for item in self.interaction_history],
            "last_interaction_tick": self.last_interaction_tick,
            "strength": self.strength,
        }

    @staticmethod
    def from_dict(data: Mapping[str, Any]) -> Relationship:
        rel = Relationship(
            relationship_id=str(data.get("relationship_id", "rel_1")),
            entity_a=str(data.get("entity_a", "e_a")),
            entity_b=str(data.get("entity_b", "e_b")),
            relationship_type=str(data.get("relationship_type", "Stranger")),
            trust=float(data.get("trust", 0.5)),
            respect=float(data.get("respect", 0.5)),
            familiarity=float(data.get("familiarity", 0.1)),
            affinity=float(data.get("affinity", 0.5)),
            interaction_history=tuple(dict(item) for item in data.get("interaction_history", ())),
            last_interaction_tick=int(data.get("last_interaction_tick", 0)),
            strength=float(data.get("strength", 0.4)),
        )
        rel.strength = rel.calculate_strength()
        return rel
