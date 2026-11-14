from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


SEASONS: tuple[str, ...] = ("Spring", "Summer", "Autumn", "Winter")

WEATHER_TYPES: tuple[str, ...] = (
    "Clear",
    "Cloudy",
    "Light Rain",
    "Heavy Rain",
    "Storm",
    "Fog",
    "Snow",
    "Blizzard",
    "Heat Wave",
    "Cold Wave",
)

DEFAULT_SEASON_LENGTH_DAYS: int = 30
TICKS_PER_DAY: int = 24


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, float(value)))


SEASON_BASE_TEMP: Mapping[str, float] = {
    "Spring": 15.0,
    "Summer": 28.0,
    "Autumn": 12.0,
    "Winter": -2.0,
}

SEASON_TEMP_VARIATION: Mapping[str, float] = {
    "Spring": 8.0,
    "Summer": 7.0,
    "Autumn": 9.0,
    "Winter": 10.0,
}

SEASON_BASE_HUMIDITY: Mapping[str, float] = {
    "Spring": 0.65,
    "Summer": 0.45,
    "Autumn": 0.6,
    "Winter": 0.5,
}

SEASON_BASE_SUNLIGHT: Mapping[str, float] = {
    "Spring": 0.75,
    "Summer": 0.95,
    "Autumn": 0.65,
    "Winter": 0.35,
}

WEATHER_MODIFIERS: Mapping[str, Mapping[str, float]] = {
    "Clear": {"temp": +1.0, "humidity": -0.05, "cloud": 0.05, "wind": 0.05, "sunlight": +0.15},
    "Cloudy": {"temp": -1.0, "humidity": +0.05, "cloud": 0.6, "wind": 0.1, "sunlight": -0.2},
    "Light Rain": {"temp": -2.0, "humidity": +0.15, "cloud": 0.85, "wind": 0.2, "sunlight": -0.5, "rain": 0.4},
    "Heavy Rain": {"temp": -4.0, "humidity": +0.25, "cloud": 0.98, "wind": 0.4, "sunlight": -0.8, "rain": 1.0},
    "Storm": {"temp": -5.0, "humidity": +0.3, "cloud": 1.0, "wind": 0.95, "sunlight": -0.95, "rain": 1.3},
    "Fog": {"temp": -0.5, "humidity": +0.3, "cloud": 0.75, "wind": 0.02, "sunlight": -0.4},
    "Snow": {"temp": -3.0, "humidity": +0.1, "cloud": 0.9, "wind": 0.15, "sunlight": -0.5, "snow": 0.6},
    "Blizzard": {"temp": -8.0, "humidity": +0.2, "cloud": 1.0, "wind": 0.9, "sunlight": -0.9, "snow": 1.4},
    "Heat Wave": {"temp": +9.0, "humidity": -0.25, "cloud": 0.1, "wind": 0.08, "sunlight": +0.2},
    "Cold Wave": {"temp": -10.0, "humidity": +0.1, "cloud": 0.3, "wind": 0.3, "sunlight": -0.1},
}


def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    
    val = hash(s) % (2**32)
    return abs(val)


def hour_of_tick(tick_number: int) -> int:
    return int(tick_number) % TICKS_PER_DAY


def day_of_tick(tick_number: int) -> int:
    return int(tick_number) // TICKS_PER_DAY


def season_for_day(
    day_number: int,
    season_length_days: int = DEFAULT_SEASON_LENGTH_DAYS,
) -> str:
    total = len(SEASONS)
    length = max(1, int(season_length_days))
    index = (int(day_number) // length) % total
    return SEASONS[index]


def season_day(
    day_number: int,
    season_length_days: int = DEFAULT_SEASON_LENGTH_DAYS,
) -> int:
    length = max(1, int(season_length_days))
    return (int(day_number) % length) + 1


def day_length_hours(season: str) -> int:
    if season == "Summer":
        return 16
    if season == "Winter":
        return 8
    if season == "Spring":
        return 13
    return 11


@dataclass(frozen=True, slots=True)
class WeatherState:
    tick_number: int = 0
    day_number: int = 0
    season: str = "Spring"
    day_of_season: int = 1
    weather: str = "Clear"
    previous_weather: str = "Clear"
    temperature_c: float = 15.0
    humidity: float = 0.5
    wind: float = 0.1
    cloud_cover: float = 0.1
    rainfall: float = 0.0
    snowfall: float = 0.0
    ground_moisture: float = 0.5
    river_level: float = 0.5
    sunlight: float = 0.75
    day_length_hours: int = 12
    storm_strength: float = 0.0
    season_length_days: int = DEFAULT_SEASON_LENGTH_DAYS
    ground_frozen: bool = False
    river_frozen: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "season", str(self.season) if self.season in SEASONS else "Spring")
        object.__setattr__(
            self,
            "weather",
            str(self.weather) if self.weather in WEATHER_TYPES else "Clear",
        )
        object.__setattr__(
            self,
            "previous_weather",
            str(self.previous_weather) if self.previous_weather in WEATHER_TYPES else "Clear",
        )
        object.__setattr__(self, "temperature_c", clamp(float(self.temperature_c), -50.0, 60.0))
        object.__setattr__(self, "humidity", clamp(float(self.humidity), 0.0, 1.0))
        object.__setattr__(self, "wind", clamp(float(self.wind), 0.0, 1.0))
        object.__setattr__(self, "cloud_cover", clamp(float(self.cloud_cover), 0.0, 1.0))
        object.__setattr__(self, "rainfall", clamp(float(self.rainfall), 0.0, 5.0))
        object.__setattr__(self, "snowfall", clamp(float(self.snowfall), 0.0, 5.0))
        object.__setattr__(self, "ground_moisture", clamp(float(self.ground_moisture), 0.0, 1.0))
        object.__setattr__(self, "river_level", clamp(float(self.river_level), 0.0, 1.0))
        object.__setattr__(self, "sunlight", clamp(float(self.sunlight), 0.0, 1.0))
        object.__setattr__(self, "storm_strength", clamp(float(self.storm_strength), 0.0, 1.0))
        object.__setattr__(self, "day_length_hours", clamp(int(self.day_length_hours), 4, 20))
        object.__setattr__(self, "season_length_days", max(1, int(self.season_length_days)))
        object.__setattr__(self, "day_of_season", max(1, int(self.day_of_season)))
        object.__setattr__(self, "tick_number", max(0, int(self.tick_number)))
        object.__setattr__(self, "day_number", max(0, int(self.day_number)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "tick_number": self.tick_number,
            "day_number": self.day_number,
            "season": self.season,
            "day_of_season": self.day_of_season,
            "weather": self.weather,
            "previous_weather": self.previous_weather,
            "temperature_c": self.temperature_c,
            "humidity": self.humidity,
            "wind": self.wind,
            "cloud_cover": self.cloud_cover,
            "rainfall": self.rainfall,
            "snowfall": self.snowfall,
            "ground_moisture": self.ground_moisture,
            "river_level": self.river_level,
            "sunlight": self.sunlight,
            "day_length_hours": self.day_length_hours,
            "storm_strength": self.storm_strength,
            "season_length_days": self.season_length_days,
            "ground_frozen": bool(self.ground_frozen),
            "river_frozen": bool(self.river_frozen),
        }

    @staticmethod
    def from_dict(data: Mapping[str, Any]) -> "WeatherState":
        d = dict(data) if isinstance(data, Mapping) else {}
        return WeatherState(
            tick_number=int(d.get("tick_number", 0)),
            day_number=int(d.get("day_number", 0)),
            season=str(d.get("season", "Spring")),
            day_of_season=int(d.get("day_of_season", 1)),
            weather=str(d.get("weather", "Clear")),
            previous_weather=str(d.get("previous_weather", "Clear")),
            temperature_c=float(d.get("temperature_c", 15.0)),
            humidity=float(d.get("humidity", 0.5)),
            wind=float(d.get("wind", 0.1)),
            cloud_cover=float(d.get("cloud_cover", 0.1)),
            rainfall=float(d.get("rainfall", 0.0)),
            snowfall=float(d.get("snowfall", 0.0)),
            ground_moisture=float(d.get("ground_moisture", 0.5)),
            river_level=float(d.get("river_level", 0.5)),
            sunlight=float(d.get("sunlight", 0.75)),
            day_length_hours=int(d.get("day_length_hours", 12)),
            storm_strength=float(d.get("storm_strength", 0.0)),
            season_length_days=int(d.get("season_length_days", DEFAULT_SEASON_LENGTH_DAYS)),
            ground_frozen=bool(d.get("ground_frozen", False)),
            river_frozen=bool(d.get("river_frozen", False)),
        )

    @staticmethod
    def initial(tick_number: int = 0, season_length_days: int = DEFAULT_SEASON_LENGTH_DAYS) -> "WeatherState":
        tick = max(0, int(tick_number))
        day = day_of_tick(tick)
        season = season_for_day(day, season_length_days)
        dos = season_day(day, season_length_days)
        base_temp = float(SEASON_BASE_TEMP.get(season, 15.0))
        base_hum = float(SEASON_BASE_HUMIDITY.get(season, 0.5))
        base_sun = float(SEASON_BASE_SUNLIGHT.get(season, 0.75))
        dlh = day_length_hours(season)
        return WeatherState(
            tick_number=tick,
            day_number=day,
            season=season,
            day_of_season=dos,
            weather="Clear",
            previous_weather="Clear",
            temperature_c=base_temp,
            humidity=base_hum,
            wind=0.1,
            cloud_cover=0.1,
            rainfall=0.0,
            snowfall=0.0,
            ground_moisture=0.5,
            river_level=0.5,
            sunlight=base_sun,
            day_length_hours=dlh,
            storm_strength=0.0,
            season_length_days=season_length_days,
            ground_frozen=False,
            river_frozen=False,
        )


def weather_modifier(weather: str, key: str) -> float:
    wmap = WEATHER_MODIFIERS.get(str(weather), {})
    return float(wmap.get(key, 0.0))
