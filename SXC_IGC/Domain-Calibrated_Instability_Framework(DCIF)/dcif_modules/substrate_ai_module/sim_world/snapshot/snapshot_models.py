from dataclasses import dataclass, asdict
from typing import Any, List, Dict


@dataclass
class VillagerModel:
    id: str
    name: str
    x: int
    y: int
    texture: str  # Required: sprite atlas key
    scale: float = 1.0  # Required: sprite scale
    facing: str | None = None
    animation: str | None = None
    activity: str | None = None
    emotion: str | None = None
    state: str | None = None
    # v1.1.0 observability: real per-villager needs/inventory (never faked).
    needs: Dict[str, float] = None
    inventory: Dict[str, float] = None

    def __post_init__(self) -> None:
        if self.needs is None:
            self.needs = {}
        if self.inventory is None:
            self.inventory = {}


@dataclass
class BuildingModel:
    id: str
    type: str
    x: int
    y: int
    texture: str  # Required: sprite atlas key
    scale: float = 1.0  # Required: sprite scale


@dataclass
class EnvironmentModel:
    id: str
    type: str
    x: int
    y: int
    texture: str  # Required: sprite atlas key
    scale: float = 1.0  # Required: sprite scale


@dataclass
class WorldSnapshot:
    tick: int
    time: Dict[str, Any]
    weather: Dict[str, Any]
    villagers: List[VillagerModel]
    buildings: List[BuildingModel]
    environment: List[EnvironmentModel]  # New: trees, rocks, roads, etc.

    def to_dict(self) -> dict:
        return {
            "tick": int(self.tick),
            "time": dict(self.time or {}),
            "weather": dict(self.weather or {}),
            "villagers": [asdict(v) for v in self.villagers],
            "buildings": [asdict(b) for b in self.buildings],
            "environment": [asdict(e) for e in self.environment],
        }
