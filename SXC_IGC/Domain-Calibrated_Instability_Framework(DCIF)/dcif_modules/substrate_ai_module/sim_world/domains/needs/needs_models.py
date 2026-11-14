from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class NeedDescriptor:
    name: str
    current: float
    minimum: float = 0.0
    maximum: float = 1.0
    decay_rate: float = 0.02
    recovery_rate: float = 0.35
    critical_threshold: float = 0.7  # For hunger/thirst (high = bad); for energy/social/warmth/comfort (low = bad)

    def clamp(self, value: float) -> float:
        return max(self.minimum, min(self.maximum, float(value)))


@dataclass(frozen=True, slots=True)
class VillagerTraits:
    occupation: str
    hunger_decay_mult: float = 1.0
    thirst_decay_mult: float = 1.0
    energy_decay_mult: float = 1.0
    social_decay_mult: float = 1.0
    max_energy: float = 1.0


TRAIT_MAP: dict[str, VillagerTraits] = {
    "farmer": VillagerTraits(occupation="farmer", social_decay_mult=0.7),
    "hunter": VillagerTraits(occupation="hunter", energy_decay_mult=1.3),
    "innkeeper": VillagerTraits(occupation="innkeeper", social_decay_mult=0.5),
    "child": VillagerTraits(occupation="child", hunger_decay_mult=1.4),
    "elder": VillagerTraits(occupation="elder", energy_decay_mult=1.3, max_energy=0.7),
    "blacksmith": VillagerTraits(occupation="blacksmith", energy_decay_mult=1.1),
    "merchant": VillagerTraits(occupation="merchant", social_decay_mult=0.8),
    "woodcutter": VillagerTraits(occupation="woodcutter", energy_decay_mult=1.2),
    "traveler": VillagerTraits(occupation="traveler", social_decay_mult=0.9),
    "village leader": VillagerTraits(occupation="village leader", social_decay_mult=0.8),
}


def get_traits(occupation: str) -> VillagerTraits:
    return TRAIT_MAP.get(str(occupation).lower(), VillagerTraits(occupation=occupation))
