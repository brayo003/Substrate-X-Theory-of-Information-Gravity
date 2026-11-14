from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    val = hash(s) % (2**32)
    return abs(val)



def _event_uuid(kind: str, village_id: str, tick_number: int, extra: str = "") -> str:
    key = f"society_event:{kind}:{village_id}:{tick_number}:{extra}"
    val = hash(key) % (2**32)
    return f"event_{abs(val)}"


SOCIETY_EVENT_TYPES = (
    "VillageMeetingHeld",
    "LeaderAssigned",
    "HarvestFestivalStarted",
    "HarvestFestivalEnded",
    "EmergencyDeclared",
    "EmergencyResolved",
    "VillageProspered",
    "VillageDeclined",
    "FoodCrisisStarted",
    "FoodCrisisResolved",
    "PublicProjectStarted",
    "PublicProjectCompleted",
    "MoraleChanged",
    "ProsperityChanged",
    "StabilityChanged",
    "PopulationChanged",
    "CelebrationStarted",
    "CelebrationEnded",
)


@dataclass(frozen=True, slots=True)
class VillageMeetingHeld:
    event_id: str
    tick_number: int
    village_id: str
    attendees: tuple[str, ...]
    agenda: str = ""
    decisions: tuple[str, ...] = tuple()
    metadata: tuple[tuple[str, Any], ...] = tuple()

    @classmethod
    def create(cls, *, village_id: str, tick_number: int, attendees: tuple[str, ...] = tuple(), agenda: str = "", decisions: tuple[str, ...] = tuple(), metadata: Mapping[str, Any] | None = None) -> "VillageMeetingHeld":
        meta = tuple((str(k), v) for k, v in dict(metadata or {}).items())
        return cls(
            event_id=_event_uuid("VillageMeetingHeld", str(village_id), int(tick_number), f"{agenda}"),
            tick_number=int(tick_number),
            village_id=str(village_id),
            attendees=tuple(str(a) for a in attendees),
            agenda=str(agenda),
            decisions=tuple(str(d) for d in decisions),
            metadata=meta,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": "VillageMeetingHeld",
            "tick_number": int(self.tick_number),
            "village_id": str(self.village_id),
            "attendees": list(self.attendees),
            "agenda": str(self.agenda),
            "decisions": list(self.decisions),
            "metadata": {str(k): v for k, v in self.metadata},
        }


@dataclass(frozen=True, slots=True)
class LeaderAssigned:
    event_id: str
    tick_number: int
    village_id: str
    leader_entity_id: str
    leader_role: str
    predecessor_entity_id: str = ""
    metadata: tuple[tuple[str, Any], ...] = tuple()

    @classmethod
    def create(cls, *, village_id: str, tick_number: int, leader_entity_id: str, leader_role: str, predecessor_entity_id: str = "", metadata: Mapping[str, Any] | None = None) -> "LeaderAssigned":
        meta = tuple((str(k), v) for k, v in dict(metadata or {}).items())
        return cls(
            event_id=_event_uuid("LeaderAssigned", str(village_id), int(tick_number), str(leader_entity_id)),
            tick_number=int(tick_number),
            village_id=str(village_id),
            leader_entity_id=str(leader_entity_id),
            leader_role=str(leader_role),
            predecessor_entity_id=str(predecessor_entity_id),
            metadata=meta,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": "LeaderAssigned",
            "tick_number": int(self.tick_number),
            "village_id": str(self.village_id),
            "leader_entity_id": str(self.leader_entity_id),
            "leader_role": str(self.leader_role),
            "predecessor_entity_id": str(self.predecessor_entity_id),
            "metadata": {str(k): v for k, v in self.metadata},
        }


@dataclass(frozen=True, slots=True)
class HarvestFestivalStarted:
    event_id: str
    tick_number: int
    village_id: str
    celebration_id: str
    organizer: str = ""
    participants: tuple[str, ...] = tuple()
    metadata: tuple[tuple[str, Any], ...] = tuple()

    @classmethod
    def create(cls, *, village_id: str, tick_number: int, celebration_id: str, organizer: str = "", participants: tuple[str, ...] = tuple(), metadata: Mapping[str, Any] | None = None) -> "HarvestFestivalStarted":
        meta = tuple((str(k), v) for k, v in dict(metadata or {}).items())
        return cls(
            event_id=_event_uuid("HarvestFestivalStarted", str(village_id), int(tick_number), str(celebration_id)),
            tick_number=int(tick_number),
            village_id=str(village_id),
            celebration_id=str(celebration_id),
            organizer=str(organizer),
            participants=tuple(str(p) for p in participants),
            metadata=meta,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": "HarvestFestivalStarted",
            "tick_number": int(self.tick_number),
            "village_id": str(self.village_id),
            "celebration_id": str(self.celebration_id),
            "organizer": str(self.organizer),
            "participants": list(self.participants),
            "metadata": {str(k): v for k, v in self.metadata},
        }


@dataclass(frozen=True, slots=True)
class HarvestFestivalEnded:
    event_id: str
    tick_number: int
    village_id: str
    celebration_id: str
    total_participants: int = 0
    harvest_yield: float = 0.0
    metadata: tuple[tuple[str, Any], ...] = tuple()

    @classmethod
    def create(cls, *, village_id: str, tick_number: int, celebration_id: str, total_participants: int = 0, harvest_yield: float = 0.0, metadata: Mapping[str, Any] | None = None) -> "HarvestFestivalEnded":
        meta = tuple((str(k), v) for k, v in dict(metadata or {}).items())
        return cls(
            event_id=_event_uuid("HarvestFestivalEnded", str(village_id), int(tick_number), str(celebration_id)),
            tick_number=int(tick_number),
            village_id=str(village_id),
            celebration_id=str(celebration_id),
            total_participants=int(total_participants),
            harvest_yield=float(harvest_yield),
            metadata=meta,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": "HarvestFestivalEnded",
            "tick_number": int(self.tick_number),
            "village_id": str(self.village_id),
            "celebration_id": str(self.celebration_id),
            "total_participants": int(self.total_participants),
            "harvest_yield": float(self.harvest_yield),
            "metadata": {str(k): v for k, v in self.metadata},
        }


@dataclass(frozen=True, slots=True)
class EmergencyDeclared:
    event_id: str
    tick_number: int
    village_id: str
    emergency_id: str
    emergency_type: str
    severity: float
    affected: tuple[str, ...] = tuple()
    metadata: tuple[tuple[str, Any], ...] = tuple()

    @classmethod
    def create(cls, *, village_id: str, tick_number: int, emergency_id: str, emergency_type: str, severity: float, affected: tuple[str, ...] = tuple(), metadata: Mapping[str, Any] | None = None) -> "EmergencyDeclared":
        meta = tuple((str(k), v) for k, v in dict(metadata or {}).items())
        return cls(
            event_id=_event_uuid("EmergencyDeclared", str(village_id), int(tick_number), f"{emergency_id}:{emergency_type}"),
            tick_number=int(tick_number),
            village_id=str(village_id),
            emergency_id=str(emergency_id),
            emergency_type=str(emergency_type),
            severity=float(severity),
            affected=tuple(str(a) for a in affected),
            metadata=meta,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": "EmergencyDeclared",
            "tick_number": int(self.tick_number),
            "village_id": str(self.village_id),
            "emergency_id": str(self.emergency_id),
            "emergency_type": str(self.emergency_type),
            "severity": float(self.severity),
            "affected": list(self.affected),
            "metadata": {str(k): v for k, v in self.metadata},
        }


@dataclass(frozen=True, slots=True)
class EmergencyResolved:
    event_id: str
    tick_number: int
    village_id: str
    emergency_id: str
    emergency_type: str
    responders: tuple[str, ...] = tuple()
    duration_ticks: int = 0
    metadata: tuple[tuple[str, Any], ...] = tuple()

    @classmethod
    def create(cls, *, village_id: str, tick_number: int, emergency_id: str, emergency_type: str, responders: tuple[str, ...] = tuple(), duration_ticks: int = 0, metadata: Mapping[str, Any] | None = None) -> "EmergencyResolved":
        meta = tuple((str(k), v) for k, v in dict(metadata or {}).items())
        return cls(
            event_id=_event_uuid("EmergencyResolved", str(village_id), int(tick_number), f"{emergency_id}:{emergency_type}"),
            tick_number=int(tick_number),
            village_id=str(village_id),
            emergency_id=str(emergency_id),
            emergency_type=str(emergency_type),
            responders=tuple(str(r) for r in responders),
            duration_ticks=int(duration_ticks),
            metadata=meta,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": "EmergencyResolved",
            "tick_number": int(self.tick_number),
            "village_id": str(self.village_id),
            "emergency_id": str(self.emergency_id),
            "emergency_type": str(self.emergency_type),
            "responders": list(self.responders),
            "duration_ticks": int(self.duration_ticks),
            "metadata": {str(k): v for k, v in self.metadata},
        }


@dataclass(frozen=True, slots=True)
class VillageProspered:
    event_id: str
    tick_number: int
    village_id: str
    prosperity_delta: float
    new_prosperity: float
    contributing_factors: tuple[str, ...] = tuple()
    metadata: tuple[tuple[str, Any], ...] = tuple()

    @classmethod
    def create(cls, *, village_id: str, tick_number: int, prosperity_delta: float, new_prosperity: float, contributing_factors: tuple[str, ...] = tuple(), metadata: Mapping[str, Any] | None = None) -> "VillageProspered":
        meta = tuple((str(k), v) for k, v in dict(metadata or {}).items())
        return cls(
            event_id=_event_uuid("VillageProspered", str(village_id), int(tick_number), f"{new_prosperity:.6f}"),
            tick_number=int(tick_number),
            village_id=str(village_id),
            prosperity_delta=float(prosperity_delta),
            new_prosperity=float(new_prosperity),
            contributing_factors=tuple(str(c) for c in contributing_factors),
            metadata=meta,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": "VillageProspered",
            "tick_number": int(self.tick_number),
            "village_id": str(self.village_id),
            "prosperity_delta": float(self.prosperity_delta),
            "new_prosperity": float(self.new_prosperity),
            "contributing_factors": list(self.contributing_factors),
            "metadata": {str(k): v for k, v in self.metadata},
        }


@dataclass(frozen=True, slots=True)
class VillageDeclined:
    event_id: str
    tick_number: int
    village_id: str
    prosperity_delta: float
    new_prosperity: float
    contributing_factors: tuple[str, ...] = tuple()
    metadata: tuple[tuple[str, Any], ...] = tuple()

    @classmethod
    def create(cls, *, village_id: str, tick_number: int, prosperity_delta: float, new_prosperity: float, contributing_factors: tuple[str, ...] = tuple(), metadata: Mapping[str, Any] | None = None) -> "VillageDeclined":
        meta = tuple((str(k), v) for k, v in dict(metadata or {}).items())
        return cls(
            event_id=_event_uuid("VillageDeclined", str(village_id), int(tick_number), f"{new_prosperity:.6f}"),
            tick_number=int(tick_number),
            village_id=str(village_id),
            prosperity_delta=float(prosperity_delta),
            new_prosperity=float(new_prosperity),
            contributing_factors=tuple(str(c) for c in contributing_factors),
            metadata=meta,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": "VillageDeclined",
            "tick_number": int(self.tick_number),
            "village_id": str(self.village_id),
            "prosperity_delta": float(self.prosperity_delta),
            "new_prosperity": float(self.new_prosperity),
            "contributing_factors": list(self.contributing_factors),
            "metadata": {str(k): v for k, v in self.metadata},
        }


@dataclass(frozen=True, slots=True)
class FoodCrisisStarted:
    event_id: str
    tick_number: int
    village_id: str
    reserve_shortfall: float
    estimated_days_remaining: float = 0.0
    metadata: tuple[tuple[str, Any], ...] = tuple()

    @classmethod
    def create(cls, *, village_id: str, tick_number: int, reserve_shortfall: float, estimated_days_remaining: float = 0.0, metadata: Mapping[str, Any] | None = None) -> "FoodCrisisStarted":
        meta = tuple((str(k), v) for k, v in dict(metadata or {}).items())
        return cls(
            event_id=_event_uuid("FoodCrisisStarted", str(village_id), int(tick_number), f"{reserve_shortfall:.6f}"),
            tick_number=int(tick_number),
            village_id=str(village_id),
            reserve_shortfall=float(reserve_shortfall),
            estimated_days_remaining=float(estimated_days_remaining),
            metadata=meta,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": "FoodCrisisStarted",
            "tick_number": int(self.tick_number),
            "village_id": str(self.village_id),
            "reserve_shortfall": float(self.reserve_shortfall),
            "estimated_days_remaining": float(self.estimated_days_remaining),
            "metadata": {str(k): v for k, v in self.metadata},
        }


@dataclass(frozen=True, slots=True)
class FoodCrisisResolved:
    event_id: str
    tick_number: int
    village_id: str
    recovery_food_reserve: float
    duration_ticks: int = 0
    metadata: tuple[tuple[str, Any], ...] = tuple()

    @classmethod
    def create(cls, *, village_id: str, tick_number: int, recovery_food_reserve: float, duration_ticks: int = 0, metadata: Mapping[str, Any] | None = None) -> "FoodCrisisResolved":
        meta = tuple((str(k), v) for k, v in dict(metadata or {}).items())
        return cls(
            event_id=_event_uuid("FoodCrisisResolved", str(village_id), int(tick_number), f"{recovery_food_reserve:.6f}"),
            tick_number=int(tick_number),
            village_id=str(village_id),
            recovery_food_reserve=float(recovery_food_reserve),
            duration_ticks=int(duration_ticks),
            metadata=meta,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": "FoodCrisisResolved",
            "tick_number": int(self.tick_number),
            "village_id": str(self.village_id),
            "recovery_food_reserve": float(self.recovery_food_reserve),
            "duration_ticks": int(self.duration_ticks),
            "metadata": {str(k): v for k, v in self.metadata},
        }


@dataclass(frozen=True, slots=True)
class PublicProjectStarted:
    event_id: str
    tick_number: int
    village_id: str
    project_id: str
    project_type: str
    project_name: str = ""
    assigned_workers: tuple[str, ...] = tuple()
    metadata: tuple[tuple[str, Any], ...] = tuple()

    @classmethod
    def create(cls, *, village_id: str, tick_number: int, project_id: str, project_type: str, project_name: str = "", assigned_workers: tuple[str, ...] = tuple(), metadata: Mapping[str, Any] | None = None) -> "PublicProjectStarted":
        meta = tuple((str(k), v) for k, v in dict(metadata or {}).items())
        return cls(
            event_id=_event_uuid("PublicProjectStarted", str(village_id), int(tick_number), str(project_id)),
            tick_number=int(tick_number),
            village_id=str(village_id),
            project_id=str(project_id),
            project_type=str(project_type),
            project_name=str(project_name),
            assigned_workers=tuple(str(a) for a in assigned_workers),
            metadata=meta,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": "PublicProjectStarted",
            "tick_number": int(self.tick_number),
            "village_id": str(self.village_id),
            "project_id": str(self.project_id),
            "project_type": str(self.project_type),
            "project_name": str(self.project_name),
            "assigned_workers": list(self.assigned_workers),
            "metadata": {str(k): v for k, v in self.metadata},
        }


@dataclass(frozen=True, slots=True)
class PublicProjectCompleted:
    event_id: str
    tick_number: int
    village_id: str
    project_id: str
    project_type: str
    total_workers_involved: int = 0
    duration_ticks: int = 0
    metadata: tuple[tuple[str, Any], ...] = tuple()

    @classmethod
    def create(cls, *, village_id: str, tick_number: int, project_id: str, project_type: str, total_workers_involved: int = 0, duration_ticks: int = 0, metadata: Mapping[str, Any] | None = None) -> "PublicProjectCompleted":
        meta = tuple((str(k), v) for k, v in dict(metadata or {}).items())
        return cls(
            event_id=_event_uuid("PublicProjectCompleted", str(village_id), int(tick_number), str(project_id)),
            tick_number=int(tick_number),
            village_id=str(village_id),
            project_id=str(project_id),
            project_type=str(project_type),
            total_workers_involved=int(total_workers_involved),
            duration_ticks=int(duration_ticks),
            metadata=meta,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": "PublicProjectCompleted",
            "tick_number": int(self.tick_number),
            "village_id": str(self.village_id),
            "project_id": str(self.project_id),
            "project_type": str(self.project_type),
            "total_workers_involved": int(self.total_workers_involved),
            "duration_ticks": int(self.duration_ticks),
            "metadata": {str(k): v for k, v in self.metadata},
        }


@dataclass(frozen=True, slots=True)
class MoraleChanged:
    event_id: str
    tick_number: int
    village_id: str
    old_morale: float
    new_morale: float
    causes: tuple[str, ...] = tuple()
    metadata: tuple[tuple[str, Any], ...] = tuple()

    @classmethod
    def create(cls, *, village_id: str, tick_number: int, old_morale: float, new_morale: float, causes: tuple[str, ...] = tuple(), metadata: Mapping[str, Any] | None = None) -> "MoraleChanged":
        meta = tuple((str(k), v) for k, v in dict(metadata or {}).items())
        return cls(
            event_id=_event_uuid("MoraleChanged", str(village_id), int(tick_number), f"{old_morale:.6f}:{new_morale:.6f}"),
            tick_number=int(tick_number),
            village_id=str(village_id),
            old_morale=float(old_morale),
            new_morale=float(new_morale),
            causes=tuple(str(c) for c in causes),
            metadata=meta,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": "MoraleChanged",
            "tick_number": int(self.tick_number),
            "village_id": str(self.village_id),
            "old_morale": float(self.old_morale),
            "new_morale": float(self.new_morale),
            "causes": list(self.causes),
            "metadata": {str(k): v for k, v in self.metadata},
        }


@dataclass(frozen=True, slots=True)
class ProsperityChanged:
    event_id: str
    tick_number: int
    village_id: str
    old_prosperity: float
    new_prosperity: float
    metadata: tuple[tuple[str, Any], ...] = tuple()

    @classmethod
    def create(cls, *, village_id: str, tick_number: int, old_prosperity: float, new_prosperity: float, metadata: Mapping[str, Any] | None = None) -> "ProsperityChanged":
        meta = tuple((str(k), v) for k, v in dict(metadata or {}).items())
        return cls(
            event_id=_event_uuid("ProsperityChanged", str(village_id), int(tick_number), f"{old_prosperity:.6f}:{new_prosperity:.6f}"),
            tick_number=int(tick_number),
            village_id=str(village_id),
            old_prosperity=float(old_prosperity),
            new_prosperity=float(new_prosperity),
            metadata=meta,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": "ProsperityChanged",
            "tick_number": int(self.tick_number),
            "village_id": str(self.village_id),
            "old_prosperity": float(self.old_prosperity),
            "new_prosperity": float(self.new_prosperity),
            "metadata": {str(k): v for k, v in self.metadata},
        }


@dataclass(frozen=True, slots=True)
class StabilityChanged:
    event_id: str
    tick_number: int
    village_id: str
    old_stability: float
    new_stability: float
    causes: tuple[str, ...] = tuple()
    metadata: tuple[tuple[str, Any], ...] = tuple()

    @classmethod
    def create(cls, *, village_id: str, tick_number: int, old_stability: float, new_stability: float, causes: tuple[str, ...] = tuple(), metadata: Mapping[str, Any] | None = None) -> "StabilityChanged":
        meta = tuple((str(k), v) for k, v in dict(metadata or {}).items())
        return cls(
            event_id=_event_uuid("StabilityChanged", str(village_id), int(tick_number), f"{old_stability:.6f}:{new_stability:.6f}"),
            tick_number=int(tick_number),
            village_id=str(village_id),
            old_stability=float(old_stability),
            new_stability=float(new_stability),
            causes=tuple(str(c) for c in causes),
            metadata=meta,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": "StabilityChanged",
            "tick_number": int(self.tick_number),
            "village_id": str(self.village_id),
            "old_stability": float(self.old_stability),
            "new_stability": float(self.new_stability),
            "causes": list(self.causes),
            "metadata": {str(k): v for k, v in self.metadata},
        }


@dataclass(frozen=True, slots=True)
class PopulationChanged:
    event_id: str
    tick_number: int
    village_id: str
    old_population: int
    new_population: int
    delta: int
    reason: str = ""
    metadata: tuple[tuple[str, Any], ...] = tuple()

    @classmethod
    def create(cls, *, village_id: str, tick_number: int, old_population: int, new_population: int, delta: int, reason: str = "", metadata: Mapping[str, Any] | None = None) -> "PopulationChanged":
        meta = tuple((str(k), v) for k, v in dict(metadata or {}).items())
        return cls(
            event_id=_event_uuid("PopulationChanged", str(village_id), int(tick_number), f"{old_population}:{new_population}:{delta}"),
            tick_number=int(tick_number),
            village_id=str(village_id),
            old_population=int(old_population),
            new_population=int(new_population),
            delta=int(delta),
            reason=str(reason),
            metadata=meta,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": "PopulationChanged",
            "tick_number": int(self.tick_number),
            "village_id": str(self.village_id),
            "old_population": int(self.old_population),
            "new_population": int(self.new_population),
            "delta": int(self.delta),
            "reason": str(self.reason),
            "metadata": {str(k): v for k, v in self.metadata},
        }


@dataclass(frozen=True, slots=True)
class CelebrationStarted:
    event_id: str
    tick_number: int
    village_id: str
    celebration_id: str
    celebration_type: str
    organizer: str = ""
    participants: tuple[str, ...] = tuple()
    metadata: tuple[tuple[str, Any], ...] = tuple()

    @classmethod
    def create(cls, *, village_id: str, tick_number: int, celebration_id: str, celebration_type: str, organizer: str = "", participants: tuple[str, ...] = tuple(), metadata: Mapping[str, Any] | None = None) -> "CelebrationStarted":
        meta = tuple((str(k), v) for k, v in dict(metadata or {}).items())
        return cls(
            event_id=_event_uuid("CelebrationStarted", str(village_id), int(tick_number), f"{celebration_id}:{celebration_type}"),
            tick_number=int(tick_number),
            village_id=str(village_id),
            celebration_id=str(celebration_id),
            celebration_type=str(celebration_type),
            organizer=str(organizer),
            participants=tuple(str(p) for p in participants),
            metadata=meta,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": "CelebrationStarted",
            "tick_number": int(self.tick_number),
            "village_id": str(self.village_id),
            "celebration_id": str(self.celebration_id),
            "celebration_type": str(self.celebration_type),
            "organizer": str(self.organizer),
            "participants": list(self.participants),
            "metadata": {str(k): v for k, v in self.metadata},
        }


@dataclass(frozen=True, slots=True)
class CelebrationEnded:
    event_id: str
    tick_number: int
    village_id: str
    celebration_id: str
    celebration_type: str
    total_participants: int = 0
    duration_ticks: int = 0
    metadata: tuple[tuple[str, Any], ...] = tuple()

    @classmethod
    def create(cls, *, village_id: str, tick_number: int, celebration_id: str, celebration_type: str, total_participants: int = 0, duration_ticks: int = 0, metadata: Mapping[str, Any] | None = None) -> "CelebrationEnded":
        meta = tuple((str(k), v) for k, v in dict(metadata or {}).items())
        return cls(
            event_id=_event_uuid("CelebrationEnded", str(village_id), int(tick_number), f"{celebration_id}:{celebration_type}"),
            tick_number=int(tick_number),
            village_id=str(village_id),
            celebration_id=str(celebration_id),
            celebration_type=str(celebration_type),
            total_participants=int(total_participants),
            duration_ticks=int(duration_ticks),
            metadata=meta,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": "CelebrationEnded",
            "tick_number": int(self.tick_number),
            "village_id": str(self.village_id),
            "celebration_id": str(self.celebration_id),
            "celebration_type": str(self.celebration_type),
            "total_participants": int(self.total_participants),
            "duration_ticks": int(self.duration_ticks),
            "metadata": {str(k): v for k, v in self.metadata},
        }
