from typing import List, Tuple
from .society_models import VillageState


def compute_prosperity(
    village: VillageState,
    food_per_capita: float,
    health_score: float,
    economy_score: float,
    production_score: float,
    relationship_score: float,
    learning_score: float,
    agri_score: float,
    weather_resilience: float
) -> float:
    raw = (
        0.20 * min(1.0, food_per_capita / 5.0) +
        0.15 * max(0.0, min(1.0, health_score)) +
        0.15 * max(0.0, min(1.0, economy_score)) +
        0.10 * max(0.0, min(1.0, production_score)) +
        0.10 * max(0.0, min(1.0, relationship_score)) +
        0.10 * max(0.0, min(1.0, learning_score)) +
        0.10 * max(0.0, min(1.0, agri_score)) +
        0.10 * max(0.0, min(1.0, weather_resilience))
    )
    return round(max(0.0, min(1.0, raw)), 4)


def compute_stability(
    village: VillageState,
    conflict_level: float,
    trust_level: float,
    resource_shortage_severity: float,
    has_leader: bool,
    recent_deaths: int,
    cooperation_level: float
) -> float:
    base = 0.5
    leader_bonus = 0.15 if has_leader else -0.10
    conflict_penalty = -0.25 * max(0.0, min(1.0, conflict_level))
    trust_bonus = 0.20 * max(0.0, min(1.0, trust_level))
    shortage_penalty = -0.20 * max(0.0, min(1.0, resource_shortage_severity))
    death_penalty = -0.10 * min(5, recent_deaths)
    coop_bonus = 0.20 * max(0.0, min(1.0, cooperation_level))

    raw = base + leader_bonus + conflict_penalty + trust_bonus + shortage_penalty + death_penalty + coop_bonus
    return round(max(0.0, min(1.0, raw)), 4)


def compute_morale(
    village: VillageState,
    successful_harvests: int,
    active_festivals: int,
    recent_deaths: int,
    conflict_level: float,
    starvation_risk: float,
    illness_rate: float,
    achievements_count: int
) -> float:
    base = 0.5
    harvest_bonus = min(0.2, successful_harvests * 0.05)
    festival_bonus = min(0.25, active_festivals * 0.15)
    death_penalty = min(0.4, recent_deaths * 0.15)
    conflict_penalty = 0.2 * max(0.0, min(1.0, conflict_level))
    starve_penalty = 0.3 * max(0.0, min(1.0, starvation_risk))
    illness_penalty = 0.2 * max(0.0, min(1.0, illness_rate))
    achievement_bonus = min(0.15, achievements_count * 0.05)

    raw = base + harvest_bonus + festival_bonus + achievement_bonus - death_penalty - conflict_penalty - starve_penalty - illness_penalty
    return round(max(0.0, min(1.0, raw)), 4)


def detect_emergencies(
    village: VillageState,
    severe_weather: bool,
    fire_active: bool,
    disease_outbreak: bool
) -> List[Tuple[str, float]]:
    emergencies = []

    food_per_cap = village.food_reserve / max(1, village.population)
    if food_per_cap < 1.0:
        severity = round(1.0 - (food_per_cap / 1.0), 2)
        emergencies.append(("Food crisis", severity))

    if severe_weather:
        emergencies.append(("Flood", 0.7))

    if fire_active:
        emergencies.append(("Fire", 0.9))

    if disease_outbreak:
        emergencies.append(("Disease outbreak", 0.8))

    if village.wood_reserve < village.population * 0.5:
        emergencies.append(("Resource shortage", 0.5))

    if village.workforce < village.population * 0.3:
        emergencies.append(("Workforce shortage", 0.6))

    return emergencies
