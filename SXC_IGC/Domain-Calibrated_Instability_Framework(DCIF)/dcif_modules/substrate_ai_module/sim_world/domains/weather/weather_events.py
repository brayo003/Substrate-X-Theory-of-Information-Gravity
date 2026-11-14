from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class SeasonChanged:
    tick_number: int
    old_season: str
    new_season: str
    day_of_season: int = 1
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": "SeasonChanged",
            "tick_number": int(self.tick_number),
            "old_season": str(self.old_season),
            "new_season": str(self.new_season),
            "day_of_season": int(self.day_of_season),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class WeatherChanged:
    tick_number: int
    old_weather: str
    new_weather: str
    temperature_c: float = 15.0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": "WeatherChanged",
            "tick_number": int(self.tick_number),
            "old_weather": str(self.old_weather),
            "new_weather": str(self.new_weather),
            "temperature_c": float(self.temperature_c),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class RainStarted:
    tick_number: int
    rainfall: float = 0.4
    weather: str = "Light Rain"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": "RainStarted",
            "tick_number": int(self.tick_number),
            "rainfall": float(self.rainfall),
            "weather": str(self.weather),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class RainStopped:
    tick_number: int
    total_rainfall: float = 0.0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": "RainStopped",
            "tick_number": int(self.tick_number),
            "total_rainfall": float(self.total_rainfall),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class SnowStarted:
    tick_number: int
    snowfall: float = 0.6
    weather: str = "Snow"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": "SnowStarted",
            "tick_number": int(self.tick_number),
            "snowfall": float(self.snowfall),
            "weather": str(self.weather),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class SnowStopped:
    tick_number: int
    total_snowfall: float = 0.0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": "SnowStopped",
            "tick_number": int(self.tick_number),
            "total_snowfall": float(self.total_snowfall),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class StormStarted:
    tick_number: int
    storm_strength: float = 0.8
    wind: float = 0.95
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": "StormStarted",
            "tick_number": int(self.tick_number),
            "storm_strength": float(self.storm_strength),
            "wind": float(self.wind),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class StormEnded:
    tick_number: int
    peak_storm_strength: float = 0.0
    damage_level: float = 0.0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": "StormEnded",
            "tick_number": int(self.tick_number),
            "peak_storm_strength": float(self.peak_storm_strength),
            "damage_level": float(self.damage_level),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class RiverFlooded:
    tick_number: int
    river_level: float = 0.95
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": "RiverFlooded",
            "tick_number": int(self.tick_number),
            "river_level": float(self.river_level),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class RiverReceded:
    tick_number: int
    river_level: float = 0.5
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": "RiverReceded",
            "tick_number": int(self.tick_number),
            "river_level": float(self.river_level),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class GroundFrozen:
    tick_number: int
    temperature_c: float = -3.0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": "GroundFrozen",
            "tick_number": int(self.tick_number),
            "temperature_c": float(self.temperature_c),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class GroundThawed:
    tick_number: int
    temperature_c: float = 2.0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": "GroundThawed",
            "tick_number": int(self.tick_number),
            "temperature_c": float(self.temperature_c),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class HeatWaveStarted:
    tick_number: int
    temperature_c: float = 35.0
    duration_estimate_ticks: int = 24
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": "HeatWaveStarted",
            "tick_number": int(self.tick_number),
            "temperature_c": float(self.temperature_c),
            "duration_estimate_ticks": int(self.duration_estimate_ticks),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class ColdWaveStarted:
    tick_number: int
    temperature_c: float = -12.0
    duration_estimate_ticks: int = 24
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": "ColdWaveStarted",
            "tick_number": int(self.tick_number),
            "temperature_c": float(self.temperature_c),
            "duration_estimate_ticks": int(self.duration_estimate_ticks),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class FogAppeared:
    tick_number: int
    visibility: float = 0.3
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": "FogAppeared",
            "tick_number": int(self.tick_number),
            "visibility": float(self.visibility),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class FogCleared:
    tick_number: int
    visibility: float = 1.0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": "FogCleared",
            "tick_number": int(self.tick_number),
            "visibility": float(self.visibility),
            "metadata": dict(self.metadata),
        }
