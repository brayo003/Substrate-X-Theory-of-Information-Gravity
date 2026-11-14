from __future__ import annotations

from typing import Any

from .weather_events import (
    ColdWaveStarted,
    FogAppeared,
    FogCleared,
    GroundFrozen,
    GroundThawed,
    HeatWaveStarted,
    RainStarted,
    RainStopped,
    RiverFlooded,
    RiverReceded,
    SeasonChanged,
    SnowStarted,
    SnowStopped,
    StormEnded,
    StormStarted,
    WeatherChanged,
)
from .weather_models import (
    SEASON_BASE_HUMIDITY,
    SEASON_BASE_SUNLIGHT,
    SEASON_BASE_TEMP,
    SEASON_TEMP_VARIATION,
    SEASONS,
    TICKS_PER_DAY,
    WEATHER_MODIFIERS,
    WEATHER_TYPES,
    WeatherState,
    clamp,
    day_length_hours,
    day_of_tick,
    deterministic_hash,
    hour_of_tick,
    season_day,
    season_for_day,
    weather_modifier,
)


RAINY_WEATHERS: tuple[str, ...] = ("Light Rain", "Heavy Rain", "Storm")
SNOWY_WEATHERS: tuple[str, ...] = ("Snow", "Blizzard")
STORMY_WEATHERS: tuple[str, ...] = ("Storm", "Blizzard")
EXTREME_WEATHERS: tuple[str, ...] = ("Storm", "Blizzard", "Heat Wave", "Cold Wave")
FOG_WEATHERS: tuple[str, ...] = ("Fog",)


def _is_rainy(w: str) -> bool:
    return str(w) in RAINY_WEATHERS


def _is_snowy(w: str) -> bool:
    return str(w) in SNOWY_WEATHERS


def _is_stormy(w: str) -> bool:
    return str(w) in STORMY_WEATHERS


def _is_extreme(w: str) -> bool:
    return str(w) in EXTREME_WEATHERS


def hour_temperature_cycle(hour: int) -> float:
    h = int(hour) % 24
    if h < 6 or h >= 20:
        return -0.35
    if h < 9 or h >= 17:
        return -0.1
    if h >= 12 and h <= 15:
        return +0.3
    return +0.15


def compute_season_day_temperature(
    season: str,
    day_of_season: int,
    hour: int,
    *,
    season_length_days: int = 30,
) -> float:
    base_temp = float(SEASON_BASE_TEMP.get(str(season), 15.0))
    variation = float(SEASON_TEMP_VARIATION.get(str(season), 6.0))
    length = max(1, int(season_length_days))
    dos = max(1, min(length, int(day_of_season)))
    phase = (dos - 1) / length
    swing = (phase - 0.5) * 2.0
    hcycle = hour_temperature_cycle(hour)
    return clamp(base_temp + swing * variation + hcycle * variation, -50.0, 60.0)


def choose_next_weather(
    current_weather: str,
    season: str,
    tick_number: int,
    day_of_season: int,
) -> str:
    seed = f"wtx:{season}:{day_of_season}:{tick_number}:{current_weather}"
    h = deterministic_hash(seed)

    def roll(n: int) -> int:
        return h % max(1, int(n))

    cur = str(current_weather)
    sn = str(season)

    if cur == "Storm":
        r = roll(7)
        if r < 2:
            return "Storm"
        if r < 5:
            return "Heavy Rain"
        return "Cloudy"
    if cur == "Blizzard":
        r = roll(7)
        if r < 2:
            return "Blizzard"
        if r < 5:
            return "Snow"
        return "Cloudy"
    if cur == "Heat Wave":
        r = roll(6)
        if r < 2:
            return "Heat Wave"
        if r < 4:
            return "Clear"
        return "Cloudy"
    if cur == "Cold Wave":
        r = roll(6)
        if r < 2:
            return "Cold Wave"
        if r < 4:
            return "Cloudy"
        return "Snow"
    if cur == "Heavy Rain":
        r = roll(6)
        if r == 0:
            return "Storm"
        if r < 3:
            return "Heavy Rain"
        if r < 5:
            return "Light Rain"
        return "Cloudy"
    if cur == "Light Rain":
        r = roll(7)
        if r == 0:
            return "Heavy Rain"
        if r < 3:
            return "Light Rain"
        if r < 5:
            return "Cloudy"
        return "Fog" if roll(3) == 0 else "Clear"
    if cur == "Snow":
        r = roll(7)
        if r == 0:
            return "Blizzard"
        if r < 3:
            return "Snow"
        if r < 5:
            return "Cloudy"
        return "Fog"
    if cur == "Fog":
        r = roll(5)
        if r < 2:
            return "Fog"
        if r == 2:
            return "Cloudy"
        return "Clear"
    if cur == "Cloudy":
        r = roll(13)
        if sn == "Winter":
            if r == 0:
                return "Blizzard"
            if r < 4:
                return "Snow"
            if r < 7:
                return "Cloudy"
            if r == 7:
                return "Fog"
            if r == 8:
                return "Cold Wave"
            return "Clear"
        if sn == "Summer":
            if r == 0:
                return "Storm"
            if r < 3:
                return "Light Rain"
            if r < 6:
                return "Cloudy"
            if r < 10:
                return "Clear"
            return "Heat Wave"
        if sn == "Spring":
            if r == 0:
                return "Storm"
            if r < 4:
                return "Light Rain"
            if r < 6:
                return "Heavy Rain"
            if r < 9:
                return "Cloudy"
            if r == 9:
                return "Fog"
            return "Clear"
        if sn == "Autumn":
            if r == 0:
                return "Storm"
            if r < 3:
                return "Light Rain"
            if r < 5:
                return "Fog"
            if r < 9:
                return "Cloudy"
            return "Clear"
        return "Cloudy"
    if cur == "Clear":
        r = roll(13)
        if sn == "Winter":
            if r == 0:
                return "Cold Wave"
            if r < 3:
                return "Clear"
            if r < 7:
                return "Cloudy"
            if r == 7:
                return "Fog"
            return "Snow"
        if sn == "Summer":
            if r == 0:
                return "Heat Wave"
            if r < 7:
                return "Clear"
            if r < 10:
                return "Cloudy"
            if r < 12:
                return "Light Rain"
            return "Storm"
        if sn == "Spring":
            if r < 5:
                return "Clear"
            if r < 9:
                return "Cloudy"
            if r < 11:
                return "Light Rain"
            if r == 11:
                return "Fog"
            return "Storm"
        if sn == "Autumn":
            if r < 4:
                return "Clear"
            if r < 8:
                return "Cloudy"
            if r < 10:
                return "Fog"
            if r < 12:
                return "Light Rain"
            return "Storm"
        return "Clear"
    return "Clear"


def compute_rainfall(weather: str) -> float:
    w = str(weather)
    if w == "Light Rain":
        return 0.4
    if w == "Heavy Rain":
        return 1.0
    if w == "Storm":
        return 1.3
    return 0.0


def compute_snowfall(weather: str) -> float:
    w = str(weather)
    if w == "Snow":
        return 0.6
    if w == "Blizzard":
        return 1.4
    return 0.0


def compute_storm_strength(weather: str) -> float:
    w = str(weather)
    if w == "Storm":
        return 0.85
    if w == "Blizzard":
        return 0.75
    if w == "Heavy Rain":
        return 0.25
    if w == "Light Rain" or w == "Snow":
        return 0.1
    return 0.0


def compute_environmental_effects(
    next_weather: str,
    next_temperature: float,
    prev_moisture: float,
    prev_river: float,
    prev_sunlight: float,
    season: str,
    hour: int,
) -> tuple[float, float, float, float, float, bool, bool]:
    rain = compute_rainfall(next_weather)
    snow = compute_snowfall(next_weather)

    moisture_add = 0.0
    if rain > 0.0:
        moisture_add += rain * 0.08
    if snow > 0.0:
        moisture_add += snow * 0.04
    moisture_decay = 0.008 if next_weather in ("Clear", "Heat Wave") else 0.002
    if next_temperature > 25.0:
        moisture_decay += 0.01
    moisture = clamp(prev_moisture + moisture_add - moisture_decay, 0.0, 1.0)

    river_add = rain * 0.05 + snow * 0.02
    river_decay = 0.005 if prev_river > 0.5 else 0.002
    river = clamp(prev_river + river_add - river_decay, 0.0, 1.0)

    storm = compute_storm_strength(next_weather)

    cloud = float(WEATHER_MODIFIERS.get(next_weather, {}).get("cloud", 0.05))
    sun_season = float(SEASON_BASE_SUNLIGHT.get(season, 0.7))
    dl = day_length_hours(season)
    is_day = (hour >= 6 and hour < (6 + dl))
    sun_day = 1.0 if is_day else 0.0
    if is_day and hour >= 10 and hour <= 14:
        sun_day = 1.1
    sun_base = sun_season * sun_day
    sunlight = clamp(sun_base * (1.0 - 0.8 * cloud) - 0.0, 0.0, 1.0)

    frozen_ground = bool(next_temperature <= -2.0)
    frozen_river = bool(next_temperature <= -3.0 and prev_river > 0.0)

    return moisture, river, storm, sunlight, rain + snow, frozen_ground, frozen_river


def advance_weather_tick(
    state: WeatherState,
    next_tick_number: int,
    *,
    update_on_hour_boundary_only: bool = True,
    force_weather_override: str | None = None,
) -> tuple[WeatherState, tuple[Any, ...]]:
    s = state
    next_tick = max(0, int(next_tick_number))
    prev_day = int(s.day_number)
    next_day = day_of_tick(next_tick)
    hour = hour_of_tick(next_tick)

    events: list[Any] = []

    prev_season = str(s.season)
    next_season = season_for_day(next_day, s.season_length_days)
    next_dos = season_day(next_day, s.season_length_days)
    if prev_season != next_season:
        events.append(
            SeasonChanged(
                tick_number=next_tick,
                old_season=prev_season,
                new_season=next_season,
                day_of_season=next_dos,
            )
        )

    seasonal_temp = compute_season_day_temperature(
        next_season, next_dos, hour, season_length_days=s.season_length_days
    )

    boundary_tick = (not update_on_hour_boundary_only) or (next_tick % TICKS_PER_DAY == 0 or next_tick == 0)
    if force_weather_override is not None:
        nxt_weather = str(force_weather_override)
        if nxt_weather not in WEATHER_TYPES:
            nxt_weather = "Clear"
    elif boundary_tick or next_season != prev_season:
        nxt_weather = choose_next_weather(s.weather, next_season, next_tick, next_dos)
    else:
        nxt_weather = str(s.weather)

    prev_weather = str(s.weather)
    if nxt_weather != prev_weather:
        events.append(
            WeatherChanged(
                tick_number=next_tick,
                old_weather=prev_weather,
                new_weather=nxt_weather,
                temperature_c=seasonal_temp,
            )
        )
    cur_for_events = nxt_weather

    if _is_rainy(cur_for_events) and not _is_rainy(prev_weather):
        events.append(
            RainStarted(
                tick_number=next_tick,
                rainfall=compute_rainfall(cur_for_events),
                weather=cur_for_events,
            )
        )
    if not _is_rainy(cur_for_events) and _is_rainy(prev_weather):
        total_rain = s.rainfall
        events.append(RainStopped(tick_number=next_tick, total_rainfall=total_rain))

    if _is_snowy(cur_for_events) and not _is_snowy(prev_weather):
        events.append(
            SnowStarted(
                tick_number=next_tick,
                snowfall=compute_snowfall(cur_for_events),
                weather=cur_for_events,
            )
        )
    if not _is_snowy(cur_for_events) and _is_snowy(prev_weather):
        total_snow = s.snowfall
        events.append(SnowStopped(tick_number=next_tick, total_snowfall=total_snow))

    if _is_stormy(cur_for_events) and not _is_stormy(prev_weather):
        wind = float(WEATHER_MODIFIERS.get(cur_for_events, {}).get("wind", 0.5))
        events.append(
            StormStarted(
                tick_number=next_tick,
                storm_strength=compute_storm_strength(cur_for_events),
                wind=wind,
            )
        )
    if not _is_stormy(cur_for_events) and _is_stormy(prev_weather):
        peak = max(s.storm_strength, compute_storm_strength(prev_weather))
        damage = clamp(peak * 0.4, 0.0, 1.0)
        events.append(
            StormEnded(
                tick_number=next_tick,
                peak_storm_strength=peak,
                damage_level=damage,
            )
        )

    if cur_for_events == "Heat Wave" and prev_weather != "Heat Wave":
        t = seasonal_temp + float(WEATHER_MODIFIERS["Heat Wave"].get("temp", 9.0))
        events.append(
            HeatWaveStarted(
                tick_number=next_tick, temperature_c=t, duration_estimate_ticks=TICKS_PER_DAY
            )
        )
    if cur_for_events == "Cold Wave" and prev_weather != "Cold Wave":
        t = seasonal_temp + float(WEATHER_MODIFIERS["Cold Wave"].get("temp", -10.0))
        events.append(
            ColdWaveStarted(
                tick_number=next_tick, temperature_c=t, duration_estimate_ticks=TICKS_PER_DAY
            )
        )

    if cur_for_events == "Fog" and prev_weather != "Fog":
        events.append(FogAppeared(tick_number=next_tick, visibility=0.3))
    if cur_for_events != "Fog" and prev_weather == "Fog":
        events.append(FogCleared(tick_number=next_tick, visibility=1.0))

    wmod_temp = weather_modifier(cur_for_events, "temp")
    wmod_hum = weather_modifier(cur_for_events, "humidity")
    wmod_wind = weather_modifier(cur_for_events, "wind")
    wmod_cloud = weather_modifier(cur_for_events, "cloud")
    next_temp = clamp(seasonal_temp + wmod_temp, -50.0, 60.0)
    base_hum = float(SEASON_BASE_HUMIDITY.get(next_season, 0.5))
    next_hum = clamp(base_hum + wmod_hum, 0.0, 1.0)
    next_wind = clamp(0.1 + wmod_wind, 0.0, 1.0)
    next_cloud = clamp(wmod_cloud, 0.0, 1.0)

    moisture, river, storm_s, sunlight, pcp, frozen_g, frozen_r = compute_environmental_effects(
        cur_for_events,
        next_temp,
        float(s.ground_moisture),
        float(s.river_level),
        float(s.sunlight),
        next_season,
        hour,
    )

    if not s.ground_frozen and frozen_g:
        events.append(GroundFrozen(tick_number=next_tick, temperature_c=next_temp))
    if s.ground_frozen and not frozen_g:
        events.append(GroundThawed(tick_number=next_tick, temperature_c=next_temp))

    was_flooded = s.river_level >= 0.9
    will_flood = river >= 0.9
    if will_flood and not was_flooded:
        events.append(RiverFlooded(tick_number=next_tick, river_level=river))
    if was_flooded and not will_flood:
        events.append(RiverReceded(tick_number=next_tick, river_level=river))

    rainfall_val = compute_rainfall(cur_for_events)
    snowfall_val = compute_snowfall(cur_for_events)

    next_state = WeatherState(
        tick_number=next_tick,
        day_number=next_day,
        season=next_season,
        day_of_season=next_dos,
        weather=cur_for_events,
        previous_weather=prev_weather,
        temperature_c=next_temp,
        humidity=next_hum,
        wind=next_wind,
        cloud_cover=next_cloud,
        rainfall=rainfall_val,
        snowfall=snowfall_val,
        ground_moisture=moisture,
        river_level=river,
        sunlight=sunlight,
        day_length_hours=day_length_hours(next_season),
        storm_strength=storm_s,
        season_length_days=s.season_length_days,
        ground_frozen=frozen_g,
        river_frozen=frozen_r,
    )
    return next_state, tuple(events)


def weather_effect_on_work(weather: str) -> float:
    w = str(weather)
    if w == "Storm" or w == "Blizzard":
        return 0.3
    if w == "Heavy Rain":
        return 0.65
    if w == "Light Rain" or w == "Snow":
        return 0.85
    if w == "Fog":
        return 0.8
    if w == "Cold Wave":
        return 0.75
    if w == "Heat Wave":
        return 0.7
    return 1.0


def weather_effect_on_travel(weather: str) -> float:
    w = str(weather)
    if w == "Storm":
        return 0.3
    if w == "Blizzard":
        return 0.2
    if w == "Snow":
        return 0.6
    if w == "Heavy Rain":
        return 0.55
    if w == "Light Rain":
        return 0.8
    if w == "Fog":
        return 0.7
    if w == "Cold Wave":
        return 0.8
    return 1.0


def weather_effect_on_warmth_need(weather: str, temperature: float) -> float:
    delta = 0.0
    if temperature < 0.0:
        delta = max(delta, 0.2 - temperature * 0.008)
    elif temperature < 10.0:
        delta = max(delta, 0.08)
    if str(weather) in RAINY_WEATHERS:
        delta = max(delta, 0.12)
    if str(weather) in SNOWY_WEATHERS:
        delta = max(delta, 0.18)
    if str(weather) in STORMY_WEATHERS:
        delta = max(delta, 0.2)
    return clamp(delta, 0.0, 1.0)


def weather_effect_on_thirst_need(weather: str, temperature: float) -> float:
    delta = 0.0
    if temperature > 28.0:
        delta = max(delta, (temperature - 28.0) * 0.015)
    if temperature > 22.0:
        delta = max(delta, 0.05)
    if str(weather) == "Heat Wave":
        delta = max(delta, 0.15)
    return clamp(delta, 0.0, 1.0)


def weather_effect_on_comfort(weather: str) -> float:
    w = str(weather)
    if w == "Storm" or w == "Blizzard":
        return 0.25
    if w == "Heavy Rain":
        return 0.45
    if w == "Cold Wave" or w == "Heat Wave":
        return 0.5
    if w == "Light Rain" or w == "Snow" or w == "Fog":
        return 0.75
    return 1.0


def agriculture_growth_multiplier(
    season: str,
    weather: str,
    temperature: float,
    ground_moisture: float,
) -> float:
    mult = 1.0
    if str(season) == "Winter":
        mult *= 0.2
    if str(weather) in RAINY_WEATHERS:
        mult *= 1.0
    if str(weather) == "Storm":
        mult *= 0.6
    if str(weather) == "Drought" or (ground_moisture < 0.15):
        mult *= 0.4
    if temperature < 3.0:
        mult *= 0.4
    if temperature > 35.0:
        mult *= 0.5
    return clamp(mult, 0.0, 3.0)


def is_outdoor_work_possible(weather: str, temperature: float) -> bool:
    if str(weather) in ("Storm", "Blizzard"):
        return False
    if str(weather) == "Heat Wave" and temperature > 38.0:
        return False
    if str(weather) == "Cold Wave" and temperature < -15.0:
        return False
    return True


def should_prioritize_fuel(season: str, weather: str, temperature: float) -> bool:
    if str(season) == "Winter":
        return True
    if temperature < 5.0:
        return True
    if str(weather) in ("Cold Wave", "Blizzard", "Snow"):
        return True
    return False


def should_seek_shelter(weather: str, temperature: float) -> bool:
    if str(weather) in STORMY_WEATHERS:
        return True
    if temperature < -5.0 or temperature > 38.0:
        return True
    if str(weather) in ("Cold Wave", "Heat Wave"):
        return True
    return False
