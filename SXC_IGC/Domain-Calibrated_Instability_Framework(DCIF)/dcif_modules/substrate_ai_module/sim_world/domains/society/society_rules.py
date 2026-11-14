from __future__ import annotations

from typing import Any, Iterable, Mapping

from .society_models import (
    SOCIETY_METRIC_MIN,
    SOCIETY_METRIC_MAX,
    DEFAULT_PROSPERITY,
    DEFAULT_STABILITY,
    DEFAULT_MORALE,
    EMERGENCY_THRESHOLD,
    FOOD_CRISIS_RESERVE_PER_PERSON,
    WOOD_RESERVE_MIN_PER_HOUSEHOLD,
    EMERGENCY_TYPES,
    PROJECT_TYPES,
    CELEBRATION_TYPES,
    LEADERSHIP_ROLES,
    VillageState,
    Household,
    CommunalProject,
    ActiveCelebration,
    ActiveEmergency,
    Leadership,
    LaborAllocation,
    clamp,
    deterministic_hash,
    make_project_id,
    make_celebration_id,
    make_emergency_id,
)

from .society_events import (
    VillageMeetingHeld,
    LeaderAssigned,
    HarvestFestivalStarted,
    HarvestFestivalEnded,
    EmergencyDeclared,
    EmergencyResolved,
    VillageProspered,
    VillageDeclined,
    FoodCrisisStarted,
    FoodCrisisResolved,
    PublicProjectStarted,
    PublicProjectCompleted,
    MoraleChanged,
    ProsperityChanged,
    StabilityChanged,
    PopulationChanged,
    CelebrationStarted,
    CelebrationEnded,
)

SOCIETY_EVENT = (
    VillageMeetingHeld,
    LeaderAssigned,
    HarvestFestivalStarted,
    HarvestFestivalEnded,
    EmergencyDeclared,
    EmergencyResolved,
    VillageProspered,
    VillageDeclined,
    FoodCrisisStarted,
    FoodCrisisResolved,
    PublicProjectStarted,
    PublicProjectCompleted,
    MoraleChanged,
    ProsperityChanged,
    StabilityChanged,
    PopulationChanged,
    CelebrationStarted,
    CelebrationEnded,
)

EVENT_TOLERANCE: float = 1e-5


def _dict_get(d: Any, key: str, default: Any = None) -> Any:
    if d is None:
        return default
    if isinstance(d, Mapping):
        return d.get(key, default)
    if hasattr(d, key):
        return getattr(d, key, default)
    return default


def _float(d: Any, key: str, default: float = 0.0) -> float:
    try:
        return float(_dict_get(d, key, default) or default)
    except Exception:
        return float(default)


def _int(d: Any, key: str, default: int = 0) -> int:
    try:
        return int(_dict_get(d, key, default) or default)
    except Exception:
        return int(default)


def _as_tuple(d: Any, key: str) -> tuple[Any, ...]:
    v = _dict_get(d, key, ())
    if v is None:
        return tuple()
    try:
        if isinstance(v, (str, bytes)):
            return (str(v),)
        return tuple(v)
    except Exception:
        return tuple()


def derive_population_from_entities(entities: Iterable[Any]) -> tuple[int, int]:
    alive_count = 0
    dead_count = 0
    for e in entities or ():
        is_human = _dict_get(e, "is_human", False) or _dict_get(e, "entity_kind") in ("human", "villager", "person")
        if not is_human:
            continue
        alive = _dict_get(e, "alive", True)
        if alive:
            alive_count += 1
        else:
            dead_count += 1
    return alive_count, dead_count


def derive_workforce_from_entities(entities: Iterable[Any]) -> tuple[int, tuple[tuple[str, int], ...]]:
    occ_counter: dict[str, int] = {}
    workforce = 0
    for e in entities or ():
        is_human = _dict_get(e, "is_human", False) or _dict_get(e, "entity_kind") in ("human", "villager", "person")
        if not is_human:
            continue
        if not _dict_get(e, "alive", True):
            continue
        occupation = str(_dict_get(e, "occupation", "") or "").strip()
        if occupation:
            occ_counter[occupation] = occ_counter.get(occupation, 0) + 1
        workforce += 1
    return workforce, tuple((k, v) for k, v in sorted(occ_counter.items()))


def compute_prosperity_components(
    *,
    population: int,
    food_reserve: float,
    wood_reserve: float,
    avg_health: float = 0.7,
    avg_energy: float = 0.7,
    avg_relationship: float = 0.5,
    production_value: float = 0.0,
    harvest_value: float = 0.0,
    trade_volume: float = 0.0,
    completed_projects_count: int = 0,
    festival_days_count: int = 0,
    leadership_effectiveness: float = 0.7,
    weather_resilience: float = 0.7,
    learning_skill_avg: float = 0.5,
    emergency_level: float = 0.0,
    stability: float = 0.7,
    morale: float = 0.6,
) -> tuple[float, tuple[str, ...]]:
    factors: list[str] = []
    food_per_cap = food_reserve / float(max(1, population)) / max(1.0, FOOD_CRISIS_RESERVE_PER_PERSON * 4.0)
    food_score = clamp(food_per_cap)
    if food_score >= 0.75:
        factors.append("food_abundance")
    elif food_score < 0.3:
        factors.append("food_scarcity")

    wood_per_household = wood_reserve / max(1.0, 1.0) / max(1.0, WOOD_RESERVE_MIN_PER_HOUSEHOLD * 5.0)
    wood_score = clamp(wood_per_household)
    if wood_score >= 0.7:
        factors.append("wood_sufficient")

    health_score = clamp(avg_health)
    energy_score = clamp(avg_energy)
    rel_score = clamp(avg_relationship)
    skill_score = clamp(learning_skill_avg)
    weather_score = clamp(weather_resilience)

    production_index = clamp(min(1.0, production_value / max(1.0, float(max(1, population) * 10.0))))
    harvest_index = clamp(min(1.0, harvest_value / max(1.0, float(max(1, population) * 8.0))))
    trade_index = clamp(min(1.0, trade_volume / max(1.0, float(max(1, population) * 6.0))))

    festival_idx = clamp(min(1.0, festival_days_count / max(60, population * 3)))
    project_idx = clamp(min(1.0, completed_projects_count / max(5, population)))

    emergency_penalty = clamp(emergency_level) * 0.6

    components = [
        (food_score, 0.14),
        (wood_score, 0.06),
        (health_score, 0.15),
        (energy_score, 0.08),
        (rel_score, 0.10),
        (skill_score, 0.08),
        (weather_score, 0.07),
        (production_index, 0.07),
        (harvest_index, 0.08),
        (trade_index, 0.05),
        (festival_idx, 0.04),
        (project_idx, 0.04),
        (clamp(leadership_effectiveness), 0.04),
    ]
    base = sum(c * w for c, w in components)
    base -= emergency_penalty

    stability_factor = clamp(stability)
    morale_factor = clamp(morale)
    composite = base * (0.65 + 0.18 * stability_factor + 0.17 * morale_factor)
    score = clamp(composite)

    if health_score >= 0.85:
        factors.append("healthy_population")
    if production_index >= 0.6:
        factors.append("strong_production")
    if harvest_index >= 0.6:
        factors.append("good_harvest")
    if emergency_level > 0.5:
        factors.append("emergency_pressure")

    return score, tuple(factors)


def compute_stability_components(
    *,
    avg_trust: float = 0.6,
    avg_relationship: float = 0.5,
    avg_conflict: float = 0.0,
    resource_shortage_severity: float = 0.0,
    leadership_effectiveness: float = 0.7,
    recent_deaths: int = 0,
    active_emergencies_count: int = 0,
    resolved_emergencies_count: int = 0,
    completed_projects_count: int = 0,
    festival_days_count: int = 0,
    population: int = 0,
) -> tuple[float, tuple[str, ...]]:
    causes: list[str] = []
    trust_score = clamp(avg_trust)
    rel_score = clamp(avg_relationship)
    conflict_score = clamp(avg_conflict)
    shortage = clamp(resource_shortage_severity)
    leadership = clamp(leadership_effectiveness)

    death_penalty = clamp(recent_deaths / max(1.0, float(max(1, population) * 3.0)))
    active_emer_penalty = clamp(active_emergencies_count / max(3.0, float(max(1, population)) * 0.5))
    resolved_emer_bonus = clamp(resolved_emergencies_count / max(8, population)) * 0.15
    project_bonus = clamp(completed_projects_count / max(5, population)) * 0.10
    festival_bonus = clamp(festival_days_count / max(30, population * 2)) * 0.08

    base = (
        trust_score * 0.28
        + rel_score * 0.18
        + (1.0 - conflict_score) * 0.16
        + (1.0 - shortage) * 0.14
        + leadership * 0.20
    ) * 0.92
    total = base - death_penalty * 0.22 - active_emer_penalty * 0.14
    total += resolved_emer_bonus + project_bonus + festival_bonus

    if avg_conflict > 0.5:
        causes.append("high_conflict")
    if resource_shortage_severity > 0.5:
        causes.append("resource_shortage")
    if recent_deaths > 0:
        causes.append("recent_deaths")
    if active_emergencies_count > 0:
        causes.append("active_emergencies")
    if resolved_emergencies_count > 0 and trust_score > 0.6:
        causes.append("successful_recovery")
    if festival_days_count > 0:
        causes.append("festival_cohesion")
    if leadership > 0.7:
        causes.append("effective_leadership")

    return clamp(total), tuple(causes)


def compute_morale_components(
    *,
    recent_harvest_success: float = 0.0,
    festival_days_count: int = 0,
    recent_deaths_count: int = 0,
    avg_conflict: float = 0.0,
    avg_hunger_pressure: float = 0.0,
    avg_thirst_pressure: float = 0.0,
    avg_illness_pressure: float = 0.0,
    shared_achievement_value: float = 0.0,
    leadership_effectiveness: float = 0.7,
    avg_relationship: float = 0.5,
    prosperity: float = 0.6,
    stability: float = 0.7,
    emergency_level: float = 0.0,
    population: int = 0,
) -> tuple[float, tuple[str, ...]]:
    causes: list[str] = []

    harvest = clamp(recent_harvest_success)
    festival = clamp(festival_days_count / max(20, population * 2))
    deaths_penalty = clamp(recent_deaths_count / max(2.0, float(max(1, population) * 2.0)))
    conflict_penalty = clamp(avg_conflict) * 0.8
    hunger_penalty = clamp(avg_hunger_pressure)
    thirst_penalty = clamp(avg_thirst_pressure)
    illness_penalty = clamp(avg_illness_pressure)
    achievement = clamp(shared_achievement_value)
    leadership = clamp(leadership_effectiveness)
    rel_score = clamp(avg_relationship)
    prosper = clamp(prosperity)
    stable = clamp(stability)
    emer_penalty = clamp(emergency_level) * 0.4

    base = (
        harvest * 0.18
        + festival * 0.14
        + achievement * 0.10
        + leadership * 0.10
        + rel_score * 0.10
        + prosper * 0.16
        + stable * 0.14
    )
    total = (
        base
        - deaths_penalty * 0.22
        - conflict_penalty * 0.18
        - hunger_penalty * 0.14
        - thirst_penalty * 0.10
        - illness_penalty * 0.12
        - emer_penalty * 0.20
    )

    if harvest > 0.6:
        causes.append("good_harvest")
    if festival_days_count > 0:
        causes.append("celebration")
    if recent_deaths_count > 0:
        causes.append("grief")
    if hunger_penalty > 0.5:
        causes.append("hunger_pressure")
    if avg_illness_pressure > 0.4:
        causes.append("illness_strain")
    if leadership > 0.75 and stable > 0.6:
        causes.append("community_pride")
    if shared_achievement_value > 0.5:
        causes.append("shared_achievement")

    return clamp(total), tuple(causes)


def derive_resource_shortage(
    *,
    food_reserve: float,
    wood_reserve: float,
    population: int,
    households_count: int = 0,
    water_reserve: float | None = None,
) -> float:
    n = max(1, population)
    hh = max(1, households_count or max(1, population // 3))
    food_shortfall = max(0.0, 1.0 - clamp(food_reserve / max(1.0, FOOD_CRISIS_RESERVE_PER_PERSON * 3.0 * n)))
    wood_shortfall = max(0.0, 1.0 - clamp(wood_reserve / max(1.0, WOOD_RESERVE_MIN_PER_HOUSEHOLD * 3.0 * hh)))
    w = 0.55 if (water_reserve is None) else max(0.0, 1.0 - clamp(float(water_reserve) / max(1.0, 5.0 * n)))
    shortage = food_shortfall * 0.55 + wood_shortfall * 0.28 + w * 0.17
    return clamp(shortage)


def derive_emergency_level(
    *,
    resource_shortage_severity: float,
    active_emergencies_count: int,
    avg_health: float,
    weather_severity: float = 0.0,
    workforce_shortage: float = 0.0,
    conflict_severity: float = 0.0,
) -> float:
    h_pressure = clamp(1.0 - clamp(avg_health))
    w_pressure = clamp(weather_severity)
    wf_pressure = clamp(workforce_shortage)
    c_pressure = clamp(conflict_severity)
    em = clamp(active_emergencies_count) * 0.18
    s = (
        clamp(resource_shortage_severity) * 0.32
        + h_pressure * 0.22
        + w_pressure * 0.18
        + wf_pressure * 0.10
        + c_pressure * 0.08
        + em
    )
    return clamp(s)


def evaluate_emergencies(
    *,
    village_id: str,
    tick_number: int,
    previous_active: Mapping[str, ActiveEmergency],
    resource_shortage_severity: float,
    avg_health: float,
    food_reserve: float,
    population: int,
    weather_state: Mapping[str, Any] | None = None,
    workforce: int = 0,
    workforce_required_ratio: float = 0.8,
    conflict_severity: float = 0.0,
    avg_trust: float = 0.6,
) -> tuple[tuple[str, ...], dict[str, ActiveEmergency], tuple[Any, ...]]:
    new_active: dict[str, ActiveEmergency] = {}
    for eid, em in (previous_active or {}).items():
        if em.resolved:
            continue
        new_active[str(eid)] = em

    events: list[Any] = []

    # Food crisis
    food_crisis_eid = make_emergency_id(village_id, "FoodCrisis")
    food_required = float(max(1, population)) * FOOD_CRISIS_RESERVE_PER_PERSON
    if food_reserve < food_required * 0.5 and resource_shortage_severity > 0.45:
        if food_crisis_eid not in new_active:
            severity = clamp(1.0 - food_reserve / max(0.0001, food_required))
            events.append(FoodCrisisStarted.create(
                village_id=village_id,
                tick_number=tick_number,
                reserve_shortfall=max(0.0, food_required - food_reserve),
                estimated_days_remaining=0.0 if food_reserve <= 0 else food_reserve / max(0.0001, float(max(1, population)) * 0.5),
            ))
            em_new = ActiveEmergency(
                emergency_id=food_crisis_eid,
                emergency_type="FoodCrisis",
                village_id=village_id,
                severity=severity,
                declared_tick=tick_number,
            )
            new_active[food_crisis_eid] = em_new
            events.append(EmergencyDeclared.create(
                village_id=village_id,
                tick_number=tick_number,
                emergency_id=food_crisis_eid,
                emergency_type="FoodCrisis",
                severity=severity,
            ))
    else:
        if food_crisis_eid in new_active:
            old = new_active[food_crisis_eid]
            events.append(FoodCrisisResolved.create(
                village_id=village_id,
                tick_number=tick_number,
                recovery_food_reserve=food_reserve,
                duration_ticks=max(0, tick_number - old.declared_tick),
            ))
            events.append(EmergencyResolved.create(
                village_id=village_id,
                tick_number=tick_number,
                emergency_id=food_crisis_eid,
                emergency_type="FoodCrisis",
                duration_ticks=max(0, tick_number - old.declared_tick),
            ))
            del new_active[food_crisis_eid]

    # Disease outbreak
    disease_eid = make_emergency_id(village_id, "DiseaseOutbreak")
    if avg_health < 0.5 and population > 3:
        if disease_eid not in new_active:
            severity = clamp(1.0 - avg_health)
            em_new = ActiveEmergency(
                emergency_id=disease_eid,
                emergency_type="DiseaseOutbreak",
                village_id=village_id,
                severity=severity,
                declared_tick=tick_number,
            )
            new_active[disease_eid] = em_new
            events.append(EmergencyDeclared.create(
                village_id=village_id,
                tick_number=tick_number,
                emergency_id=disease_eid,
                emergency_type="DiseaseOutbreak",
                severity=severity,
            ))
    else:
        if disease_eid in new_active:
            old = new_active[disease_eid]
            events.append(EmergencyResolved.create(
                village_id=village_id,
                tick_number=tick_number,
                emergency_id=disease_eid,
                emergency_type="DiseaseOutbreak",
                duration_ticks=max(0, tick_number - old.declared_tick),
            ))
            del new_active[disease_eid]

    # Flood / Storm
    weather = weather_state or {}
    weather_type = str(_dict_get(weather, "weather_type", "") or _dict_get(weather, "condition", "") or "").strip().lower()
    severity_w = _float(weather, "severity", 0.0)
    temp_c = _float(weather, "temperature_c", 0.0)
    wind = _float(weather, "wind_speed", 0.0)
    rainfall = _float(weather, "rainfall", 0.0)

    flood_eid = make_emergency_id(village_id, "Flood")
    if rainfall > 20.0 or (severity_w > 0.7 and weather_type in {"rain", "storm", "thunderstorm"}):
        if flood_eid not in new_active:
            sev = clamp((rainfall - 20.0) / 20.0 + severity_w * 0.3)
            em_new = ActiveEmergency(
                emergency_id=flood_eid,
                emergency_type="Flood",
                village_id=village_id,
                severity=sev,
                declared_tick=tick_number,
            )
            new_active[flood_eid] = em_new
            events.append(EmergencyDeclared.create(
                village_id=village_id,
                tick_number=tick_number,
                emergency_id=flood_eid,
                emergency_type="Flood",
                severity=sev,
            ))
    else:
        if flood_eid in new_active:
            old = new_active[flood_eid]
            events.append(EmergencyResolved.create(
                village_id=village_id,
                tick_number=tick_number,
                emergency_id=flood_eid,
                emergency_type="Flood",
                duration_ticks=max(0, tick_number - old.declared_tick),
            ))
            del new_active[flood_eid]

    # Fire
    fire_eid = make_emergency_id(village_id, "Fire")
    fire_present = weather_type == "fire" or bool(_dict_get(weather, "fire_risk", False)) or (temp_c > 36.0 and wind > 8.0 and rainfall < 0.1 and deterministic_hash(f"{village_id}:fire:{tick_number}") % 50 == 0)
    if fire_present:
        if fire_eid not in new_active:
            sev = clamp((max(0.0, temp_c - 30.0) / 15.0) + clamp(wind / 15.0) + 0.3)
            em_new = ActiveEmergency(
                emergency_id=fire_eid,
                emergency_type="Fire",
                village_id=village_id,
                severity=sev,
                declared_tick=tick_number,
            )
            new_active[fire_eid] = em_new
            events.append(EmergencyDeclared.create(
                village_id=village_id,
                tick_number=tick_number,
                emergency_id=fire_eid,
                emergency_type="Fire",
                severity=sev,
            ))
    else:
        if fire_eid in new_active:
            old = new_active[fire_eid]
            events.append(EmergencyResolved.create(
                village_id=village_id,
                tick_number=tick_number,
                emergency_id=fire_eid,
                emergency_type="Fire",
                duration_ticks=max(0, tick_number - old.declared_tick),
            ))
            del new_active[fire_eid]

    # Resource shortage
    shortage_eid = make_emergency_id(village_id, "ResourceShortage")
    if resource_shortage_severity > 0.7:
        if shortage_eid not in new_active and food_crisis_eid not in new_active:
            sev = clamp(resource_shortage_severity)
            em_new = ActiveEmergency(
                emergency_id=shortage_eid,
                emergency_type="ResourceShortage",
                village_id=village_id,
                severity=sev,
                declared_tick=tick_number,
            )
            new_active[shortage_eid] = em_new
            events.append(EmergencyDeclared.create(
                village_id=village_id,
                tick_number=tick_number,
                emergency_id=shortage_eid,
                emergency_type="ResourceShortage",
                severity=sev,
            ))
    else:
        if shortage_eid in new_active:
            old = new_active[shortage_eid]
            events.append(EmergencyResolved.create(
                village_id=village_id,
                tick_number=tick_number,
                emergency_id=shortage_eid,
                emergency_type="ResourceShortage",
                duration_ticks=max(0, tick_number - old.declared_tick),
            ))
            del new_active[shortage_eid]

    # Workforce shortage
    wf_eid = make_emergency_id(village_id, "WorkforceShortage")
    wf_required = max(1, int(float(max(1, population)) * workforce_required_ratio))
    if workforce > 0 and workforce < max(1, wf_required // 2) and population > 4:
        if wf_eid not in new_active:
            sev = clamp(1.0 - (workforce / max(1, wf_required)))
            em_new = ActiveEmergency(
                emergency_id=wf_eid,
                emergency_type="WorkforceShortage",
                village_id=village_id,
                severity=sev,
                declared_tick=tick_number,
            )
            new_active[wf_eid] = em_new
            events.append(EmergencyDeclared.create(
                village_id=village_id,
                tick_number=tick_number,
                emergency_id=wf_eid,
                emergency_type="WorkforceShortage",
                severity=sev,
            ))
    else:
        if wf_eid in new_active:
            old = new_active[wf_eid]
            events.append(EmergencyResolved.create(
                village_id=village_id,
                tick_number=tick_number,
                emergency_id=wf_eid,
                emergency_type="WorkforceShortage",
                duration_ticks=max(0, tick_number - old.declared_tick),
            ))
            del new_active[wf_eid]

    # Civil unrest
    civil_eid = make_emergency_id(village_id, "CivilUnrest")
    if conflict_severity > 0.7 and avg_trust < 0.35 and population > 2:
        if civil_eid not in new_active:
            sev = clamp(conflict_severity * 0.6 + (1.0 - avg_trust) * 0.4)
            em_new = ActiveEmergency(
                emergency_id=civil_eid,
                emergency_type="CivilUnrest",
                village_id=village_id,
                severity=sev,
                declared_tick=tick_number,
            )
            new_active[civil_eid] = em_new
            events.append(EmergencyDeclared.create(
                village_id=village_id,
                tick_number=tick_number,
                emergency_id=civil_eid,
                emergency_type="CivilUnrest",
                severity=sev,
            ))
    else:
        if civil_eid in new_active:
            old = new_active[civil_eid]
            events.append(EmergencyResolved.create(
                village_id=village_id,
                tick_number=tick_number,
                emergency_id=civil_eid,
                emergency_type="CivilUnrest",
                duration_ticks=max(0, tick_number - old.declared_tick),
            ))
            del new_active[civil_eid]

    active_ids = tuple(sorted(new_active.keys()))
    return active_ids, new_active, tuple(events)


def evaluate_communal_projects(
    *,
    village_id: str,
    tick_number: int,
    previous_projects: Mapping[str, CommunalProject],
    leadership: Leadership | None,
    emergency_level: float,
    avg_harvest_readiness: float = 0.0,
    roads_damaged: bool = False,
    bridges_damaged: bool = False,
    storage_disorganized: bool = False,
    fire_risk_active: bool = False,
    construction_active: bool = False,
    available_workers: tuple[str, ...] = tuple(),
    harvest_completed: bool = False,
    prosperity: float = 0.6,
) -> tuple[tuple[str, ...], dict[str, CommunalProject], tuple[Any, ...], int, int]:
    new_projects: dict[str, CommunalProject] = {}
    completed_increment = 0
    started_increment = 0
    events: list[Any] = []

    for pid, p in (previous_projects or {}).items():
        new_projects[str(pid)] = p

    completed_ids: list[str] = []
    for pid, p in list(new_projects.items()):
        if not p.active:
            continue
        workers_increment = 0
        if p.required_workers > 0 and len(p.assigned_workers) >= max(1, p.required_workers // 2):
            base_increment = 1.0 / max(1.0, float(p.required_ticks))
            worker_ratio = clamp(len(p.assigned_workers) / max(1.0, float(p.required_workers)))
            workers_increment = base_increment * (0.5 + worker_ratio)
        elif p.required_workers <= 0:
            workers_increment = 1.0 / max(1.0, float(p.required_ticks))
        new_progress = clamp(p.progress + workers_increment)
        completed_now = new_progress >= 1.0
        if completed_now:
            new_progress = 1.0
            completed_ids.append(pid)
            completed_increment += 1
            events.append(PublicProjectCompleted.create(
                village_id=village_id,
                tick_number=tick_number,
                project_id=pid,
                project_type=p.project_type,
                total_workers_involved=len(p.assigned_workers),
                duration_ticks=max(1, tick_number - p.start_tick),
            ))
        new_projects[pid] = CommunalProject(
            project_id=p.project_id,
            project_type=p.project_type,
            village_id=p.village_id,
            name=p.name,
            assigned_workers=p.assigned_workers,
            required_workers=p.required_workers,
            required_ticks=p.required_ticks,
            progress=new_progress,
            start_tick=p.start_tick,
            completed_tick=tick_number if completed_now else p.completed_tick,
            active=False if completed_now else p.active,
            material_cost=p.material_cost,
            reward=p.reward,
        )

    # Attempt new project starts
    def maybe_start(p_type: str, name: str, required_ticks: int, required_workers: int, should: bool) -> None:
        nonlocal started_increment
        if not should:
            return
        # Avoid duplicate active projects of the same type
        for p in new_projects.values():
            if p.active and p.project_type == p_type:
                return
        pid = make_project_id(village_id, p_type, tick_number)
        if pid in new_projects:
            return
        assigned = available_workers[: min(len(available_workers), max(1, required_workers))]
        new_p = CommunalProject(
            project_id=pid,
            project_type=p_type,
            village_id=village_id,
            name=name,
            assigned_workers=tuple(assigned),
            required_workers=required_workers,
            required_ticks=required_ticks,
            progress=0.0,
            start_tick=tick_number,
            completed_tick=0,
            active=True,
        )
        new_projects[pid] = new_p
        started_increment += 1
        events.append(PublicProjectStarted.create(
            village_id=village_id,
            tick_number=tick_number,
            project_id=pid,
            project_type=p_type,
            project_name=name,
            assigned_workers=tuple(assigned),
        ))

    maybe_start("Harvest", "Communal Harvest", required_ticks=5, required_workers=3, should=(avg_harvest_readiness > 0.8 and not harvest_completed))
    maybe_start("RoadRepair", "Road Repairs", required_ticks=6, required_workers=2, should=roads_damaged)
    maybe_start("BridgeRepair", "Bridge Repair", required_ticks=10, required_workers=3, should=bridges_damaged)
    maybe_start("StorageOrganization", "Storage Tidy", required_ticks=4, required_workers=2, should=storage_disorganized)
    maybe_start("FireResponse", "Fire Watch", required_ticks=3, required_workers=3, should=fire_risk_active)
    maybe_start("ConstructionSupport", "Construction Support Crew", required_ticks=8, required_workers=3, should=construction_active and prosperity > 0.45)
    maybe_start("WellDigging", "Well Digging", required_ticks=12, required_workers=3, should=(emergency_level < 0.3 and prosperity > 0.7))

    active_ids = tuple(sorted(pid for pid, p in new_projects.items() if p.active))
    return active_ids, new_projects, tuple(events), started_increment, completed_increment


def evaluate_celebrations(
    *,
    village_id: str,
    tick_number: int,
    previous_celebrations: Mapping[str, ActiveCelebration],
    emergency_level: float,
    prosperity: float,
    morale: float,
    harvest_surplus: float = 0.0,
    population: int = 0,
    leadership: Leadership | None = None,
    marriages_count_recent: int = 0,
    midseason_tick: bool = False,
    founding_day_tick: bool = False,
) -> tuple[tuple[str, ...], dict[str, ActiveCelebration], tuple[Any, ...], int]:
    new_celebrations: dict[str, ActiveCelebration] = {}
    festival_days_increment = 0
    events: list[Any] = []

    for cid, c in (previous_celebrations or {}).items():
        duration = int(tick_number) - int(c.start_tick)
        if duration < int(c.duration_ticks):
            new_celebrations[str(cid)] = c
            festival_days_increment += 1
        else:
            if c.celebration_type == "HarvestFestival":
                events.append(HarvestFestivalEnded.create(
                    village_id=village_id,
                    tick_number=tick_number,
                    celebration_id=cid,
                    total_participants=len(c.participants),
                    harvest_yield=float(harvest_surplus),
                ))
            events.append(CelebrationEnded.create(
                village_id=village_id,
                tick_number=tick_number,
                celebration_id=cid,
                celebration_type=c.celebration_type,
                total_participants=len(c.participants),
                duration_ticks=max(1, duration),
            ))

    def try_start(ctype: str, name: str, duration: int, should_start: bool, organizer_extra: str = "") -> None:
        nonlocal festival_days_increment
        if not should_start:
            return
        for c in new_celebrations.values():
            if c.celebration_type == ctype:
                return
        cid = make_celebration_id(village_id, ctype, tick_number)
        if cid in new_celebrations:
            return
        participants = tuple()
        organizer = str(leadership.leader_entity_id) if leadership and leadership.leader_entity_id else str(organizer_extra)
        celeb = ActiveCelebration(
            celebration_id=cid,
            celebration_type=ctype,
            village_id=village_id,
            name=name,
            start_tick=tick_number,
            duration_ticks=duration,
            participants=participants,
            organizer=organizer,
        )
        new_celebrations[cid] = celeb
        festival_days_increment += 1
        events.append(CelebrationStarted.create(
            village_id=village_id,
            tick_number=tick_number,
            celebration_id=cid,
            celebration_type=ctype,
            organizer=organizer,
            participants=participants,
        ))
        if ctype == "HarvestFestival":
            events.append(HarvestFestivalStarted.create(
                village_id=village_id,
                tick_number=tick_number,
                celebration_id=cid,
                organizer=organizer,
                participants=participants,
            ))

    harvest_ok = emergency_level < 0.4 and prosperity > 0.55 and harvest_surplus > 0.0
    try_start("HarvestFestival", "Harvest Home", 4, harvest_ok)
    try_start("WeddingFeast", "Wedding Celebration", 2, marriages_count_recent > 0 and emergency_level < 0.6)
    try_start("Midsummer", "Midsummer Day", 3, midseason_tick and emergency_level < 0.5 and morale > 0.45)
    try_start("Midwinter", "Midwinter Festival", 4, founding_day_tick and emergency_level < 0.5)
    try_start("SeasonalFestival", "Seasonal Fare", 3, emergency_level < 0.25 and prosperity > 0.8 and morale > 0.7 and population > 2)

    active_ids = tuple(sorted(new_celebrations.keys()))
    return active_ids, new_celebrations, tuple(events), festival_days_increment


def evaluate_leadership(
    *,
    village_id: str,
    tick_number: int,
    previous_leadership: Leadership | None,
    population: int,
    prosperity: float,
    stability: float,
    morale: float,
    emergency_level: float,
    available_leader_ids: tuple[str, ...] = tuple(),
    meeting_frequency_ticks: int = 30,
    leader_entity_seniority: Mapping[str, int] | None = None,
) -> tuple[Leadership, tuple[Any, ...]]:
    events: list[Any] = []
    prev = previous_leadership or Leadership(village_id=village_id, leadership_effectiveness=0.5)
    leader_entity_id = prev.leader_entity_id
    leader_role = prev.leader_role
    deputy = prev.deputy_entity_id
    councillors = tuple(prev.councillors)
    appointed = prev.appointed_tick
    last_meeting = prev.last_meeting_tick
    meetings = int(prev.meeting_count)

    if not leader_entity_id and available_leader_ids:
        seniority = leader_entity_seniority or {}
        ranked = sorted(available_leader_ids, key=lambda eid: (-int(seniority.get(eid, 0)), str(eid)))
        leader_entity_id = ranked[0]
        leader_role = "Elder"
        if len(ranked) > 1:
            deputy = ranked[1]
        if len(ranked) > 2:
            councillors = tuple(ranked[2: min(len(ranked), 5)])
        appointed = tick_number
        events.append(LeaderAssigned.create(
            village_id=village_id,
            tick_number=tick_number,
            leader_entity_id=leader_entity_id,
            leader_role=leader_role,
        ))

    time_since_meeting = max(0, tick_number - last_meeting)
    held_meeting_now = False
    emergency_override = emergency_level > EMERGENCY_THRESHOLD
    if time_since_meeting >= max(1, meeting_frequency_ticks) or emergency_override:
        held_meeting_now = True
        last_meeting = tick_number
        meetings += 1
        agenda: list[str] = []
        decisions: list[str] = []
        if emergency_level > 0.5:
            agenda.append("emergency_response")
            decisions.append("responders_deployed")
        if prosperity < 0.4:
            agenda.append("economic_priorities")
            decisions.append("increase_production")
        if stability < 0.5:
            agenda.append("community_disputes")
            decisions.append("mediate_conflicts")
        if morale < 0.4:
            agenda.append("morale_initiative")
            decisions.append("schedule_celebration")
        if not agenda:
            agenda.append("council_report")
            decisions.append("maintain_course")
        events.append(VillageMeetingHeld.create(
            village_id=village_id,
            tick_number=tick_number,
            attendees=tuple(sorted({leader_entity_id, deputy, *councillors})) if leader_entity_id else tuple(),
            agenda=",".join(agenda),
            decisions=tuple(decisions),
        ))

    out = (
        0.22 * clamp(prosperity)
        + 0.22 * clamp(stability)
        + 0.18 * clamp(morale)
        + 0.16 * (1.0 - clamp(emergency_level))
        + 0.10 * (1.0 if held_meeting_now else 0.0)
        + 0.12 * clamp(prev.leadership_effectiveness)
    )
    effectiveness = clamp(out)
    new_leadership = Leadership(
        village_id=village_id,
        leader_entity_id=str(leader_entity_id),
        leader_role=str(leader_role),
        deputy_entity_id=str(deputy),
        councillors=tuple(councillors),
        appointed_tick=int(appointed),
        leadership_effectiveness=float(effectiveness),
        last_meeting_tick=int(last_meeting),
        meeting_count=int(meetings),
    )
    return new_leadership, tuple(events)


def evaluate_village_tick(
    *,
    previous: VillageState,
    leadership: Leadership | None,
    tick_number: int,
    households: Mapping[str, Household] | None = None,
    active_projects_map: Mapping[str, CommunalProject] | None = None,
    active_celebrations_map: Mapping[str, ActiveCelebration] | None = None,
    active_emergencies_map: Mapping[str, ActiveEmergency] | None = None,
    population_new: int | None = None,
    workforce_new: int | None = None,
    occupations_new: tuple[tuple[str, int], ...] | None = None,
    entities: Iterable[Any] | None = None,
    avg_health: float | None = None,
    avg_energy: float | None = None,
    avg_relationship: float | None = None,
    avg_trust: float | None = None,
    avg_conflict: float | None = None,
    avg_hunger_pressure: float | None = None,
    avg_thirst_pressure: float | None = None,
    avg_illness_pressure: float | None = None,
    avg_skill: float | None = None,
    production_value: float = 0.0,
    harvest_value: float = 0.0,
    trade_volume: float = 0.0,
    weather_state: Mapping[str, Any] | None = None,
    food_reserve_new: float | None = None,
    wood_reserve_new: float | None = None,
    water_reserve: float | None = None,
    weather_resilience: float | None = None,
    recent_harvest_success: float | None = None,
    recent_deaths_count: int = 0,
    shared_achievement_value: float = 0.0,
    available_workers: tuple[str, ...] = tuple(),
    available_leader_ids: tuple[str, ...] = tuple(),
    roads_damaged: bool = False,
    bridges_damaged: bool = False,
    storage_disorganized: bool = False,
    fire_risk_active: bool = False,
    construction_active: bool = False,
    harvest_completed: bool = False,
    marriages_count_recent: int = 0,
    midseason_tick: bool = False,
    founding_day_tick: bool = False,
    leadership_meeting_frequency_ticks: int = 30,
    leader_entity_seniority: Mapping[str, int] | None = None,
    cumulative_harvest_delta: float = 0.0,
    cumulative_production_delta: float = 0.0,
    cumulative_trade_delta: float = 0.0,
    births_count_delta: int = 0,
    deaths_count_delta: int = 0,
    marriages_count_delta: int = 0,
) -> tuple[VillageState, Leadership, dict[str, Household], dict[str, CommunalProject], dict[str, ActiveCelebration], dict[str, ActiveEmergency], tuple[Any, ...]]:
    events: list[Any] = []
    prev_households = dict(households or {})
    prev_projects = dict(active_projects_map or {})
    prev_celebrations = dict(active_celebrations_map or {})
    prev_emergencies = dict(active_emergencies_map or {})

    population = int(population_new if population_new is not None else previous.population)
    workforce = int(workforce_new if workforce_new is not None else previous.workforce_size)
    occupations = tuple(occupations_new if occupations_new is not None else previous.occupations)
    food_reserve = float(food_reserve_new if food_reserve_new is not None else previous.food_reserve)
    wood_reserve = float(wood_reserve_new if wood_reserve_new is not None else previous.wood_reserve)

    avg_health_v = clamp(0.7 if avg_health is None else float(avg_health))
    avg_energy_v = clamp(0.7 if avg_energy is None else float(avg_energy))
    avg_rel_v = clamp(0.5 if avg_relationship is None else float(avg_relationship))
    avg_trust_v = clamp(0.6 if avg_trust is None else float(avg_trust))
    avg_conflict_v = clamp(0.0 if avg_conflict is None else float(avg_conflict))
    avg_hunger_v = clamp(0.0 if avg_hunger_pressure is None else float(avg_hunger_pressure))
    avg_thirst_v = clamp(0.0 if avg_thirst_pressure is None else float(avg_thirst_pressure))
    avg_illness_v = clamp(0.0 if avg_illness_pressure is None else float(avg_illness_pressure))
    avg_skill_v = clamp(0.5 if avg_skill is None else float(avg_skill))
    weather_resilience_v = clamp(0.7 if weather_resilience is None else float(weather_resilience))
    harvest_success_v = clamp(recent_harvest_success if recent_harvest_success is not None else (1.0 if harvest_value > 0 else 0.5))

    hh_count = max(1, len(prev_households))
    shortage_severity = derive_resource_shortage(
        food_reserve=food_reserve,
        wood_reserve=wood_reserve,
        population=population,
        households_count=hh_count,
        water_reserve=water_reserve,
    )

    weather_state_v = weather_state or {}
    severity_w = _float(weather_state_v, "severity", 0.0)
    temp_c = _float(weather_state_v, "temperature_c", 0.0)
    wind = _float(weather_state_v, "wind_speed", 0.0)
    rainfall = _float(weather_state_v, "rainfall", 0.0)
    weather_severity = clamp((severity_w + clamp(abs(temp_c - 20.0) / 30.0) + clamp(wind / 15.0) + clamp(rainfall / 50.0)) / 4.0)

    wf_required = max(1, int(float(max(1, population)) * 0.8))
    wf_shortage = clamp(1.0 - workforce / max(1.0, float(wf_required)))

    leadership_v, leader_events = evaluate_leadership(
        village_id=previous.village_id,
        tick_number=tick_number,
        previous_leadership=leadership,
        population=population,
        prosperity=previous.prosperity,
        stability=previous.stability,
        morale=previous.morale,
        emergency_level=previous.emergency_level,
        available_leader_ids=tuple(available_leader_ids),
        meeting_frequency_ticks=leadership_meeting_frequency_ticks,
        leader_entity_seniority=dict(leader_entity_seniority or {}),
    )
    events.extend(leader_events)

    # Preliminary prosperity/stability/morale estimates for project/celebration decision gates
    prosperity_pre, _ = compute_prosperity_components(
        population=population,
        food_reserve=food_reserve,
        wood_reserve=wood_reserve,
        avg_health=avg_health_v,
        avg_energy=avg_energy_v,
        avg_relationship=avg_rel_v,
        production_value=production_value,
        harvest_value=harvest_value,
        trade_volume=trade_volume,
        completed_projects_count=previous.completed_projects_count,
        festival_days_count=previous.festival_days_count,
        leadership_effectiveness=leadership_v.leadership_effectiveness,
        weather_resilience=weather_resilience_v,
        learning_skill_avg=avg_skill_v,
        emergency_level=previous.emergency_level,
        stability=previous.stability,
        morale=previous.morale,
    )
    stability_pre, _ = compute_stability_components(
        avg_trust=avg_trust_v,
        avg_relationship=avg_rel_v,
        avg_conflict=avg_conflict_v,
        resource_shortage_severity=shortage_severity,
        leadership_effectiveness=leadership_v.leadership_effectiveness,
        recent_deaths=recent_deaths_count + deaths_count_delta,
        active_emergencies_count=len(prev_emergencies),
        resolved_emergencies_count=previous.resolved_emergencies_count,
        completed_projects_count=previous.completed_projects_count,
        festival_days_count=previous.festival_days_count,
        population=population,
    )
    morale_pre, _ = compute_morale_components(
        recent_harvest_success=harvest_success_v,
        festival_days_count=previous.festival_days_count,
        recent_deaths_count=recent_deaths_count + deaths_count_delta,
        avg_conflict=avg_conflict_v,
        avg_hunger_pressure=avg_hunger_v,
        avg_thirst_pressure=avg_thirst_v,
        avg_illness_pressure=avg_illness_v,
        shared_achievement_value=shared_achievement_value,
        leadership_effectiveness=leadership_v.leadership_effectiveness,
        avg_relationship=avg_rel_v,
        prosperity=prosperity_pre,
        stability=stability_pre,
        emergency_level=previous.emergency_level,
        population=population,
    )

    active_emer_ids, new_emergencies_map, emer_events = evaluate_emergencies(
        village_id=previous.village_id,
        tick_number=tick_number,
        previous_active=prev_emergencies,
        resource_shortage_severity=shortage_severity,
        avg_health=avg_health_v,
        food_reserve=food_reserve,
        population=population,
        weather_state=weather_state_v,
        workforce=workforce,
        conflict_severity=avg_conflict_v,
        avg_trust=avg_trust_v,
    )
    events.extend(emer_events)
    resolved_increment = 0
    for eid in prev_emergencies:
        if eid not in new_emergencies_map:
            resolved_increment += 1

    active_emer_level = derive_emergency_level(
        resource_shortage_severity=shortage_severity,
        active_emergencies_count=len(new_emergencies_map),
        avg_health=avg_health_v,
        weather_severity=weather_severity,
        workforce_shortage=wf_shortage,
        conflict_severity=avg_conflict_v,
    )

    project_active_ids, new_projects_map, project_events, started_inc, completed_inc = evaluate_communal_projects(
        village_id=previous.village_id,
        tick_number=tick_number,
        previous_projects=prev_projects,
        leadership=leadership_v,
        emergency_level=active_emer_level,
        avg_harvest_readiness=harvest_success_v,
        roads_damaged=roads_damaged,
        bridges_damaged=bridges_damaged,
        storage_disorganized=storage_disorganized,
        fire_risk_active=fire_risk_active or bool(_dict_get(weather_state_v, "fire_risk", False)),
        construction_active=construction_active,
        available_workers=tuple(available_workers),
        harvest_completed=harvest_completed,
        prosperity=prosperity_pre,
    )
    events.extend(project_events)

    celeb_active_ids, new_celebrations_map, celeb_events, festival_days_inc = evaluate_celebrations(
        village_id=previous.village_id,
        tick_number=tick_number,
        previous_celebrations=prev_celebrations,
        emergency_level=active_emer_level,
        prosperity=prosperity_pre,
        morale=morale_pre,
        harvest_surplus=harvest_value,
        population=population,
        leadership=leadership_v,
        marriages_count_recent=marriages_count_recent + marriages_count_delta,
        midseason_tick=midseason_tick,
        founding_day_tick=founding_day_tick,
    )
    events.extend(celeb_events)

    # Now re-compute prosperity/stability/morale AFTER applying project/emergency/celebration state updates
    new_completed_projects = previous.completed_projects_count + completed_inc
    new_resolved_emer = previous.resolved_emergencies_count + resolved_increment
    new_festival_days = previous.festival_days_count + festival_days_inc

    prosperity_new, prosperity_factors = compute_prosperity_components(
        population=population,
        food_reserve=food_reserve,
        wood_reserve=wood_reserve,
        avg_health=avg_health_v,
        avg_energy=avg_energy_v,
        avg_relationship=avg_rel_v,
        production_value=production_value,
        harvest_value=harvest_value,
        trade_volume=trade_volume,
        completed_projects_count=new_completed_projects,
        festival_days_count=new_festival_days,
        leadership_effectiveness=leadership_v.leadership_effectiveness,
        weather_resilience=weather_resilience_v,
        learning_skill_avg=avg_skill_v,
        emergency_level=active_emer_level,
        stability=stability_pre,
        morale=morale_pre,
    )
    stability_new, stability_causes = compute_stability_components(
        avg_trust=avg_trust_v,
        avg_relationship=avg_rel_v,
        avg_conflict=avg_conflict_v,
        resource_shortage_severity=shortage_severity,
        leadership_effectiveness=leadership_v.leadership_effectiveness,
        recent_deaths=recent_deaths_count + deaths_count_delta,
        active_emergencies_count=len(new_emergencies_map),
        resolved_emergencies_count=new_resolved_emer,
        completed_projects_count=new_completed_projects,
        festival_days_count=new_festival_days,
        population=population,
    )
    morale_new, morale_causes = compute_morale_components(
        recent_harvest_success=harvest_success_v,
        festival_days_count=new_festival_days,
        recent_deaths_count=recent_deaths_count + deaths_count_delta,
        avg_conflict=avg_conflict_v,
        avg_hunger_pressure=avg_hunger_v,
        avg_thirst_pressure=avg_thirst_v,
        avg_illness_pressure=avg_illness_v,
        shared_achievement_value=shared_achievement_value,
        leadership_effectiveness=leadership_v.leadership_effectiveness,
        avg_relationship=avg_rel_v,
        prosperity=prosperity_new,
        stability=stability_new,
        emergency_level=active_emer_level,
        population=population,
    )

    # Metric delta events
    prosper_delta = prosperity_new - previous.prosperity
    if prosper_delta > EVENT_TOLERANCE:
        events.append(VillageProspered.create(
            village_id=previous.village_id,
            tick_number=tick_number,
            prosperity_delta=prosper_delta,
            new_prosperity=prosperity_new,
            contributing_factors=prosperity_factors,
        ))
    elif prosper_delta < -EVENT_TOLERANCE:
        events.append(VillageDeclined.create(
            village_id=previous.village_id,
            tick_number=tick_number,
            prosperity_delta=prosper_delta,
            new_prosperity=prosperity_new,
            contributing_factors=prosperity_factors,
        ))

    if abs(prosperity_new - previous.prosperity) > EVENT_TOLERANCE:
        events.append(ProsperityChanged.create(
            village_id=previous.village_id,
            tick_number=tick_number,
            old_prosperity=previous.prosperity,
            new_prosperity=prosperity_new,
        ))
    if abs(stability_new - previous.stability) > EVENT_TOLERANCE:
        events.append(StabilityChanged.create(
            village_id=previous.village_id,
            tick_number=tick_number,
            old_stability=previous.stability,
            new_stability=stability_new,
            causes=stability_causes,
        ))
    if abs(morale_new - previous.morale) > EVENT_TOLERANCE:
        events.append(MoraleChanged.create(
            village_id=previous.village_id,
            tick_number=tick_number,
            old_morale=previous.morale,
            new_morale=morale_new,
            causes=morale_causes,
        ))

    population_delta = int(population - previous.population)
    if population_delta != 0:
        reason = ""
        if deaths_count_delta > 0 and births_count_delta > 0:
            reason = "births_and_deaths"
        elif deaths_count_delta > 0:
            reason = "deaths"
        elif births_count_delta > 0:
            reason = "births"
        else:
            reason = "migration_or_correction"
        events.append(PopulationChanged.create(
            village_id=previous.village_id,
            tick_number=tick_number,
            old_population=previous.population,
            new_population=population,
            delta=population_delta,
            reason=reason,
        ))

    hh_ids = tuple(sorted(prev_households.keys()))
    labor_ids = tuple(previous.labor_allocations)

    new_state = VillageState(
        village_id=previous.village_id,
        village_name=previous.village_name,
        world_id=previous.world_id,
        population=population,
        workforce_size=workforce,
        food_reserve=food_reserve,
        wood_reserve=wood_reserve,
        emergency_level=active_emer_level,
        prosperity=prosperity_new,
        stability=stability_new,
        morale=morale_new,
        founded_tick=previous.founded_tick,
        last_updated_tick=tick_number,
        households=hh_ids,
        occupations=occupations,
        labor_allocations=labor_ids,
        active_projects=project_active_ids,
        completed_projects_count=new_completed_projects,
        active_celebrations=celeb_active_ids,
        active_emergencies=active_emer_ids,
        resolved_emergencies_count=new_resolved_emer,
        births_count=previous.births_count + max(0, births_count_delta),
        deaths_count=previous.deaths_count + max(0, deaths_count_delta),
        marriages_count=previous.marriages_count + max(0, marriages_count_delta),
        cumulative_harvest=max(0.0, previous.cumulative_harvest + cumulative_harvest_delta),
        cumulative_production_value=max(0.0, previous.cumulative_production_value + cumulative_production_delta),
        cumulative_trade_volume=max(0.0, previous.cumulative_trade_volume + cumulative_trade_delta),
        festival_days_count=new_festival_days,
        leadership=str(leadership_v.leader_entity_id),
    )

    return (
        new_state,
        leadership_v,
        prev_households,
        new_projects_map,
        new_celebrations_map,
        new_emergencies_map,
        tuple(events),
    )


def derive_society_goals(
    *,
    village: VillageState,
    leadership: Leadership | None,
    active_emergencies: Mapping[str, ActiveEmergency],
    tick_number: int,
) -> list[dict[str, Any]]:
    goals: list[dict[str, Any]] = []
    v = village
    n = max(1, v.population)
    hh = max(1, len(v.households))
    food_needed = float(n) * FOOD_CRISIS_RESERVE_PER_PERSON * 3.0
    wood_needed = float(hh) * WOOD_RESERVE_MIN_PER_HOUSEHOLD * 2.0

    em_ids = set(v.active_emergencies)
    food_crisis = any(
        em.emergency_type == "FoodCrisis"
        for em in (active_emergencies or {}).values()
        if str(getattr(em, "emergency_id", "")) in em_ids
    )
    flood_active = any(
        em.emergency_type == "Flood"
        for em in (active_emergencies or {}).values()
        if str(getattr(em, "emergency_id", "")) in em_ids
    )
    fire_active = any(
        em.emergency_type == "Fire"
        for em in (active_emergencies or {}).values()
        if str(getattr(em, "emergency_id", "")) in em_ids
    )
    disease_active = any(
        em.emergency_type == "DiseaseOutbreak"
        for em in (active_emergencies or {}).values()
        if str(getattr(em, "emergency_id", "")) in em_ids
    )

    if fire_active:
        goals.append({"goal": "organize_fire_response", "priority": 0.98, "sector": "FireResponse", "description": "Carry water and organize fire watch"})
    if flood_active:
        goals.append({"goal": "repair_flood_damage", "priority": 0.94, "sector": "RoadRepair", "description": "Prioritize drainage and road repairs"})
    if food_crisis or v.food_reserve < food_needed * 0.6:
        goals.append({"goal": "expand_farming_and_rationing", "priority": 0.92, "sector": "Agriculture", "description": "Increase farming and apply rationing goals"})
    if disease_active:
        goals.append({"goal": "reduce_gatherings_and_recover", "priority": 0.90, "sector": "Health", "description": "Reduce gatherings; prioritize recovery and water"})
    if v.emergency_level > EMERGENCY_THRESHOLD:
        goals.append({"goal": "village_emergency_coordination", "priority": 0.88, "sector": "Leadership", "description": "Leader holds village meeting and deploys responders"})
    if v.wood_reserve < wood_needed * 0.6:
        goals.append({"goal": "increase_woodcutting", "priority": 0.80, "sector": "Forestry", "description": "Increase wood gathering and stockpile"})
    if v.workforce_size < max(1, int(float(n) * 0.7)):
        goals.append({"goal": "assign_work_roles", "priority": 0.72, "sector": "Occupation", "description": "Assign work roles to idle villagers"})
    if len(v.active_projects) == 0 and v.prosperity < 0.75 and v.emergency_level < 0.3:
        goals.append({"goal": "organize_storage_and_construction", "priority": 0.66, "sector": "StorageOrganization", "description": "Communal storage organization"})
    if v.morale < 0.45 and v.emergency_level < 0.5:
        goals.append({"goal": "community_celebration", "priority": 0.62, "sector": "Festival", "description": "Schedule a celebration to raise morale"})
    if v.prosperity > 0.8 and v.stability > 0.75 and v.morale > 0.7:
        goals.append({"goal": "invest_in_public_projects", "priority": 0.50, "sector": "ConstructionSupport", "description": "Undertake public works when village prospers"})
    return goals


def should_hold_meeting_for(
    *,
    village: VillageState,
    leadership: Leadership | None,
    tick_number: int,
    meeting_frequency_ticks: int = 30,
) -> bool:
    if village is None:
        return False
    last = int(leadership.last_meeting_tick) if leadership else 0
    if village.emergency_level > EMERGENCY_THRESHOLD:
        return True
    if tick_number - last >= max(1, meeting_frequency_ticks):
        return True
    return False


def labor_priority_for(
    *,
    village: VillageState,
    active_emergencies: Mapping[str, ActiveEmergency],
) -> tuple[tuple[str, float], ...]:
    v = village
    if v is None:
        return tuple()
    out: list[tuple[str, float]] = []
    em_ids = set(v.active_emergencies)
    any_fire = any(str(getattr(e, "emergency_id", "")) in em_ids and getattr(e, "emergency_type", "") == "Fire" for e in (active_emergencies or {}).values())
    any_flood = any(str(getattr(e, "emergency_id", "")) in em_ids and getattr(e, "emergency_type", "") == "Flood" for e in (active_emergencies or {}).values())
    any_disease = any(str(getattr(e, "emergency_id", "")) in em_ids and getattr(e, "emergency_type", "") == "DiseaseOutbreak" for e in (active_emergencies or {}).values())
    any_food = any(str(getattr(e, "emergency_id", "")) in em_ids and getattr(e, "emergency_type", "") == "FoodCrisis" for e in (active_emergencies or {}).values())
    if any_fire:
        out.append(("FireResponse", 0.99))
    if any_flood:
        out.append(("RoadRepair", 0.93))
    if any_disease:
        out.append(("Health", 0.91))
    if any_food:
        out.append(("Agriculture", 0.90))
    out.append(("Agriculture", max(0.6, 0.85 - v.food_reserve / max(1.0, 200.0))))
    out.append(("Forestry", max(0.5, 0.75 - v.wood_reserve / max(1.0, 200.0))))
    out.append(("Production", 0.6 + 0.2 * clamp(v.prosperity)))
    out.append(("Trade", 0.4 + 0.3 * clamp(v.prosperity)))
    out.append(("CommunityCare", 0.3 + 0.5 * clamp(1.0 - v.morale)))
    return tuple(sorted(out, key=lambda kv: -kv[1]))
