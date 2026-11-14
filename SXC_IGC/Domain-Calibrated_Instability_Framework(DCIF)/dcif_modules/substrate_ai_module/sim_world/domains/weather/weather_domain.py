from __future__ import annotations

from typing import Any, Mapping

from ...core.contracts import TransitionProposal
from ...simulation.simulation_engine import SimulationEngine
from .weather_models import (
    DEFAULT_SEASON_LENGTH_DAYS,
    SEASONS,
    WEATHER_TYPES,
    WeatherState,
    clamp,
    season_for_day,
)
from .weather_rules import (
    RAINY_WEATHERS,
    STORMY_WEATHERS,
    advance_weather_tick,
    agriculture_growth_multiplier,
    is_outdoor_work_possible,
    should_prioritize_fuel,
    should_seek_shelter,
    weather_effect_on_comfort,
    weather_effect_on_thirst_need,
    weather_effect_on_travel,
    weather_effect_on_warmth_need,
    weather_effect_on_work,
)


def _extract_context(context: Any) -> dict[str, Any]:
    try:
        state = dict(getattr(context, "world_state", None) or {})
    except Exception:
        state = {}
    try:
        tick_number = int(getattr(context, "tick_number", 0))
    except Exception:
        tick_number = 0
    try:
        world_id = getattr(context, "world_id", None)
    except Exception:
        world_id = None
    try:
        tick_context = getattr(context, "tick_context", None)
    except Exception:
        tick_context = None
    try:
        committed_revision = getattr(context, "committed_revision", None)
    except Exception:
        committed_revision = None
    try:
        correlation_id = (
            getattr(tick_context, "correlation_id", None)
            if tick_context is not None
            else None
        )
    except Exception:
        correlation_id = None
    try:
        tick_id = (
            getattr(tick_context, "tick_id", None) if tick_context is not None else None
        )
    except Exception:
        tick_id = None
    return {
        "state": state,
        "tick_number": tick_number,
        "world_id": world_id,
        "tick_context": tick_context,
        "committed_revision": committed_revision,
        "correlation_id": correlation_id,
        "tick_id": tick_id,
    }


def _id_str(oid: Any) -> str:
    if oid is None:
        return ""
    if hasattr(oid, "value"):
        try:
            return str(getattr(oid, "value"))
        except Exception:
            return str(oid)
    return str(oid)


def _normalize_identifier(value: Any, allowed: tuple[str, ...], default: str) -> str:
    v = str(value)
    if v in allowed:
        return v
    return str(default)


def _read_weather_state(world_state: Mapping[str, Any]) -> WeatherState:
    weather_dict = dict(world_state.get("weather", {})) if isinstance(world_state, Mapping) else {}
    if not weather_dict or "tick_number" not in weather_dict:
        return WeatherState.initial(season_length_days=int(weather_dict.get("season_length_days", DEFAULT_SEASON_LENGTH_DAYS)))
    return WeatherState.from_dict(weather_dict)


def _make_proposal(
    info: Mapping[str, Any],
    patch: Mapping[str, Any],
    metadata: Mapping[str, Any],
    description: str,
) -> TransitionProposal:
    return TransitionProposal(
        world_id=info.get("world_id"),
        tick_id=info.get("tick_id"),
        state_revision=info.get("committed_revision"),
        correlation_id=info.get("correlation_id"),
        subject="domain.weather",
        patch=dict(patch),
        description=str(description),
        metadata=dict(metadata),
    )


def _legacy_weather_state_code(rich_weather: str, temperature_c: float) -> str:
    w = str(rich_weather)
    if w == "Clear":
        return "clear"
    if w == "Cloudy":
        return "cloudy"
    if w == "Light Rain" or w == "Heavy Rain":
        return "rain"
    if w == "Storm":
        return "storm"
    if w == "Fog":
        return "cloudy"
    if w == "Snow" or w == "Blizzard":
        return "snow"
    if w == "Heat Wave":
        return "drought"
    if w == "Cold Wave":
        return "cold"
    if float(temperature_c) < 2.0:
        return "cold"
    return "sunny"


def _attach_compat_state(weather_dict: Mapping[str, Any]) -> dict[str, Any]:
    d = dict(weather_dict)
    if "state" not in d:
        d["state"] = _legacy_weather_state_code(
            str(d.get("weather", "Clear")), float(d.get("temperature_c", 15.0))
        )
    return d


def register(engine: SimulationEngine) -> None:
    engine.register_domain("weather", lambda engine, context: (apply(context),))


def apply(context: Any) -> TransitionProposal:
    info = _extract_context(context)
    world_state = info.get("state") or {}
    current_weather_state = _read_weather_state(world_state)
    next_tick = int(info.get("tick_number") or 0)
    new_ws, events = advance_weather_tick(current_weather_state, next_tick)
    patch: dict[str, Any] = {"weather": _attach_compat_state(new_ws.to_dict())}
    meta: dict[str, Any] = {
        "domain": "weather",
        "action": "weather_tick_update",
        "tick_number": next_tick,
        "season": new_ws.season,
        "weather": new_ws.weather,
        "state": _legacy_weather_state_code(new_ws.weather, new_ws.temperature_c),
        "temperature_c": new_ws.temperature_c,
        "humidity": new_ws.humidity,
        "ground_moisture": new_ws.ground_moisture,
        "river_level": new_ws.river_level,
        "events": tuple(ev.to_dict() for ev in events),
    }
    desc = (
        f"weather update tick={next_tick} "
        f"season={new_ws.season}({new_ws.day_of_season}) "
        f"weather={new_ws.weather} t={round(new_ws.temperature_c, 1)}C"
    )
    return _make_proposal(info, patch, meta, desc)


def get_weather_state(context_or_state: Any) -> WeatherState:
    state = context_or_state
    if not isinstance(context_or_state, Mapping):
        state = dict(getattr(context_or_state, "current_state", None) or {})
        if not state:
            try:
                info = _extract_context(context_or_state)
                state = info.get("state") or {}
            except Exception:
                state = {}
    return _read_weather_state(state)


def get_weather_summary(context_or_state: Any) -> dict[str, Any]:
    ws = get_weather_state(context_or_state)
    return ws.to_dict()


def get_season(context_or_state: Any) -> str:
    return str(get_weather_state(context_or_state).season)


def get_current_weather(context_or_state: Any) -> str:
    return str(get_weather_state(context_or_state).weather)


def get_current_temperature(context_or_state: Any) -> float:
    return float(get_weather_state(context_or_state).temperature_c)


def get_ground_moisture(context_or_state: Any) -> float:
    return float(get_weather_state(context_or_state).ground_moisture)


def get_river_level(context_or_state: Any) -> float:
    return float(get_weather_state(context_or_state).river_level)


def get_sunlight(context_or_state: Any) -> float:
    return float(get_weather_state(context_or_state).sunlight)


def is_weather_stormy(context_or_state: Any) -> bool:
    return str(get_current_weather(context_or_state)) in STORMY_WEATHERS


def is_weather_rainy(context_or_state: Any) -> bool:
    return str(get_current_weather(context_or_state)) in RAINY_WEATHERS


def can_work_outdoors(context_or_state: Any) -> bool:
    ws = get_weather_state(context_or_state)
    return is_outdoor_work_possible(ws.weather, ws.temperature_c)


def work_efficiency_multiplier(context_or_state: Any) -> float:
    ws = get_weather_state(context_or_state)
    return weather_effect_on_work(ws.weather)


def travel_efficiency_multiplier(context_or_state: Any) -> float:
    ws = get_weather_state(context_or_state)
    return weather_effect_on_travel(ws.weather)


def warmth_need_penalty(context_or_state: Any) -> float:
    ws = get_weather_state(context_or_state)
    return weather_effect_on_warmth_need(ws.weather, ws.temperature_c)


def thirst_need_penalty(context_or_state: Any) -> float:
    ws = get_weather_state(context_or_state)
    return weather_effect_on_thirst_need(ws.weather, ws.temperature_c)


def comfort_level(context_or_state: Any) -> float:
    ws = get_weather_state(context_or_state)
    return weather_effect_on_comfort(ws.weather)


def agriculture_multiplier(context_or_state: Any) -> float:
    ws = get_weather_state(context_or_state)
    return agriculture_growth_multiplier(
        ws.season, ws.weather, ws.temperature_c, ws.ground_moisture
    )


def prioritise_fuel(context_or_state: Any) -> bool:
    ws = get_weather_state(context_or_state)
    return should_prioritize_fuel(ws.season, ws.weather, ws.temperature_c)


def should_go_to_shelter(context_or_state: Any) -> bool:
    ws = get_weather_state(context_or_state)
    return should_seek_shelter(ws.weather, ws.temperature_c)


def force_weather_override_action(
    context: Any,
    target_weather: str,
) -> TransitionProposal | tuple[()]:
    info = _extract_context(context)
    state = info.get("state") or {}
    target = _normalize_identifier(target_weather, WEATHER_TYPES, "Clear")
    ws = _read_weather_state(state)
    tick = int(info.get("tick_number") or 0)
    new_ws, events = advance_weather_tick(ws, tick, force_weather_override=target)
    patch: dict[str, Any] = {"weather": _attach_compat_state(new_ws.to_dict())}
    meta: dict[str, Any] = {
        "domain": "weather",
        "action": "force_weather_override",
        "target_weather": target,
        "state": _legacy_weather_state_code(target, new_ws.temperature_c),
        "tick_number": tick,
        "events": tuple(ev.to_dict() for ev in events),
    }
    return _make_proposal(info, patch, meta, f"force weather override to {target}")


def set_season_action(
    context: Any,
    target_season: str,
    season_length_days: int | None = None,
) -> TransitionProposal | tuple[()]:
    info = _extract_context(context)
    state = info.get("state") or {}
    ws = _read_weather_state(state)
    target = _normalize_identifier(target_season, SEASONS, "Spring")
    length = int(
        season_length_days
        if season_length_days is not None
        else ws.season_length_days
    )
    data = ws.to_dict()
    data["season"] = target
    data["day_of_season"] = 1
    data["day_length_hours"] = 12
    data["season_length_days"] = length
    new_ws = WeatherState.from_dict(data)
    from .weather_events import SeasonChanged, WeatherChanged
    events: list[Any] = [
        SeasonChanged(
            tick_number=int(info.get("tick_number") or 0),
            old_season=ws.season,
            new_season=target,
            day_of_season=1,
        )
    ]
    if ws.weather != new_ws.weather:
        events.append(
            WeatherChanged(
                tick_number=int(info.get("tick_number") or 0),
                old_weather=ws.weather,
                new_weather=new_ws.weather,
                temperature_c=new_ws.temperature_c,
            )
        )
    patch: dict[str, Any] = {"weather": _attach_compat_state(new_ws.to_dict())}
    meta: dict[str, Any] = {
        "domain": "weather",
        "action": "set_season",
        "target_season": target,
        "season_length_days": length,
        "state": _legacy_weather_state_code(new_ws.weather, new_ws.temperature_c),
        "events": tuple(ev.to_dict() for ev in events),
    }
    return _make_proposal(info, patch, meta, f"set season to {target}")


def generate_weather_goals(context_or_state: Any) -> list[dict[str, Any]]:
    goals: list[dict[str, Any]] = []
    ws = get_weather_state(context_or_state)
    if should_seek_shelter(ws.weather, ws.temperature_c):
        goals.append(
            {
                "kind": "shelter",
                "subject": f"seek shelter during {ws.weather}",
                "target_state": {"room": "house_1", "status": "sheltering"},
                "priority": 88,
                "reason": {"weather": ws.weather, "temperature_c": ws.temperature_c},
            }
        )
    if should_prioritize_fuel(ws.season, ws.weather, ws.temperature_c):
        goals.append(
            {
                "kind": "fuel",
                "subject": "gather fuel for cold weather",
                "target_state": {"resource_type": "fuel", "minimum": 20.0},
                "priority": 75,
                "reason": {
                    "season": ws.season,
                    "weather": ws.weather,
                    "temperature_c": ws.temperature_c,
                },
            }
        )
    if ws.weather in ("Storm", "Heavy Rain"):
        goals.append(
            {
                "kind": "harvest_delay",
                "subject": "delay harvesting due to bad weather",
                "target_state": {"outdoor_work": False},
                "priority": 70,
                "reason": {"weather": ws.weather},
            }
        )
    return goals
