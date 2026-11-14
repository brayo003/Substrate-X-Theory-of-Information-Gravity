from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class VillageMeetingHeld:
    village_id: str
    topic: str
    leader_id: Optional[str]
    attendees: List[str]
    tick: int = 0


@dataclass(frozen=True)
class LeaderAssigned:
    village_id: str
    leader_id: str
    tick: int = 0


@dataclass(frozen=True)
class HarvestFestivalStarted:
    village_id: str
    tick: int = 0


@dataclass(frozen=True)
class HarvestFestivalEnded:
    village_id: str
    tick: int = 0


@dataclass(frozen=True)
class EmergencyDeclared:
    village_id: str
    emergency_type: str
    severity: float
    tick: int = 0


@dataclass(frozen=True)
class EmergencyResolved:
    village_id: str
    emergency_type: str
    tick: int = 0


@dataclass(frozen=True)
class VillageProspered:
    village_id: str
    prosperity: float
    tick: int = 0


@dataclass(frozen=True)
class VillageDeclined:
    village_id: str
    reason: str
    tick: int = 0


@dataclass(frozen=True)
class FoodCrisisStarted:
    village_id: str
    tick: int = 0


@dataclass(frozen=True)
class FoodCrisisResolved:
    village_id: str
    tick: int = 0


@dataclass(frozen=True)
class PublicProjectStarted:
    project_id: str
    project_type: str
    village_id: str
    tick: int = 0


@dataclass(frozen=True)
class PublicProjectCompleted:
    project_id: str
    project_type: str
    village_id: str
    tick: int = 0


@dataclass(frozen=True)
class MoraleChanged:
    village_id: str
    old_morale: float
    new_morale: float
    tick: int = 0


@dataclass(frozen=True)
class ProsperityChanged:
    village_id: str
    old_prosperity: float
    new_prosperity: float
    tick: int = 0


@dataclass(frozen=True)
class StabilityChanged:
    village_id: str
    old_stability: float
    new_stability: float
    tick: int = 0


@dataclass(frozen=True)
class PopulationChanged:
    village_id: str
    old_population: int
    new_population: int
    tick: int = 0
