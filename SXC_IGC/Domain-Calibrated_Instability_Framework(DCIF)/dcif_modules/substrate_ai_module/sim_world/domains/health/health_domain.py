from __future__ import annotations

from typing import Any, Mapping

from sim_world.core.contracts import TransitionProposal
from sim_world.simulation.simulation_engine import SimulationEngine

from .health_events import (
    DeathOccurred,
    HEALTH_EVENT_TYPES,
    HealthDeclined,
    HealthImproved,
    IllnessRecovered,
    IllnessStarted,
    InjuryOccurred,
    InjuryRecovered,
)
from .health_models import (
    HEALTH_MAX,
    HEALTH_MIN,
    ILLNESS_TYPES,
    INJURY_TYPES,
    HealthState,
    clamp,
    make_health_state_id,
)
from .health_rules import (
    compute_overall_health_from_components,
    evaluate_villager_health_tick,
    should_go_to_hospital_or_home,
    should_prioritize_rest,
    should_seek_shelter_for_health,
    work_efficiency_multiplier_for,
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
            v = getattr(oid, "value")
            return str(v)
        except Exception:
            return str(oid)
    return str(oid)


def _read_health_state(state: Mapping[str, Any], entity_id: str) -> HealthState:
    key = str(entity_id)
    top_map = state.get("health_states", {}) if isinstance(state, Mapping) else {}
    try:
        raw = top_map.get(key)
    except Exception:
        raw = None
    if raw is None:
        entity_data = {}
        entities = state.get("entities", {}) if isinstance(state, Mapping) else {}
        if isinstance(entities, Mapping):
            ed = entities.get(key)
            if isinstance(ed, Mapping):
                components = dict(ed.get("components", {}))
                hc = components.get("HealthComponent", {})
                if isinstance(hc, Mapping) and hc.get("health_state"):
                    raw = hc.get("health_state")
    if raw is None:
        return HealthState.initial(key)
    if isinstance(raw, HealthState):
        return raw
    if isinstance(raw, Mapping):
        return HealthState.from_dict(dict(raw))
    try:
        if hasattr(raw, "to_dict"):
            return HealthState.from_dict(raw.to_dict())
    except Exception:
        pass
    return HealthState.initial(key)


def _weather_from_state(state: Mapping[str, Any]) -> tuple[float, str]:
    w = state.get("weather", {}) if isinstance(state, Mapping) else {}
    if isinstance(w, Mapping):
        temp = float(w.get("temperature_c", 15.0) or 15.0)
        short = str(w.get("state", w.get("weather", "clear")) or "clear").lower()
        return temp, short
    return 15.0, "clear"


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
        subject="domain.health",
        patch=dict(patch),
        description=str(description),
        metadata=dict(metadata),
    )


def register(engine: SimulationEngine) -> None:
    engine.register_domain("health", lambda engine, context: (apply(context),))


def _action_flags_from_entity_metadata(metadata: Mapping[str, Any]) -> dict[str, Any]:
    md = dict(metadata) if metadata else {}
    la = str(md.get("last_action") or md.get("current_action") or "").lower()
    status = str(md.get("status") or "").lower()
    did_eat = "eat" in la or "cook" in la or "dine" in la or "food" in status
    did_drink = "drink" in la or "water" in status
    did_sleep = "sleep" in la or "resting" == status or "sleeping" in status
    did_rest = "rest" in la or did_sleep or "rest" in status
    did_heavy_work = any(x in la for x in ("build", "construct", "chop", "mine", "haul", "forge", "hunt", "farm_heavy", "harvest"))
    did_light_work = (not did_heavy_work) and any(x in la for x in ("work", "tend", "clean", "shop", "trade", "teach", "cook_easy"))
    did_construction = "build" in la or "construct" in la or "carpentry" in la
    had_treatment = "treat" in la or "heal" in la or "medicine" in status
    return {
        "did_eat": did_eat,
        "did_drink": did_drink,
        "did_sleep": did_sleep,
        "did_rest": did_rest,
        "did_heavy_work": did_heavy_work,
        "did_light_work": did_light_work,
        "did_construction": did_construction,
        "had_treatment": had_treatment,
    }


def _is_outside_from_location(location: Any) -> bool:
    loc = str(location or "").lower()
    if not loc:
        return False
    if any(x in loc for x in ("house_", "home", "tavern", "shop", "hall", "temple", "hut", "cottage", "room", "inside", "shelter", "clinic", "hospital", "well_", "kitchen")):
        return False
    return True


def apply(context: Any) -> TransitionProposal:
    info = _extract_context(context)
    state: Mapping[str, Any] = info.get("state") or {}
    tick = int(info.get("tick_number") or 0)

    entities = state.get("entities", {}) if isinstance(state, Mapping) else {}
    weather_temp, weather_state = _weather_from_state(state)

    entity_patches: dict[str, Any] = {}
    health_states_patch: dict[str, Any] = {}
    all_events: list[dict[str, Any]] = []

    for entity_id_str, entity_data in sorted(entities.items()):
        ed = entity_data if isinstance(entity_data, Mapping) else {}
        if str(ed.get("type")) != "human":
            continue

        # Extract entity context
        components = dict(ed.get("components", {}))
        metadata = dict(ed.get("metadata", {}))
        transform = dict(components.get("TransformComponent", {}))
        location = transform.get("room")

        # Get action flags
        action_flags = _action_flags_from_entity_metadata(metadata)
        is_outside = _is_outside_from_location(location)

        # Read current health state
        prev_hs = _read_health_state(state, entity_id_str)

        # Evaluate health tick with original logic
        new_hs, events = evaluate_villager_health_tick(
            previous=prev_hs,
            weather_temperature_c=weather_temp,
            weather_state_short=weather_state,
            is_outside=is_outside,
            did_sleep=action_flags.get("did_sleep", False),
            did_rest=action_flags.get("did_rest", False),
            did_eat=action_flags.get("did_eat", False),
            did_drink=action_flags.get("did_drink", False),
            did_heavy_work=action_flags.get("did_heavy_work", False),
            did_light_work=action_flags.get("did_light_work", False),
            did_construction=action_flags.get("did_construction", False),
            tick_number=tick,
        )

        # Update patches
        health_states_patch[entity_id_str] = new_hs.to_dict()
        entity_patches[entity_id_str] = {
            "components": {
                "HealthComponent": {
                    "health_state": new_hs.to_dict(),
                    "component_type": "HealthComponent",
                }
            }
        }
        all_events.extend(event.to_dict() for event in events)

    if health_states_patch:
        health_patch = {"health_states": health_states_patch}
    else:
        health_patch = {}

    patch = {"health": health_patch, "entity_health_components": entity_patches}

    metadata = {"domain": "health", "events": all_events}
    description = f"health domain tick: {len(health_states_patch)} humans"

    return _make_proposal(info, patch, metadata, description)