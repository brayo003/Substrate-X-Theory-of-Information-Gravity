from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    val = hash(s) % (2**32)
    return abs(val)


FACILITY_TYPES: tuple[str, ...] = (
    "Farm",
    "Barn",
    "Blacksmith",
    "Workshop",
    "Kitchen",
    "Storage",
)


PRODUCTION_TOOLS: tuple[str, ...] = (
    "Hammer",
    "Axe",
    "Hoe",
    "Oven",
    "Forge",
    "Mill",
)


OCCUPATIONS: tuple[str, ...] = (
    "Farmer",
    "Miller",
    "Blacksmith",
    "Cook",
    "Carpenter",
)


JOB_STATUSES: tuple[str, ...] = (
    "Reserved",
    "Active",
    "Progressing",
    "Completed",
    "Cancelled",
    "Deposited",
)


RECIPE_REGISTRY: tuple[Mapping[str, Any], ...] = (
    {
        "recipe_id": "recipe:grow:wheat",
        "name": "Grow Wheat",
        "facility": "Farm",
        "occupation": "Farmer",
        "inputs": {"seeds": 2.0},
        "tools": ("Hoe",),
        "duration_ticks": 5,
        "outputs": {"food": 10.0},
    },
    {
        "recipe_id": "recipe:chop:firewood",
        "name": "Chop Firewood",
        "facility": "Workshop",
        "occupation": "Carpenter",
        "inputs": {"wood": 2.0},
        "tools": ("Axe",),
        "duration_ticks": 2,
        "outputs": {"fuel": 4.0},
    },
    {
        "recipe_id": "recipe:mill:planks",
        "name": "Mill Planks",
        "facility": "Workshop",
        "occupation": "Carpenter",
        "inputs": {"wood": 1.0},
        "tools": ("Axe",),
        "duration_ticks": 2,
        "outputs": {"wood": 2.0},
    },
    {
        "recipe_id": "recipe:forge:tools_wood",
        "name": "Forge Wooden Tools",
        "facility": "Workshop",
        "occupation": "Carpenter",
        "inputs": {"wood": 3.0},
        "tools": ("Axe", "Hammer"),
        "duration_ticks": 4,
        "outputs": {"tools": 1.0},
    },
    {
        "recipe_id": "recipe:smelt:iron_ingots",
        "name": "Smelt Iron Ingots",
        "facility": "Blacksmith",
        "occupation": "Blacksmith",
        "inputs": {"iron": 2.0, "fuel": 1.0},
        "tools": ("Forge",),
        "duration_ticks": 4,
        "outputs": {"iron": 3.0},
    },
    {
        "recipe_id": "recipe:forge:iron_tools",
        "name": "Forge Iron Tools",
        "facility": "Blacksmith",
        "occupation": "Blacksmith",
        "inputs": {"iron": 3.0, "fuel": 1.0, "wood": 1.0},
        "tools": ("Forge", "Hammer"),
        "duration_ticks": 6,
        "outputs": {"tools": 3.0},
    },
    {
        "recipe_id": "recipe:mill:flour",
        "name": "Mill Grain into Flour",
        "facility": "Barn",
        "occupation": "Miller",
        "inputs": {"food": 2.0},
        "tools": ("Mill",),
        "duration_ticks": 2,
        "outputs": {"food": 4.0},
    },
    {
        "recipe_id": "recipe:bake:bread",
        "name": "Bake Bread",
        "facility": "Kitchen",
        "occupation": "Cook",
        "inputs": {"food": 2.0, "fuel": 1.0, "water": 1.0},
        "tools": ("Oven",),
        "duration_ticks": 3,
        "outputs": {"food": 6.0},
    },
    {
        "recipe_id": "recipe:cook:meal",
        "name": "Cook Meal",
        "facility": "Kitchen",
        "occupation": "Cook",
        "inputs": {"food": 3.0, "fuel": 1.0},
        "tools": ("Oven",),
        "duration_ticks": 3,
        "outputs": {"food": 8.0},
    },
)


FACILITY_OCCUPATION_MATRIX: dict[str, tuple[str, ...]] = {
    "Farm": ("Farmer",),
    "Barn": ("Miller", "Farmer"),
    "Blacksmith": ("Blacksmith",),
    "Workshop": ("Carpenter", "Blacksmith"),
    "Kitchen": ("Cook",),
    "Storage": ("Farmer", "Miller", "Blacksmith", "Cook", "Carpenter"),
}


def _normalize_identifier(
    value: str,
    allowed: Sequence[str],
    default: str,
) -> str:
    if value in allowed:
        return str(value)
    lookup = {str(a).lower(): str(a) for a in allowed}
    return lookup.get(str(value).lower(), str(default))


def _to_tuple_of_str(seq: Any) -> tuple[str, ...]:
    if not seq:
        return ()
    return tuple(str(v) for v in seq)


def _to_frozen_resource_map(data: Any) -> tuple[tuple[str, float], ...]:
    result: list[tuple[str, float]] = []
    if isinstance(data, Mapping):
        for k, v in data.items():
            result.append((str(k), max(0.0, float(v))))
    elif isinstance(data, Sequence):
        for row in data:
            if isinstance(row, Mapping) and "identifier" in row:
                result.append((str(row["identifier"]), max(0.0, float(row.get("quantity", 0.0)))))
            elif isinstance(row, Sequence) and len(row) >= 2:
                result.append((str(row[0]), max(0.0, float(row[1]))))
    return tuple(sorted(result, key=lambda r: r[0]))


def _resource_map_to_dict(items: tuple[tuple[str, float], ...]) -> dict[str, float]:
    return {k: float(v) for k, v in items}


def make_facility_id(facility_type: str, location: str) -> str:
    ft = _normalize_identifier(facility_type, FACILITY_TYPES, "Storage")
    seed = f"facility:{ft}:{location}"
    return f"fac:{ft}:{location}:{deterministic_hash(seed)}"


def make_recipe_id(name: str, facility: str) -> str:
    return f"recipe:{_normalize_identifier(facility, FACILITY_TYPES, 'Workshop')}:{name}"


def make_job_id(facility_id: str, recipe_id: str, worker_id: str, tick: int) -> str:
    seed = f"job:{facility_id}:{recipe_id}:{worker_id}:{tick}"
    return f"job:{tick}:{worker_id}:{deterministic_hash(seed)}"


def make_tool_state_id(tool: str, owner: str) -> str:
    return f"tool:{tool}:{owner}"


@dataclass(slots=True)
class ToolState:
    tool_id: str
    tool_type: str
    owner_id: str
    durability: float = 1.0
    uses: int = 0

    def __post_init__(self) -> None:
        self.tool_id = str(self.tool_id)
        self.tool_type = _normalize_identifier(self.tool_type, PRODUCTION_TOOLS, "Hammer")
        self.owner_id = str(self.owner_id)
        self.durability = max(0.0, min(1.0, float(self.durability)))
        self.uses = max(0, int(self.uses))

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_id": self.tool_id,
            "tool_type": self.tool_type,
            "owner_id": self.owner_id,
            "durability": self.durability,
            "uses": self.uses,
        }

    @staticmethod
    def from_dict(data: Mapping[str, Any]) -> ToolState:
        return ToolState(
            tool_id=str(data.get("tool_id", "tool_1")),
            tool_type=str(data.get("tool_type", "Hammer")),
            owner_id=str(data.get("owner_id", "")),
            durability=float(data.get("durability", 1.0)),
            uses=int(data.get("uses", 0)),
        )


@dataclass(slots=True)
class ProductionRecipe:
    recipe_id: str
    name: str
    facility: str
    occupation: str
    inputs: tuple[tuple[str, float], ...] = ()
    tools_required: tuple[str, ...] = ()
    duration_ticks: int = 1
    outputs: tuple[tuple[str, float], ...] = ()

    def __post_init__(self) -> None:
        self.recipe_id = str(self.recipe_id)
        self.name = str(self.name)
        self.facility = _normalize_identifier(self.facility, FACILITY_TYPES, "Workshop")
        if self.occupation not in OCCUPATIONS:
            lookup = {o.lower(): o for o in OCCUPATIONS}
            self.occupation = lookup.get(str(self.occupation).lower(), "Farmer")
        self.inputs = _to_frozen_resource_map(self.inputs)
        self.tools_required = tuple(
            _normalize_identifier(t, PRODUCTION_TOOLS, "Hammer")
            for t in self.tools_required
        )
        self.duration_ticks = max(1, int(self.duration_ticks))
        self.outputs = _to_frozen_resource_map(self.outputs)

    @property
    def inputs_dict(self) -> dict[str, float]:
        return _resource_map_to_dict(self.inputs)

    @property
    def outputs_dict(self) -> dict[str, float]:
        return _resource_map_to_dict(self.outputs)

    def to_dict(self) -> dict[str, Any]:
        return {
            "recipe_id": self.recipe_id,
            "name": self.name,
            "facility": self.facility,
            "occupation": self.occupation,
            "inputs": [{"identifier": k, "quantity": v} for k, v in self.inputs],
            "tools_required": list(self.tools_required),
            "duration_ticks": self.duration_ticks,
            "outputs": [{"identifier": k, "quantity": v} for k, v in self.outputs],
        }

    @staticmethod
    def from_dict(data: Mapping[str, Any]) -> ProductionRecipe:
        return ProductionRecipe(
            recipe_id=str(data.get("recipe_id", "recipe:default")),
            name=str(data.get("name", "Recipe")),
            facility=str(data.get("facility", "Workshop")),
            occupation=str(data.get("occupation", "Farmer")),
            inputs=tuple(data.get("inputs", ())),
            tools_required=_to_tuple_of_str(data.get("tools_required", ())),
            duration_ticks=int(data.get("duration_ticks", 1)),
            outputs=tuple(data.get("outputs", ())),
        )


@dataclass(slots=True)
class ProductionFacility:
    facility_id: str
    facility_type: str
    location: str
    workers: tuple[str, ...] = ()
    supported_recipes: tuple[str, ...] = ()
    active_jobs: tuple[str, ...] = ()
    capacity: int = 1

    def __post_init__(self) -> None:
        self.facility_id = str(self.facility_id)
        self.facility_type = _normalize_identifier(self.facility_type, FACILITY_TYPES, "Storage")
        self.location = str(self.location)
        self.workers = _to_tuple_of_str(self.workers)
        self.supported_recipes = _to_tuple_of_str(self.supported_recipes)
        self.active_jobs = _to_tuple_of_str(self.active_jobs)
        self.capacity = max(1, int(self.capacity))

    def to_dict(self) -> dict[str, Any]:
        return {
            "facility_id": self.facility_id,
            "facility_type": self.facility_type,
            "location": self.location,
            "workers": list(self.workers),
            "supported_recipes": list(self.supported_recipes),
            "active_jobs": list(self.active_jobs),
            "capacity": self.capacity,
        }

    @staticmethod
    def from_dict(data: Mapping[str, Any]) -> ProductionFacility:
        return ProductionFacility(
            facility_id=str(data.get("facility_id", "fac:1")),
            facility_type=str(data.get("facility_type", "Storage")),
            location=str(data.get("location", "")),
            workers=_to_tuple_of_str(data.get("workers", ())),
            supported_recipes=_to_tuple_of_str(data.get("supported_recipes", ())),
            active_jobs=_to_tuple_of_str(data.get("active_jobs", ())),
            capacity=int(data.get("capacity", 1)),
        )


@dataclass(slots=True)
class ProductionJob:
    job_id: str
    worker_id: str
    facility_id: str
    recipe_id: str
    inputs_reserved: tuple[tuple[str, float], ...] = ()
    progress: float = 0.0
    start_tick: int = 0
    completion_tick: int = 0
    duration: int = 1
    status: str = "Reserved"
    outputs_produced: tuple[tuple[str, float], ...] = ()
    tools_used: tuple[str, ...] = ()
    cancel_reason: str = ""

    def __post_init__(self) -> None:
        self.job_id = str(self.job_id)
        self.worker_id = str(self.worker_id)
        self.facility_id = str(self.facility_id)
        self.recipe_id = str(self.recipe_id)
        self.inputs_reserved = _to_frozen_resource_map(self.inputs_reserved)
        self.progress = max(0.0, min(1.0, float(self.progress)))
        self.start_tick = max(0, int(self.start_tick))
        self.completion_tick = max(0, int(self.completion_tick))
        self.duration = max(1, int(self.duration))
        if self.status not in JOB_STATUSES:
            self.status = "Reserved"
        self.outputs_produced = _to_frozen_resource_map(self.outputs_produced)
        self.tools_used = tuple(
            _normalize_identifier(t, PRODUCTION_TOOLS, "Hammer")
            for t in self.tools_used
        )
        self.cancel_reason = str(self.cancel_reason)

    @property
    def inputs_dict(self) -> dict[str, float]:
        return _resource_map_to_dict(self.inputs_reserved)

    @property
    def outputs_dict(self) -> dict[str, float]:
        return _resource_map_to_dict(self.outputs_produced)

    @property
    def is_active(self) -> bool:
        return self.status in ("Reserved", "Active", "Progressing")

    @property
    def is_completed(self) -> bool:
        return self.status in ("Completed", "Deposited")

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "worker_id": self.worker_id,
            "facility_id": self.facility_id,
            "recipe_id": self.recipe_id,
            "inputs_reserved": [{"identifier": k, "quantity": v} for k, v in self.inputs_reserved],
            "progress": self.progress,
            "start_tick": self.start_tick,
            "completion_tick": self.completion_tick,
            "duration": self.duration,
            "status": self.status,
            "outputs_produced": [{"identifier": k, "quantity": v} for k, v in self.outputs_produced],
            "tools_used": list(self.tools_used),
            "cancel_reason": self.cancel_reason,
        }

    @staticmethod
    def from_dict(data: Mapping[str, Any]) -> ProductionJob:
        return ProductionJob(
            job_id=str(data.get("job_id", "job:1")),
            worker_id=str(data.get("worker_id", "")),
            facility_id=str(data.get("facility_id", "")),
            recipe_id=str(data.get("recipe_id", "")),
            inputs_reserved=tuple(data.get("inputs_reserved", ())),
            progress=float(data.get("progress", 0.0)),
            start_tick=int(data.get("start_tick", 0)),
            completion_tick=int(data.get("completion_tick", 0)),
            duration=int(data.get("duration", 1)),
            status=str(data.get("status", "Reserved")),
            outputs_produced=tuple(data.get("outputs_produced", ())),
            tools_used=_to_tuple_of_str(data.get("tools_used", ())),
            cancel_reason=str(data.get("cancel_reason", "")),
        )


@dataclass(slots=True)
class ProductionState:
    phase: str = "Idle"
    active_job_count: int = 0
    completed_count: int = 0
    cancelled_count: int = 0
    reserved_count: int = 0
    deposited_count: int = 0

    def __post_init__(self) -> None:
        self.phase = str(self.phase)
        self.active_job_count = max(0, int(self.active_job_count))
        self.completed_count = max(0, int(self.completed_count))
        self.cancelled_count = max(0, int(self.cancelled_count))
        self.reserved_count = max(0, int(self.reserved_count))
        self.deposited_count = max(0, int(self.deposited_count))

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase": self.phase,
            "active_job_count": self.active_job_count,
            "completed_count": self.completed_count,
            "cancelled_count": self.cancelled_count,
            "reserved_count": self.reserved_count,
            "deposited_count": self.deposited_count,
        }

    @staticmethod
    def from_dict(data: Mapping[str, Any]) -> ProductionState:
        return ProductionState(
            phase=str(data.get("phase", "Idle")),
            active_job_count=int(data.get("active_job_count", 0)),
            completed_count=int(data.get("completed_count", 0)),
            cancelled_count=int(data.get("cancelled_count", 0)),
            reserved_count=int(data.get("reserved_count", 0)),
            deposited_count=int(data.get("deposited_count", 0)),
        )


def build_default_recipes() -> dict[str, ProductionRecipe]:
    result: dict[str, ProductionRecipe] = {}
    for entry in RECIPE_REGISTRY:
        rec = ProductionRecipe(
            recipe_id=str(entry["recipe_id"]),
            name=str(entry["name"]),
            facility=str(entry["facility"]),
            occupation=str(entry.get("occupation", "Farmer")),
            inputs=dict(entry.get("inputs", {})),
            tools_required=tuple(entry.get("tools", ())),
            duration_ticks=int(entry.get("duration_ticks", 1)),
            outputs=dict(entry.get("outputs", {})),
        )
        result[rec.recipe_id] = rec
    return result


def build_default_facilities(
    locations: Mapping[str, str] | None = None,
) -> dict[str, ProductionFacility]:
    if locations is None:
        locations = {
            "Farm": "north_fields",
            "Barn": "village_center",
            "Blacksmith": "east_street",
            "Workshop": "west_street",
            "Kitchen": "tavern_hall",
            "Storage": "village_center",
        }
    facilities: dict[str, ProductionFacility] = {}
    recipes = build_default_recipes()
    for ftype, loc in locations.items():
        fac = ProductionFacility(
            facility_id=make_facility_id(ftype, loc),
            facility_type=ftype,
            location=loc,
            workers=(),
            supported_recipes=tuple(
                sorted(rid for rid, r in recipes.items() if r.facility == ftype)
            ),
            active_jobs=(),
            capacity=3 if ftype in ("Workshop", "Kitchen", "Barn") else 1,
        )
        facilities[fac.facility_id] = fac
    return facilities
