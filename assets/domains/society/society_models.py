from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass(frozen=True)
class Household:
    id: str
    name: str
    member_ids: List[str]
    dwelling_id: Optional[str] = None


@dataclass(frozen=True)
class Family:
    id: str
    household_id: str
    member_ids: List[str]
    relation_type: str = "nuclear"


@dataclass(frozen=True)
class Occupation:
    villager_id: str
    role: str
    assigned_location: Optional[str] = None


@dataclass(frozen=True)
class CommunalProject:
    id: str
    project_type: str
    required_work: float
    completed_work: float = 0.0
    assigned_worker_ids: List[str] = field(default_factory=list)
    status: str = "active"


@dataclass(frozen=True)
class PublicStorage:
    food_reserve: float = 0.0
    wood_reserve: float = 0.0
    tools: int = 0


@dataclass
class VillageState:
    village_id: str
    village_name: str
    leader_id: Optional[str] = None
    households: Dict[str, Household] = field(default_factory=dict)
    families: Dict[str, Family] = field(default_factory=dict)
    occupations: Dict[str, Occupation] = field(default_factory=dict)
    population: int = 0
    workforce: int = 0
    food_reserve: float = 0.0
    wood_reserve: float = 0.0
    emergency_level: float = 0.0
    prosperity: float = 0.0
    stability: float = 1.0
    morale: float = 1.0
    labor_allocation: Dict[str, float] = field(default_factory=dict)
    communal_projects: Dict[str, CommunalProject] = field(default_factory=dict)
    active_celebrations: List[str] = field(default_factory=list)
    active_emergencies: List[str] = field(default_factory=list)
    public_responsibilities: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "village_id": self.village_id,
            "village_name": self.village_name,
            "leader_id": self.leader_id,
            "households": {k: v.__dict__ for k, v in self.households.items()},
            "families": {k: v.__dict__ for k, v in self.families.items()},
            "occupations": {k: v.__dict__ for k, v in self.occupations.items()},
            "population": self.population,
            "workforce": self.workforce,
            "food_reserve": self.food_reserve,
            "wood_reserve": self.wood_reserve,
            "emergency_level": self.emergency_level,
            "prosperity": self.prosperity,
            "stability": self.stability,
            "morale": self.morale,
            "labor_allocation": dict(self.labor_allocation),
            "communal_projects": {k: v.__dict__ for k, v in self.communal_projects.items()},
            "active_celebrations": list(self.active_celebrations),
            "active_emergencies": list(self.active_emergencies),
            "public_responsibilities": dict(self.public_responsibilities),
        }
