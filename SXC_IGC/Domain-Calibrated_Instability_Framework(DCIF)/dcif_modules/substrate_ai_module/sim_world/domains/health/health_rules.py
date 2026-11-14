from __future__ import annotations

from typing import Any, Mapping

from .health_events import (
    DeathOccurred,
    Dehydrated,
    FatigueIncreased,
    FatigueRecovered,
    HealthDeclined,
    HealthImproved,
    HeatStressStarted,
    HypothermiaStarted,
    IllnessRecovered,
    IllnessStarted,
    InjuryOccurred,
    InjuryRecovered,
    Malnourished,
    RecoveryCompleted,
    RecoveryStarted,
)
from .health_models import (
    DEFAULT_BODY_TEMP,
    DEATH_THRESHOLD,
    HEALTH_MAX,
    HEALTH_MIN,
    ILLNESS_TYPES,
    INJURY_RECOVERY_RATE,
    INJURY_TYPES,
    IMMUNITY_SICKNESS_DECAY,
    RECOVERY_RATE_BASE,
    HealthState,
    add_illness,
    add_injury,
    clamp,
    deterministic_hash,
    remove_illness,
    remove_injury,
)


def _bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return bool(int(v) != 0)
    s = str(v).strip().lower()
    return s in {"1", "true", "yes", "on"}


def _float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except Exception:
        return float(default)


def derive_body_temperature_from_weather(
    *,
    weather_temperature_c: float,
    is_outside: bool,
    has_warm_clothing: bool,
    current_body_temp: float = DEFAULT_BODY_TEMP,
    weather_state_short: str = "clear",
) -> float:
    base = float(current_body_temp)
    wt = float(weather_temperature_c)
    if not _bool(is_outside):
        delta = (36.7 - base) * 0.15
        return clamp(base + delta, 30.0, 44.0)
    clothing_factor = 0.8 if _bool(has_warm_clothing) else 1.4
    if wt < 0.0:
        delta = (wt - 5.0) * 0.02 * clothing_factor
    elif wt < 10.0:
        delta = (wt - 15.0) * 0.012 * clothing_factor
    elif wt > 35.0:
        delta = (wt - 32.0) * 0.018
    elif wt > 28.0:
        delta = (wt - 30.0) * 0.01
    else:
        delta = (36.7 - base) * 0.05
    if weather_state_short in ("rain", "storm", "snow"):
        delta -= 0.25 * clothing_factor
    return clamp(base + delta, 30.0, 44.0)


def apply_food_eaten(
    nutrition: float, hydration: float, immunity: float, food_quality: float, water_quality: float
) -> tuple[float, float, float]:
    fq = clamp(_float(food_quality, 0.8), 0.0, 1.0)
    wq = clamp(_float(water_quality, 0.8), 0.0, 1.0)
    n = clamp(nutrition + 0.12 * fq, 0.0, HEALTH_MAX)
    h = clamp(hydration + 0.08 * wq, 0.0, HEALTH_MAX)
    imm = clamp(immunity + 0.02 * (fq + wq) * 0.5, 0.0, HEALTH_MAX)
    return n, h, imm


def apply_water_drank(hydration: float, water_quality: float) -> float:
    wq = clamp(_float(water_quality, 0.8), 0.0, 1.0)
    return clamp(hydration + 0.2 * wq, 0.0, HEALTH_MAX)


def apply_sleep_recovery(fatigue: float, stress: float, body_temp_c: float) -> tuple[float, float, float]:
    fatigue_n = clamp(fatigue - 0.25, 0.0, HEALTH_MAX)
    stress_n = clamp(stress - 0.08, 0.0, HEALTH_MAX)
    bt = clamp(body_temp_c + 0.1, 30.0, 44.0)
    return fatigue_n, stress_n, bt


def apply_heavy_work(fatigue: float, nutrition: float, hydration: float, injury: float) -> tuple[float, float, float, float]:
    fat = clamp(fatigue + 0.18, 0.0, HEALTH_MAX)
    nut = clamp(nutrition - 0.05, 0.0, HEALTH_MAX)
    hyd = clamp(hydration - 0.07, 0.0, HEALTH_MAX)
    inj = clamp(injury, 0.0, HEALTH_MAX)
    return fat, nut, hyd, inj


def apply_light_work(fatigue: float, nutrition: float, hydration: float) -> tuple[float, float, float]:
    fat = clamp(fatigue + 0.07, 0.0, HEALTH_MAX)
    nut = clamp(nutrition - 0.02, 0.0, HEALTH_MAX)
    hyd = clamp(hydration - 0.03, 0.0, HEALTH_MAX)
    return fat, nut, hyd


def apply_rest_recovery(fatigue: float, stress: float) -> tuple[float, float]:
    fat = clamp(fatigue - 0.1, 0.0, HEALTH_MAX)
    strs = clamp(stress - 0.04, 0.0, HEALTH_MAX)
    return fat, strs


def compute_overall_health_from_components(
    fatigue: float,
    nutrition: float,
    hydration: float,
    immunity: float,
    stress: float,
    sickness: float,
    injury: float,
    infection: float,
    body_temperature_c: float,
) -> float:
    base = (
        (1.0 - fatigue) * 0.12
        + nutrition * 0.16
        + hydration * 0.16
        + immunity * 0.14
        + (1.0 - stress) * 0.1
        + (1.0 - sickness) * 0.12
        + (1.0 - injury) * 0.1
        + (1.0 - infection) * 0.1
    )
    if body_temperature_c < 34.0:
        base *= 0.6
    elif body_temperature_c > 40.0:
        base *= 0.7
    elif body_temperature_c < 35.5 or body_temperature_c > 38.5:
        base *= 0.9
    return clamp(base, HEALTH_MIN, HEALTH_MAX)


def _tick_decides(seed: str, divisor: int) -> bool:
    if int(divisor) <= 1:
        return True
    return deterministic_hash(seed) % int(divisor) == 0


def _determine_illnesses(
    *,
    prev: HealthState,
    hydration_n: float,
    nutrition_n: float,
    body_temp_n: float,
    immunity_n: float,
    fatigue_n: float,
    sickness_n: float,
    tick_number: int,
    weather_state_short: str,
    food_poisoned: bool,
    seed_tag: str,
) -> tuple[tuple[str, ...], float, tuple[Any, ...]]:
    events: list[Any] = []
    illnesses = list(prev.active_illnesses)
    sickness = float(sickness_n)
    eid = prev.entity_id

    # Dehydration
    if hydration_n < 0.25 and "Dehydration" not in illnesses:
        illnesses.append("Dehydration")
        sickness = clamp(sickness + 0.15, 0.0, HEALTH_MAX)
        events.append(Dehydrated(tick_number, eid, metadata={"hydration": hydration_n}))
        events.append(IllnessStarted(tick_number, eid, illness_type="Dehydration", metadata={"level": hydration_n}))
    elif "Dehydration" in illnesses and hydration_n > 0.7:
        illnesses = [x for x in illnesses if x != "Dehydration"]
        events.append(IllnessRecovered(tick_number, eid, illness_type="Dehydration"))

    # Malnutrition
    if nutrition_n < 0.25 and "Malnutrition" not in illnesses:
        illnesses.append("Malnutrition")
        sickness = clamp(sickness + 0.12, 0.0, HEALTH_MAX)
        events.append(Malnourished(tick_number, eid, metadata={"nutrition": nutrition_n}))
        events.append(IllnessStarted(tick_number, eid, illness_type="Malnutrition"))
    elif "Malnutrition" in illnesses and nutrition_n > 0.75:
        illnesses = [x for x in illnesses if x != "Malnutrition"]
        events.append(IllnessRecovered(tick_number, eid, illness_type="Malnutrition"))

    # Hypothermia
    if body_temp_n < 34.0 and "Hypothermia" not in illnesses:
        illnesses.append("Hypothermia")
        sickness = clamp(sickness + 0.2, 0.0, HEALTH_MAX)
        events.append(HypothermiaStarted(tick_number, eid, body_temperature_c=body_temp_n))
        events.append(IllnessStarted(tick_number, eid, illness_type="Hypothermia"))
    elif "Hypothermia" in illnesses and body_temp_n > 36.0:
        illnesses = [x for x in illnesses if x != "Hypothermia"]
        events.append(IllnessRecovered(tick_number, eid, illness_type="Hypothermia"))

    # Heat Stress
    if body_temp_n > 39.0 and "HeatStress" not in illnesses:
        illnesses.append("HeatStress")
        sickness = clamp(sickness + 0.18, 0.0, HEALTH_MAX)
        events.append(HeatStressStarted(tick_number, eid, body_temperature_c=body_temp_n))
        events.append(IllnessStarted(tick_number, eid, illness_type="HeatStress"))
    elif "HeatStress" in illnesses and body_temp_n < 37.8:
        illnesses = [x for x in illnesses if x != "HeatStress"]
        events.append(IllnessRecovered(tick_number, eid, illness_type="HeatStress"))

    # Exhaustion
    if fatigue_n > 0.85 and "Exhaustion" not in illnesses:
        illnesses.append("Exhaustion")
        sickness = clamp(sickness + 0.1, 0.0, HEALTH_MAX)
        events.append(IllnessStarted(tick_number, eid, illness_type="Exhaustion", metadata={"fatigue": fatigue_n}))
    elif "Exhaustion" in illnesses and fatigue_n < 0.35:
        illnesses = [x for x in illnesses if x != "Exhaustion"]
        events.append(IllnessRecovered(tick_number, eid, illness_type="Exhaustion"))

    # Food Poisoning
    if _bool(food_poisoned) and "FoodPoisoning" not in illnesses:
        illnesses.append("FoodPoisoning")
        sickness = clamp(sickness + 0.2, 0.0, HEALTH_MAX)
        events.append(IllnessStarted(tick_number, eid, illness_type="FoodPoisoning"))

    if "FoodPoisoning" in illnesses:
        if _tick_decides(f"{eid}:{tick_number}:foodpoison:{seed_tag}", 12):
            illnesses = [x for x in illnesses if x != "FoodPoisoning"]
            events.append(IllnessRecovered(tick_number, eid, illness_type="FoodPoisoning"))

    # Cold: low immunity + cold weather OR Hypothermia present
    cold_trigger = (immunity_n < 0.4 and (weather_state_short in ("cold", "snow", "storm"))) or "Hypothermia" in illnesses
    if cold_trigger and "Cold" not in illnesses and _tick_decides(f"{eid}:{tick_number}:cold:{seed_tag}", 8):
        illnesses.append("Cold")
        sickness = clamp(sickness + 0.12, 0.0, HEALTH_MAX)
        events.append(IllnessStarted(tick_number, eid, illness_type="Cold"))
    if "Cold" in illnesses and immunity_n > 0.7 and body_temp_n > 36.0:
        if _tick_decides(f"{eid}:{tick_number}:cold_end:{seed_tag}", 8):
            illnesses = [x for x in illnesses if x != "Cold"]
            events.append(IllnessRecovered(tick_number, eid, illness_type="Cold"))

    # Flu: Cold + sickness high
    if "Cold" in illnesses and sickness > 0.45 and "Flu" not in illnesses:
        if _tick_decides(f"{eid}:{tick_number}:flu:{seed_tag}", 12):
            illnesses.append("Flu")
            sickness = clamp(sickness + 0.1, 0.0, HEALTH_MAX)
            events.append(IllnessStarted(tick_number, eid, illness_type="Flu"))
    if "Flu" in illnesses and immunity_n > 0.8 and sickness < 0.2:
        illnesses = [x for x in illnesses if x != "Flu"]
        events.append(IllnessRecovered(tick_number, eid, illness_type="Flu"))

    return tuple(i for i in illnesses if i in ILLNESS_TYPES), sickness, tuple(events)


def _determine_injuries(
    *,
    prev: HealthState,
    tick_number: int,
    did_heavy_work: bool,
    did_construction: bool,
    was_outside_storm: bool,
    seed_tag: str,
    injury_n: float,
    mobility_n: float,
) -> tuple[tuple[str, ...], float, float, tuple[Any, ...]]:
    events: list[Any] = []
    injuries = list(prev.active_injuries)
    inj = float(injury_n)
    mob = float(mobility_n)
    eid = prev.entity_id

    # Recovery of existing injuries first
    for inj_type in list(injuries):
        if _tick_decides(f"{eid}:{tick_number}:inj_heal:{inj_type}:{seed_tag}", 20):
            injuries = [x for x in injuries if x != inj_type]
            inj = clamp(inj - INJURY_RECOVERY_RATE * 4.0, 0.0, HEALTH_MAX)
            mob = clamp(mob - 0.08, 0.0, 1.0)
            events.append(InjuryRecovered(tick_number, eid, injury_type=inj_type))

    if _bool(did_construction):
        if _tick_decides(f"{eid}:{tick_number}:consfall:{seed_tag}", 80):
            if "ConstructionFall" not in injuries:
                injuries.append("ConstructionFall")
                inj = clamp(inj + 0.25, 0.0, HEALTH_MAX)
                mob = clamp(mob + 0.3, 0.0, 1.0)
                events.append(InjuryOccurred(tick_number, eid, injury_type="ConstructionFall"))
        elif _tick_decides(f"{eid}:{tick_number}:sprain:{seed_tag}", 40):
            if "Sprain" not in injuries:
                injuries.append("Sprain")
                inj = clamp(inj + 0.1, 0.0, HEALTH_MAX)
                mob = clamp(mob + 0.1, 0.0, 1.0)
                events.append(InjuryOccurred(tick_number, eid, injury_type="Sprain"))

    if _bool(did_heavy_work) and "WorkStrain" not in injuries:
        if _tick_decides(f"{eid}:{tick_number}:workstrain:{seed_tag}", 60):
            injuries.append("WorkStrain")
            inj = clamp(inj + 0.08, 0.0, HEALTH_MAX)
            mob = clamp(mob + 0.06, 0.0, 1.0)
            events.append(InjuryOccurred(tick_number, eid, injury_type="WorkStrain"))

    if _bool(was_outside_storm):
        if _tick_decides(f"{eid}:{tick_number}:stormacc:{seed_tag}", 40):
            if "StormAccident" not in injuries:
                injuries.append("StormAccident")
                inj = clamp(inj + 0.18, 0.0, HEALTH_MAX)
                mob = clamp(mob + 0.2, 0.0, 1.0)
                events.append(InjuryOccurred(tick_number, eid, injury_type="StormAccident"))
        elif _tick_decides(f"{eid}:{tick_number}:fallingtree:{seed_tag}", 200):
            if "FallingTree" not in injuries:
                injuries.append("FallingTree")
                inj = clamp(inj + 0.3, 0.0, HEALTH_MAX)
                mob = clamp(mob + 0.4, 0.0, 1.0)
                events.append(InjuryOccurred(tick_number, eid, injury_type="FallingTree"))

    if _bool(did_heavy_work) and "MinorCut" not in injuries:
        if _tick_decides(f"{eid}:{tick_number}:minorcut:{seed_tag}", 30):
            injuries.append("MinorCut")
            inj = clamp(inj + 0.03, 0.0, HEALTH_MAX)
            events.append(InjuryOccurred(tick_number, eid, injury_type="MinorCut"))

    return tuple(i for i in injuries if i in INJURY_TYPES), inj, mob, tuple(events)


def evaluate_villager_health_tick(
    *,
    previous: HealthState,
    tick_number: int,
    needs: Mapping[str, Any] | None = None,
    weather_temperature_c: float = 15.0,
    weather_state_short: str = "clear",
    is_outside: bool = False,
    has_shelter: bool = False,
    has_warm_clothing: bool = False,
    did_sleep: bool = False,
    did_rest: bool = False,
    did_eat: bool = False,
    did_drink: bool = False,
    did_heavy_work: bool = False,
    did_light_work: bool = False,
    did_construction: bool = False,
    was_outside_storm: bool = False,
    food_quality: float = 0.8,
    water_quality: float = 0.8,
    food_spoiled: bool = False,
    had_treatment: bool = False,
    seed_tag: str = "",
) -> tuple[HealthState, tuple[Any, ...]]:
    if not previous.alive:
        return (previous, tuple())

    tick = int(tick_number)
    needs_dict: dict[str, Any] = dict(needs) if needs else {}

    fatigue = float(previous.fatigue)
    nutrition = float(previous.nutrition)
    hydration = float(previous.hydration)
    immunity = float(previous.immunity)
    stress = float(previous.stress)
    sickness = float(previous.sickness)
    injury = float(previous.injury)
    infection = float(previous.infection)
    mobility = float(previous.mobility_penalty)
    body_temp = float(previous.body_temperature_c)
    last_treat = int(previous.last_treatment_tick)
    recovering = bool(previous.recovering)

    events: list[Any] = []

    hunger_need = clamp(1.0 - _float(needs_dict.get("hunger", 0.0), 0.0), 0.0, 1.0)
    thirst_need = clamp(1.0 - _float(needs_dict.get("thirst", 0.0), 0.0), 0.0, 1.0)
    energy_need = clamp(_float(needs_dict.get("energy", 1.0), 1.0), 0.0, 1.0)
    comfort_need = clamp(_float(needs_dict.get("comfort", 1.0), 1.0), 0.0, 1.0)
    warmth_need = clamp(_float(needs_dict.get("warmth", 1.0), 1.0), 0.0, 1.0)
    social_need = clamp(_float(needs_dict.get("social", 1.0), 1.0), 0.0, 1.0)

    # Needs effects on baseline components
    nutrition = clamp(nutrition - (1.0 - hunger_need) * 0.05, 0.0, HEALTH_MAX)
    hydration = clamp(hydration - (1.0 - thirst_need) * 0.06, 0.0, HEALTH_MAX)
    fatigue = clamp(fatigue + (1.0 - energy_need) * 0.08, 0.0, HEALTH_MAX)
    stress = clamp(stress + (1.0 - comfort_need) * 0.05, 0.0, HEALTH_MAX)
    if warmth_need < 0.4:
        body_temp = clamp(body_temp - 0.15, 30.0, 44.0)
        stress = clamp(stress + 0.04, 0.0, HEALTH_MAX)
    if social_need < 0.4:
        stress = clamp(stress + 0.03, 0.0, HEALTH_MAX)

    # Explicit actions
    if _bool(did_eat):
        nutrition, _h, immunity = apply_food_eaten(nutrition, hydration, immunity, food_quality, water_quality)
        hydration = _h
    if _bool(did_drink):
        hydration = apply_water_drank(hydration, water_quality)
    if _bool(did_sleep):
        fatigue, stress, body_temp = apply_sleep_recovery(fatigue, stress, body_temp)
    if _bool(did_rest):
        fatigue, stress = apply_rest_recovery(fatigue, stress)

    food_poisoned = False
    if _bool(food_spoiled) and _bool(did_eat):
        food_poisoned = True
        nutrition = clamp(nutrition - 0.1, 0.0, HEALTH_MAX)
        sickness = clamp(sickness + 0.1, 0.0, HEALTH_MAX)

    if _bool(did_heavy_work):
        fatigue, nutrition, hydration, _ = apply_heavy_work(fatigue, nutrition, hydration, injury)
    elif _bool(did_light_work):
        fatigue, nutrition, hydration = apply_light_work(fatigue, nutrition, hydration)

    sheltered = _bool(has_shelter)
    outside = _bool(is_outside) and not sheltered
    body_temp = derive_body_temperature_from_weather(
        weather_temperature_c=float(weather_temperature_c),
        is_outside=outside,
        has_warm_clothing=_bool(has_warm_clothing),
        current_body_temp=body_temp,
        weather_state_short=str(weather_state_short),
    )

    # Treatment/recovery boost
    if _bool(had_treatment):
        last_treat = tick
        immunity = clamp(immunity + 0.06, 0.0, HEALTH_MAX)
        sickness = clamp(sickness - 0.08, 0.0, HEALTH_MAX)
        if not recovering:
            recovering = True
            events.append(RecoveryStarted(tick, previous.entity_id, reason="treatment"))

    # Recovering: natural recovery if rest and food/water OK
    conditions_good = (
        nutrition > 0.5
        and hydration > 0.5
        and sheltered
        and not _bool(did_heavy_work)
        and body_temp > 35.5
        and body_temp < 38.5
    )
    if conditions_good:
        if not recovering:
            recovering = True
            events.append(RecoveryStarted(tick, previous.entity_id, reason="good_conditions"))
        recover_rate = RECOVERY_RATE_BASE * (1.3 if had_treatment else 1.0)
        nutrition = clamp(nutrition + recover_rate * 0.4, 0.0, HEALTH_MAX)
        hydration = clamp(hydration + recover_rate * 0.4, 0.0, HEALTH_MAX)
        immunity = clamp(immunity + recover_rate * 0.3, 0.0, HEALTH_MAX)
        sickness = clamp(sickness - recover_rate, 0.0, HEALTH_MAX)
        infection = clamp(infection - recover_rate, 0.0, HEALTH_MAX)
    elif not sheltered and sickness > 0.0 and mobility < 0.5:
        recovering = False

    if recovering and conditions_good and sickness < 0.05 and injury < 0.05:
        recovering = False
        events.append(RecoveryCompleted(tick, previous.entity_id, reason="restored"))

    # Immunity decays sickness a little each tick if conditions OK
    if immunity > 0.6 and sickness > 0.0:
        sickness = clamp(sickness - IMMUNITY_SICKNESS_DECAY * immunity, 0.0, HEALTH_MAX)

    # Sickness / low immunity creates infection over time
    if sickness > 0.6 and immunity < 0.5:
        infection = clamp(infection + 0.02, 0.0, HEALTH_MAX)
    if infection > 0.0 and immunity > 0.5:
        infection = clamp(infection - IMMUNITY_SICKNESS_DECAY * 0.6 * immunity, 0.0, HEALTH_MAX)

    # Fatigue delta events
    prev_fatigue = float(previous.fatigue)
    fatigue_delta = float(fatigue) - prev_fatigue
    eid = previous.entity_id
    if fatigue_delta > 0.005:
        events.append(FatigueIncreased(tick, eid, delta_fatigue=fatigue_delta))
    elif fatigue_delta < -0.005:
        events.append(FatigueRecovered(tick, eid, delta_fatigue=-fatigue_delta))

    # Determine illnesses
    illnesses_n, sickness_n, ill_events = _determine_illnesses(
        prev=previous,
        hydration_n=hydration,
        nutrition_n=nutrition,
        body_temp_n=body_temp,
        immunity_n=immunity,
        fatigue_n=fatigue,
        sickness_n=sickness,
        tick_number=tick,
        weather_state_short=str(weather_state_short),
        food_poisoned=food_poisoned,
        seed_tag=str(seed_tag),
    )
    sickness = float(sickness_n)
    events.extend(ill_events)

    # Determine injuries
    injuries_n, injury_n, mob_n, inj_events = _determine_injuries(
        prev=previous,
        tick_number=tick,
        did_heavy_work=_bool(did_heavy_work),
        did_construction=_bool(did_construction),
        was_outside_storm=_bool(was_outside_storm),
        seed_tag=str(seed_tag),
        injury_n=injury,
        mobility_n=mobility,
    )
    injury = float(injury_n)
    mobility = float(mob_n)
    events.extend(inj_events)

    # Compute overall health from components
    overall = compute_overall_health_from_components(
        fatigue=fatigue,
        nutrition=nutrition,
        hydration=hydration,
        immunity=immunity,
        stress=stress,
        sickness=sickness,
        injury=injury,
        infection=infection,
        body_temperature_c=body_temp,
    )

    prev_overall = float(previous.overall_health)
    overall_delta = float(overall) - prev_overall
    if overall_delta > 0.002:
        events.append(HealthImproved(tick, eid, delta_health=overall_delta))
    elif overall_delta < -0.002:
        events.append(HealthDeclined(tick, eid, delta_health=-overall_delta))

    # Death check
    alive = True
    cause = ""
    if overall <= DEATH_THRESHOLD:
        alive = False
        if infection > 0.5 or sickness > 0.8:
            cause = "infection_sickness"
        elif injury > 0.8:
            cause = "injury"
        elif nutrition < 0.05:
            cause = "starvation"
        elif hydration < 0.05:
            cause = "dehydration"
        elif body_temp < 32.0:
            cause = "hypothermia"
        elif body_temp > 42.0:
            cause = "hyperthermia"
        elif fatigue > 0.98 and stress > 0.9:
            cause = "exhaustion_stress"
        else:
            cause = "health_failure"
        events.append(DeathOccurred(tick, eid, cause=cause))

    if not alive:
        recovering = False

    new_state = HealthState(
        health_id=previous.health_id,
        entity_id=previous.entity_id,
        overall_health=float(overall),
        fatigue=float(fatigue),
        nutrition=float(nutrition),
        hydration=float(hydration),
        immunity=float(immunity),
        stress=float(stress),
        sickness=float(sickness),
        injury=float(injury),
        infection=float(infection),
        body_temperature_c=float(body_temp),
        mobility_penalty=float(mobility),
        alive=bool(alive),
        recovering=bool(recovering),
        last_treatment_tick=int(last_treat),
        active_illnesses=tuple(illnesses_n),
        active_injuries=tuple(injuries_n),
        last_updated_tick=int(tick),
        birth_tick=int(previous.birth_tick),
    )
    return (new_state, tuple(events))


def work_efficiency_multiplier_for(hs: HealthState) -> float:
    if not hs.alive:
        return 0.0
    base = 1.0
    base *= 1.0 - 0.5 * float(hs.fatigue)
    base *= 1.0 - 0.35 * float(hs.sickness)
    base *= 1.0 - 0.45 * float(hs.injury)
    base *= 1.0 - 0.25 * float(hs.infection)
    base *= 1.0 - 0.3 * float(hs.mobility_penalty)
    base *= 1.0 - 0.2 * float(hs.stress)
    if hs.body_temperature_c < 34.5:
        base *= 0.7
    elif hs.body_temperature_c > 39.5:
        base *= 0.75
    nutrition_mult = 0.5 + 0.5 * float(hs.nutrition)
    hydration_mult = 0.5 + 0.5 * float(hs.hydration)
    base *= nutrition_mult
    base *= hydration_mult
    return clamp(base, 0.0, 1.2)


def should_prioritize_rest(hs: HealthState) -> bool:
    if not hs.alive:
        return False
    if hs.fatigue > 0.7:
        return True
    if hs.sickness > 0.35:
        return True
    if hs.injury > 0.25:
        return True
    if hs.active_illnesses:
        return True
    if hs.recovering and hs.sickness > 0.08:
        return True
    return False


def should_seek_shelter_for_health(hs: HealthState) -> bool:
    if not hs.alive:
        return False
    if hs.body_temperature_c < 35.5:
        return True
    if hs.body_temperature_c > 38.8:
        return True
    if "Hypothermia" in hs.active_illnesses or "HeatStress" in hs.active_illnesses:
        return True
    if hs.sickness > 0.4 and hs.immunity < 0.4:
        return True
    return False


def should_go_to_hospital_or_home(hs: HealthState) -> bool:
    if not hs.alive:
        return False
    if hs.injury > 0.35:
        return True
    if hs.sickness > 0.5:
        return True
    if hs.active_illnesses and hs.immunity < 0.45:
        return True
    if hs.active_injuries and hs.mobility_penalty > 0.2:
        return True
    if hs.infection > 0.3:
        return True
    return False
