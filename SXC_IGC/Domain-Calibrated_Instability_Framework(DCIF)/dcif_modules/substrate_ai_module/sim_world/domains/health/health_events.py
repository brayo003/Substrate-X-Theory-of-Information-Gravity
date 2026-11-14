from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class HealthEvent:
    tick_number: int
    entity_id: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def _base_dict(self, event_type: str) -> dict[str, Any]:
        meta: dict[str, Any] = {}
        if self.metadata:
            try:
                meta = {k: v for k, v in dict(self.metadata).items()}
            except Exception:
                meta = {}
        return {
            "event_type": str(event_type),
            "tick_number": int(self.tick_number),
            "entity_id": str(self.entity_id),
            "metadata": meta,
        }


@dataclass(frozen=True)
class HealthImproved(HealthEvent):
    delta_health: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        d = self._base_dict("HealthImproved")
        d["delta_health"] = float(self.delta_health)
        return d


@dataclass(frozen=True)
class HealthDeclined(HealthEvent):
    delta_health: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        d = self._base_dict("HealthDeclined")
        d["delta_health"] = float(self.delta_health)
        return d


@dataclass(frozen=True)
class FatigueIncreased(HealthEvent):
    delta_fatigue: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        d = self._base_dict("FatigueIncreased")
        d["delta_fatigue"] = float(self.delta_fatigue)
        return d


@dataclass(frozen=True)
class FatigueRecovered(HealthEvent):
    delta_fatigue: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        d = self._base_dict("FatigueRecovered")
        d["delta_fatigue"] = float(self.delta_fatigue)
        return d


@dataclass(frozen=True)
class IllnessStarted(HealthEvent):
    illness_type: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = self._base_dict("IllnessStarted")
        d["illness_type"] = str(self.illness_type)
        return d


@dataclass(frozen=True)
class IllnessRecovered(HealthEvent):
    illness_type: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = self._base_dict("IllnessRecovered")
        d["illness_type"] = str(self.illness_type)
        return d


@dataclass(frozen=True)
class InjuryOccurred(HealthEvent):
    injury_type: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = self._base_dict("InjuryOccurred")
        d["injury_type"] = str(self.injury_type)
        return d


@dataclass(frozen=True)
class InjuryRecovered(HealthEvent):
    injury_type: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = self._base_dict("InjuryRecovered")
        d["injury_type"] = str(self.injury_type)
        return d


@dataclass(frozen=True)
class Dehydrated(HealthEvent):
    hydration_level: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        d = self._base_dict("Dehydrated")
        d["hydration_level"] = float(self.hydration_level)
        return d


@dataclass(frozen=True)
class Malnourished(HealthEvent):
    nutrition_level: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        d = self._base_dict("Malnourished")
        d["nutrition_level"] = float(self.nutrition_level)
        return d


@dataclass(frozen=True)
class HypothermiaStarted(HealthEvent):
    body_temperature_c: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        d = self._base_dict("HypothermiaStarted")
        d["body_temperature_c"] = float(self.body_temperature_c)
        return d


@dataclass(frozen=True)
class HeatStressStarted(HealthEvent):
    body_temperature_c: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        d = self._base_dict("HeatStressStarted")
        d["body_temperature_c"] = float(self.body_temperature_c)
        return d


@dataclass(frozen=True)
class DeathOccurred(HealthEvent):
    cause: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = self._base_dict("DeathOccurred")
        d["cause"] = str(self.cause)
        return d


@dataclass(frozen=True)
class RecoveryStarted(HealthEvent):
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = self._base_dict("RecoveryStarted")
        d["reason"] = str(self.reason)
        return d


@dataclass(frozen=True)
class RecoveryCompleted(HealthEvent):
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = self._base_dict("RecoveryCompleted")
        d["reason"] = str(self.reason)
        return d


HEALTH_EVENT_TYPES = (
    "HealthImproved",
    "HealthDeclined",
    "FatigueIncreased",
    "FatigueRecovered",
    "IllnessStarted",
    "IllnessRecovered",
    "InjuryOccurred",
    "InjuryRecovered",
    "Dehydrated",
    "Malnourished",
    "HypothermiaStarted",
    "HeatStressStarted",
    "DeathOccurred",
    "RecoveryStarted",
    "RecoveryCompleted",
)
