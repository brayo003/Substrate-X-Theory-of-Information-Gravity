from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


DEFAULT_HEALTH: float = 0.85
DEFAULT_FATIGUE: float = 0.1
DEFAULT_NUTRITION: float = 0.8
DEFAULT_HYDRATION: float = 0.85
DEFAULT_IMMUNITY: float = 0.75
DEFAULT_STRESS: float = 0.1
DEFAULT_SICKNESS: float = 0.0
DEFAULT_INJURY: float = 0.0
DEFAULT_INFECTION: float = 0.0
DEFAULT_BODY_TEMP: float = 36.7
DEFAULT_MOBILITY_PENALTY: float = 0.0
HEALTH_MIN: float = 0.0
HEALTH_MAX: float = 1.0
DEATH_THRESHOLD: float = 0.001
RECOVERY_RATE_BASE: float = 0.01
IMMUNITY_SICKNESS_DECAY: float = 0.01
INJURY_RECOVERY_RATE: float = 0.005


HEALTH_ID_PREFIX = "health_state"

ILLNESS_TYPES = (
    "Cold",
    "Flu",
    "FoodPoisoning",
    "Exhaustion",
    "Dehydration",
    "Malnutrition",
    "Hypothermia",
    "HeatStress",
)

INJURY_TYPES = (
    "MinorCut",
    "Sprain",
    "Fracture",
    "WorkStrain",
    "StormAccident",
    "FallingTree",
    "ConstructionFall",
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


def make_health_state_id(entity_id: str) -> str:
    eid = str(entity_id)
    key = f"{HEALTH_ID_PREFIX}:{eid}"
    return f"{HEALTH_ID_PREFIX}_{deterministic_hash(key)}"


def _norm_bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return bool(int(v) != 0)
    s = str(v).strip().lower()
    return s in {"1", "true", "yes", "on", "alive"}


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


@dataclass(frozen=True)
class HealthState:
    health_id: str
    entity_id: str
    overall_health: float = DEFAULT_HEALTH
    fatigue: float = DEFAULT_FATIGUE
    nutrition: float = DEFAULT_NUTRITION
    hydration: float = DEFAULT_HYDRATION
    immunity: float = DEFAULT_IMMUNITY
    stress: float = DEFAULT_STRESS
    sickness: float = DEFAULT_SICKNESS
    injury: float = DEFAULT_INJURY
    infection: float = DEFAULT_INFECTION
    body_temperature_c: float = DEFAULT_BODY_TEMP
    mobility_penalty: float = DEFAULT_MOBILITY_PENALTY
    alive: bool = True
    recovering: bool = False
    last_treatment_tick: int = 0
    active_illnesses: tuple[str, ...] = tuple()
    active_injuries: tuple[str, ...] = tuple()
    last_updated_tick: int = 0
    birth_tick: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(self, "overall_health", clamp(self.overall_health, HEALTH_MIN, HEALTH_MAX))
        object.__setattr__(self, "fatigue", clamp(self.fatigue, 0.0, HEALTH_MAX))
        object.__setattr__(self, "nutrition", clamp(self.nutrition, 0.0, HEALTH_MAX))
        object.__setattr__(self, "hydration", clamp(self.hydration, 0.0, HEALTH_MAX))
        object.__setattr__(self, "immunity", clamp(self.immunity, 0.0, HEALTH_MAX))
        object.__setattr__(self, "stress", clamp(self.stress, 0.0, HEALTH_MAX))
        object.__setattr__(self, "sickness", clamp(self.sickness, 0.0, HEALTH_MAX))
        object.__setattr__(self, "injury", clamp(self.injury, 0.0, HEALTH_MAX))
        object.__setattr__(self, "infection", clamp(self.infection, 0.0, HEALTH_MAX))
        object.__setattr__(self, "body_temperature_c", clamp(self.body_temperature_c, 30.0, 44.0))
        object.__setattr__(self, "mobility_penalty", clamp(self.mobility_penalty, 0.0, 1.0))
        object.__setattr__(self, "active_illnesses", _as_tuple_of_str(self.active_illnesses))
        object.__setattr__(self, "active_injuries", _as_tuple_of_str(self.active_injuries))
        if self.overall_health <= DEATH_THRESHOLD and self.alive:
            object.__setattr__(self, "alive", False)
        if not self.alive:
            object.__setattr__(self, "recovering", False)

    @classmethod
    def initial(cls, entity_id: str, *, birth_tick: int = 0, seed: str | None = None) -> "HealthState":
        eid = str(entity_id)
        hid = make_health_state_id(eid)
        return cls(
            health_id=hid,
            entity_id=eid,
            last_updated_tick=int(birth_tick),
            birth_tick=int(birth_tick),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "health_id": str(self.health_id),
            "entity_id": str(self.entity_id),
            "overall_health": float(self.overall_health),
            "fatigue": float(self.fatigue),
            "nutrition": float(self.nutrition),
            "hydration": float(self.hydration),
            "immunity": float(self.immunity),
            "stress": float(self.stress),
            "sickness": float(self.sickness),
            "injury": float(self.injury),
            "infection": float(self.infection),
            "body_temperature_c": float(self.body_temperature_c),
            "mobility_penalty": float(self.mobility_penalty),
            "alive": bool(self.alive),
            "recovering": bool(self.recovering),
            "last_treatment_tick": int(self.last_treatment_tick),
            "active_illnesses": list(self.active_illnesses),
            "active_injuries": list(self.active_injuries),
            "last_updated_tick": int(self.last_updated_tick),
            "birth_tick": int(self.birth_tick),
        }

    @classmethod
    def from_dict(cls, d: Mapping[str, Any]) -> "HealthState":
        if not d:
            raise ValueError("HealthState.from_dict requires non-empty dict")
        return cls(
            health_id=str(d.get("health_id")),
            entity_id=str(d.get("entity_id")),
            overall_health=_as_float(d.get("overall_health"), DEFAULT_HEALTH),
            fatigue=_as_float(d.get("fatigue"), DEFAULT_FATIGUE),
            nutrition=_as_float(d.get("nutrition"), DEFAULT_NUTRITION),
            hydration=_as_float(d.get("hydration"), DEFAULT_HYDRATION),
            immunity=_as_float(d.get("immunity"), DEFAULT_IMMUNITY),
            stress=_as_float(d.get("stress"), DEFAULT_STRESS),
            sickness=_as_float(d.get("sickness"), DEFAULT_SICKNESS),
            injury=_as_float(d.get("injury"), DEFAULT_INJURY),
            infection=_as_float(d.get("infection"), DEFAULT_INFECTION),
            body_temperature_c=_as_float(d.get("body_temperature_c"), DEFAULT_BODY_TEMP),
            mobility_penalty=_as_float(d.get("mobility_penalty"), DEFAULT_MOBILITY_PENALTY),
            alive=_norm_bool(d.get("alive", True)),
            recovering=_norm_bool(d.get("recovering", False)),
            last_treatment_tick=_as_int(d.get("last_treatment_tick"), 0),
            active_illnesses=tuple(d.get("active_illnesses") or ()),
            active_injuries=tuple(d.get("active_injuries") or ()),
            last_updated_tick=_as_int(d.get("last_updated_tick"), 0),
            birth_tick=_as_int(d.get("birth_tick"), 0),
        )


def add_illness(existing: tuple[str, ...], illness: str) -> tuple[str, ...]:
    if illness in existing:
        return tuple(existing)
    return tuple(list(existing) + [str(illness)])


def remove_illness(existing: tuple[str, ...], illness: str) -> tuple[str, ...]:
    return tuple(x for x in existing if x != illness)


def add_injury(existing: tuple[str, ...], injury: str) -> tuple[str, ...]:
    if injury in existing:
        return tuple(existing)
    return tuple(list(existing) + [str(injury)])


def remove_injury(existing: tuple[str, ...], injury: str) -> tuple[str, ...]:
    return tuple(x for x in existing if x != injury)


def _normalize_identifier(value: Any, allowed: tuple[str, ...], default: str) -> str:
    if value is None:
        return str(default)
    s = str(value).strip()
    if not s:
        return str(default)
    if s in allowed:
        return s
    for candidate in allowed:
        if str(candidate).lower() == s.lower():
            return candidate
    return str(default)
