from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


VILLAGE_ID_PREFIX = "village"
HOUSEHOLD_ID_PREFIX = "household"
PROJECT_ID_PREFIX = "communal_project"
CELEBRATION_ID_PREFIX = "celebration"
EMERGENCY_ID_PREFIX = "emergency"
LABOR_ID_PREFIX = "labor_alloc"


SOCIETY_METRIC_MIN: float = 0.0
SOCIETY_METRIC_MAX: float = 1.0
DEFAULT_PROSPERITY: float = 0.6
DEFAULT_STABILITY: float = 0.7
DEFAULT_MORALE: float = 0.65
DEFAULT_EMERGENCY_LEVEL: float = 0.0
EMERGENCY_THRESHOLD: float = 0.5
FOOD_CRISIS_RESERVE_PER_PERSON: float = 5.0
WOOD_RESERVE_MIN_PER_HOUSEHOLD: float = 10.0


EMERGENCY_TYPES = (
    "FoodCrisis",
    "Flood",
    "Fire",
    "DiseaseOutbreak",
    "ResourceShortage",
    "WorkforceShortage",
    "StormDamage",
    "CivilUnrest",
)

PROJECT_TYPES = (
    "Harvest",
    "RoadRepair",
    "BridgeRepair",
    "StorageOrganization",
    "FireResponse",
    "ConstructionSupport",
    "WellDigging",
    "WallReinforcement",
    "FoodPreservation",
)

CELEBRATION_TYPES = (
    "HarvestFestival",
    "FoundingDay",
    "WeddingFeast",
    "SeasonalFestival",
    "Midsummer",
    "Midwinter",
)

LEADERSHIP_ROLES = (
    "Elder",
    "Headman",
    "Mayor",
    "Councillor",
    "Priest",
    "Commander",
)


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    v = float(value)
    if v < lo:
        return lo
    if v > hi:
        return hi
    return v


def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    
    val = hash(s) % (2**32)
    return abs(val)


def make_village_id(world_id: str, village_name: str) -> str:
    key = f"{VILLAGE_ID_PREFIX}:{world_id}:{village_name}"
    return f"{VILLAGE_ID_PREFIX}_{deterministic_hash(key)}"


def make_household_id(village_id: str, household_name: str) -> str:
    key = f"{HOUSEHOLD_ID_PREFIX}:{village_id}:{household_name}"
    return f"{HOUSEHOLD_ID_PREFIX}_{deterministic_hash(key)}"


def make_project_id(village_id: str, project_type: str, tick_number: int) -> str:
    key = f"{PROJECT_ID_PREFIX}:{village_id}:{project_type}:{tick_number}"
    return f"{PROJECT_ID_PREFIX}_{deterministic_hash(key)}"


def make_celebration_id(village_id: str, celebration_type: str, tick_number: int) -> str:
    key = f"{CELEBRATION_ID_PREFIX}:{village_id}:{celebration_type}:{tick_number}"
    return f"{CELEBRATION_ID_PREFIX}_{deterministic_hash(key)}"


def make_emergency_id(village_id: str, emergency_type: str) -> str:
    key = f"{EMERGENCY_ID_PREFIX}:{village_id}:{emergency_type}"
    return f"{EMERGENCY_ID_PREFIX}_{deterministic_hash(key)}"


def _as_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except Exception:
        return float(default)


def _as_int(v: Any, default: int = 0) -> int:
    try:
        return int(v)
    except Exception:
        return int(default)


def _as_bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return bool(int(v) != 0)
    s = str(v).strip().lower()
    return s in {"1", "true", "yes", "on", "active"}


def _as_tuple_of_str(value: Any) -> tuple[str, ...]:
    if value is None:
        return tuple()
    if isinstance(value, (str, bytes)):
        s = str(value).strip()
        if not s:
            return tuple()
        return (s,)
    out: list[str] = []
    for item in value:
        out.append(str(item))
    return tuple(out)


def _as_tuple_of_float(value: Any) -> tuple[float, ...]:
    if value is None:
        return tuple()
    if isinstance(value, (int, float)):
        return (float(value),)
    out: list[float] = []
    for item in value:
        try:
            out.append(float(item))
        except Exception:
            out.append(0.0)
    return tuple(out)


def _as_mapping(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    try:
        if hasattr(value, "items"):
            return {str(k): v for k, v in dict(value).items()}
    except Exception:
        pass
    return {}


@dataclass(frozen=True, slots=True)
class Household:
    household_id: str
    name: str
    village_id: str
    members: tuple[str, ...] = tuple()
    head_of_household: str = ""
    residence_location: str = ""
    food_store: float = 0.0
    wood_store: float = 0.0
    founded_tick: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "household_id": str(self.household_id),
            "name": str(self.name),
            "village_id": str(self.village_id),
            "members": list(self.members),
            "head_of_household": str(self.head_of_household),
            "residence_location": str(self.residence_location),
            "food_store": float(self.food_store),
            "wood_store": float(self.wood_store),
            "founded_tick": int(self.founded_tick),
        }

    @classmethod
    def from_dict(cls, d: Mapping[str, Any]) -> "Household":
        return cls(
            household_id=str(d.get("household_id")),
            name=str(d.get("name", "Household")),
            village_id=str(d.get("village_id")),
            members=_as_tuple_of_str(d.get("members")),
            head_of_household=str(d.get("head_of_household", "")),
            residence_location=str(d.get("residence_location", "")),
            food_store=_as_float(d.get("food_store"), 0.0),
            wood_store=_as_float(d.get("wood_store"), 0.0),
            founded_tick=_as_int(d.get("founded_tick"), 0),
        )


@dataclass(frozen=True, slots=True)
class LaborAllocation:
    allocation_id: str
    sector: str
    assigned_workers: tuple[str, ...] = tuple()
    required_workers: int = 0
    priority: float = 0.5
    start_tick: int = 0
    progress: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "allocation_id": str(self.allocation_id),
            "sector": str(self.sector),
            "assigned_workers": list(self.assigned_workers),
            "required_workers": int(self.required_workers),
            "priority": float(self.priority),
            "start_tick": int(self.start_tick),
            "progress": float(self.progress),
        }

    @classmethod
    def from_dict(cls, d: Mapping[str, Any]) -> "LaborAllocation":
        return cls(
            allocation_id=str(d.get("allocation_id")),
            sector=str(d.get("sector", "General")),
            assigned_workers=_as_tuple_of_str(d.get("assigned_workers")),
            required_workers=_as_int(d.get("required_workers"), 0),
            priority=clamp(_as_float(d.get("priority"), 0.5)),
            start_tick=_as_int(d.get("start_tick"), 0),
            progress=clamp(_as_float(d.get("progress"), 0.0)),
        )


@dataclass(frozen=True, slots=True)
class CommunalProject:
    project_id: str
    project_type: str
    village_id: str
    name: str
    assigned_workers: tuple[str, ...] = tuple()
    required_workers: int = 2
    required_ticks: int = 10
    progress: float = 0.0
    start_tick: int = 0
    completed_tick: int = 0
    active: bool = False
    material_cost: tuple[tuple[str, float], ...] = tuple()
    reward: tuple[tuple[str, float], ...] = tuple()

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": str(self.project_id),
            "project_type": str(self.project_type),
            "village_id": str(self.village_id),
            "name": str(self.name),
            "assigned_workers": list(self.assigned_workers),
            "required_workers": int(self.required_workers),
            "required_ticks": int(self.required_ticks),
            "progress": float(self.progress),
            "start_tick": int(self.start_tick),
            "completed_tick": int(self.completed_tick),
            "active": bool(self.active),
            "material_cost": [list(item) for item in self.material_cost],
            "reward": [list(item) for item in self.reward],
        }

    @classmethod
    def from_dict(cls, d: Mapping[str, Any]) -> "CommunalProject":
        mat = d.get("material_cost", ())
        rwd = d.get("reward", ())
        return cls(
            project_id=str(d.get("project_id")),
            project_type=str(d.get("project_type", "General")),
            village_id=str(d.get("village_id")),
            name=str(d.get("name", "Project")),
            assigned_workers=_as_tuple_of_str(d.get("assigned_workers")),
            required_workers=_as_int(d.get("required_workers"), 2),
            required_ticks=_as_int(d.get("required_ticks"), 10),
            progress=clamp(_as_float(d.get("progress"), 0.0)),
            start_tick=_as_int(d.get("start_tick"), 0),
            completed_tick=_as_int(d.get("completed_tick"), 0),
            active=_as_bool(d.get("active")),
            material_cost=tuple(tuple((str(item[0]), float(item[1]))) for item in mat) if hasattr(mat, "__iter__") and not isinstance(mat, (str, bytes)) else tuple(),
            reward=tuple(tuple((str(item[0]), float(item[1]))) for item in rwd) if hasattr(rwd, "__iter__") and not isinstance(rwd, (str, bytes)) else tuple(),
        )


@dataclass(frozen=True, slots=True)
class ActiveCelebration:
    celebration_id: str
    celebration_type: str
    village_id: str
    name: str
    start_tick: int
    duration_ticks: int = 5
    participants: tuple[str, ...] = tuple()
    organizer: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "celebration_id": str(self.celebration_id),
            "celebration_type": str(self.celebration_type),
            "village_id": str(self.village_id),
            "name": str(self.name),
            "start_tick": int(self.start_tick),
            "duration_ticks": int(self.duration_ticks),
            "participants": list(self.participants),
            "organizer": str(self.organizer),
        }

    @classmethod
    def from_dict(cls, d: Mapping[str, Any]) -> "ActiveCelebration":
        return cls(
            celebration_id=str(d.get("celebration_id")),
            celebration_type=str(d.get("celebration_type", "Festival")),
            village_id=str(d.get("village_id")),
            name=str(d.get("name", "Celebration")),
            start_tick=_as_int(d.get("start_tick"), 0),
            duration_ticks=_as_int(d.get("duration_ticks"), 5),
            participants=_as_tuple_of_str(d.get("participants")),
            organizer=str(d.get("organizer", "")),
        )


@dataclass(frozen=True, slots=True)
class ActiveEmergency:
    emergency_id: str
    emergency_type: str
    village_id: str
    severity: float
    declared_tick: int
    resolved_tick: int = 0
    resolved: bool = False
    affected: tuple[str, ...] = tuple()
    responders: tuple[str, ...] = tuple()

    def to_dict(self) -> dict[str, Any]:
        return {
            "emergency_id": str(self.emergency_id),
            "emergency_type": str(self.emergency_type),
            "village_id": str(self.village_id),
            "severity": float(self.severity),
            "declared_tick": int(self.declared_tick),
            "resolved_tick": int(self.resolved_tick),
            "resolved": bool(self.resolved),
            "affected": list(self.affected),
            "responders": list(self.responders),
        }

    @classmethod
    def from_dict(cls, d: Mapping[str, Any]) -> "ActiveEmergency":
        return cls(
            emergency_id=str(d.get("emergency_id")),
            emergency_type=str(d.get("emergency_type", "General")),
            village_id=str(d.get("village_id")),
            severity=clamp(_as_float(d.get("severity"), 0.3)),
            declared_tick=_as_int(d.get("declared_tick"), 0),
            resolved_tick=_as_int(d.get("resolved_tick"), 0),
            resolved=_as_bool(d.get("resolved")),
            affected=_as_tuple_of_str(d.get("affected")),
            responders=_as_tuple_of_str(d.get("responders")),
        )


@dataclass(frozen=True, slots=True)
class Leadership:
    village_id: str
    leader_entity_id: str = ""
    leader_role: str = ""
    deputy_entity_id: str = ""
    councillors: tuple[str, ...] = tuple()
    appointed_tick: int = 0
    leadership_effectiveness: float = 0.7
    last_meeting_tick: int = 0
    meeting_count: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(self, "leadership_effectiveness", clamp(float(self.leadership_effectiveness)))
        object.__setattr__(self, "appointed_tick", max(0, int(self.appointed_tick)))
        object.__setattr__(self, "last_meeting_tick", max(0, int(self.last_meeting_tick)))
        object.__setattr__(self, "meeting_count", max(0, int(self.meeting_count)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "village_id": str(self.village_id),
            "leader_entity_id": str(self.leader_entity_id),
            "leader_role": str(self.leader_role),
            "deputy_entity_id": str(self.deputy_entity_id),
            "councillors": list(self.councillors),
            "appointed_tick": int(self.appointed_tick),
            "leadership_effectiveness": float(self.leadership_effectiveness),
            "last_meeting_tick": int(self.last_meeting_tick),
            "meeting_count": int(self.meeting_count),
        }

    @classmethod
    def from_dict(cls, d: Mapping[str, Any]) -> "Leadership":
        return cls(
            village_id=str(d.get("village_id")),
            leader_entity_id=str(d.get("leader_entity_id", "")),
            leader_role=str(d.get("leader_role", "")),
            deputy_entity_id=str(d.get("deputy_entity_id", "")),
            councillors=_as_tuple_of_str(d.get("councillors")),
            appointed_tick=_as_int(d.get("appointed_tick"), 0),
            leadership_effectiveness=clamp(_as_float(d.get("leadership_effectiveness"), 0.7)),
            last_meeting_tick=_as_int(d.get("last_meeting_tick"), 0),
            meeting_count=_as_int(d.get("meeting_count"), 0),
        )


@dataclass(frozen=True, slots=True)
class VillageState:
    village_id: str
    village_name: str
    world_id: str
    population: int = 0
    workforce_size: int = 0
    food_reserve: float = 0.0
    wood_reserve: float = 0.0
    emergency_level: float = DEFAULT_EMERGENCY_LEVEL
    prosperity: float = DEFAULT_PROSPERITY
    stability: float = DEFAULT_STABILITY
    morale: float = DEFAULT_MORALE
    founded_tick: int = 0
    last_updated_tick: int = 0
    households: tuple[str, ...] = tuple()
    occupations: tuple[tuple[str, int], ...] = tuple()
    labor_allocations: tuple[str, ...] = tuple()
    active_projects: tuple[str, ...] = tuple()
    completed_projects_count: int = 0
    active_celebrations: tuple[str, ...] = tuple()
    active_emergencies: tuple[str, ...] = tuple()
    resolved_emergencies_count: int = 0
    births_count: int = 0
    deaths_count: int = 0
    marriages_count: int = 0
    cumulative_harvest: float = 0.0
    cumulative_production_value: float = 0.0
    cumulative_trade_volume: float = 0.0
    festival_days_count: int = 0
    leadership: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "prosperity", clamp(self.prosperity, SOCIETY_METRIC_MIN, SOCIETY_METRIC_MAX))
        object.__setattr__(self, "stability", clamp(self.stability, SOCIETY_METRIC_MIN, SOCIETY_METRIC_MAX))
        object.__setattr__(self, "morale", clamp(self.morale, SOCIETY_METRIC_MIN, SOCIETY_METRIC_MAX))
        object.__setattr__(self, "emergency_level", clamp(self.emergency_level, SOCIETY_METRIC_MIN, SOCIETY_METRIC_MAX))
        object.__setattr__(self, "population", max(0, int(self.population)))
        object.__setattr__(self, "workforce_size", max(0, int(self.workforce_size)))
        object.__setattr__(self, "food_reserve", max(0.0, float(self.food_reserve)))
        object.__setattr__(self, "wood_reserve", max(0.0, float(self.wood_reserve)))

    @classmethod
    def initial(
        cls,
        *,
        world_id: str,
        village_name: str = "Valley Village",
        founded_tick: int = 0,
    ) -> "VillageState":
        vid = make_village_id(str(world_id), str(village_name))
        return cls(
            village_id=vid,
            village_name=str(village_name),
            world_id=str(world_id),
            founded_tick=int(founded_tick),
            last_updated_tick=int(founded_tick),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "village_id": str(self.village_id),
            "village_name": str(self.village_name),
            "world_id": str(self.world_id),
            "population": int(self.population),
            "workforce_size": int(self.workforce_size),
            "food_reserve": float(self.food_reserve),
            "wood_reserve": float(self.wood_reserve),
            "emergency_level": float(self.emergency_level),
            "prosperity": float(self.prosperity),
            "stability": float(self.stability),
            "morale": float(self.morale),
            "founded_tick": int(self.founded_tick),
            "last_updated_tick": int(self.last_updated_tick),
            "households": list(self.households),
            "occupations": [list(item) for item in self.occupations],
            "labor_allocations": list(self.labor_allocations),
            "active_projects": list(self.active_projects),
            "completed_projects_count": int(self.completed_projects_count),
            "active_celebrations": list(self.active_celebrations),
            "active_emergencies": list(self.active_emergencies),
            "resolved_emergencies_count": int(self.resolved_emergencies_count),
            "births_count": int(self.births_count),
            "deaths_count": int(self.deaths_count),
            "marriages_count": int(self.marriages_count),
            "cumulative_harvest": float(self.cumulative_harvest),
            "cumulative_production_value": float(self.cumulative_production_value),
            "cumulative_trade_volume": float(self.cumulative_trade_volume),
            "festival_days_count": int(self.festival_days_count),
            "leadership": str(self.leadership),
        }

    @classmethod
    def from_dict(cls, d: Mapping[str, Any]) -> "VillageState":
        occ = d.get("occupations", ())
        occupations = tuple(
            tuple((str(item[0]), int(item[1])))
            for item in occ
            if hasattr(item, "__len__") and len(item) >= 2
        ) if hasattr(occ, "__iter__") and not isinstance(occ, (str, bytes)) else tuple()
        return cls(
            village_id=str(d.get("village_id")),
            village_name=str(d.get("village_name", "Village")),
            world_id=str(d.get("world_id")),
            population=_as_int(d.get("population"), 0),
            workforce_size=_as_int(d.get("workforce_size"), 0),
            food_reserve=_as_float(d.get("food_reserve"), 0.0),
            wood_reserve=_as_float(d.get("wood_reserve"), 0.0),
            emergency_level=_as_float(d.get("emergency_level"), DEFAULT_EMERGENCY_LEVEL),
            prosperity=_as_float(d.get("prosperity"), DEFAULT_PROSPERITY),
            stability=_as_float(d.get("stability"), DEFAULT_STABILITY),
            morale=_as_float(d.get("morale"), DEFAULT_MORALE),
            founded_tick=_as_int(d.get("founded_tick"), 0),
            last_updated_tick=_as_int(d.get("last_updated_tick"), 0),
            households=_as_tuple_of_str(d.get("households")),
            occupations=occupations,
            labor_allocations=_as_tuple_of_str(d.get("labor_allocations")),
            active_projects=_as_tuple_of_str(d.get("active_projects")),
            completed_projects_count=_as_int(d.get("completed_projects_count"), 0),
            active_celebrations=_as_tuple_of_str(d.get("active_celebrations")),
            active_emergencies=_as_tuple_of_str(d.get("active_emergencies")),
            resolved_emergencies_count=_as_int(d.get("resolved_emergencies_count"), 0),
            births_count=_as_int(d.get("births_count"), 0),
            deaths_count=_as_int(d.get("deaths_count"), 0),
            marriages_count=_as_int(d.get("marriages_count"), 0),
            cumulative_harvest=_as_float(d.get("cumulative_harvest"), 0.0),
            cumulative_production_value=_as_float(d.get("cumulative_production_value"), 0.0),
            cumulative_trade_volume=_as_float(d.get("cumulative_trade_volume"), 0.0),
            festival_days_count=_as_int(d.get("festival_days_count"), 0),
            leadership=str(d.get("leadership", "")),
        )


def _count_tuple_entry(entries: tuple[str, ...], target: str) -> int:
    return sum(1 for e in entries if e == target)
