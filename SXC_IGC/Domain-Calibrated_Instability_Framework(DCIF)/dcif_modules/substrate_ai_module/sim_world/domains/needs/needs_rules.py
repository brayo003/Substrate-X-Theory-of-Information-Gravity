from __future__ import annotations

from typing import Any, Mapping
from .needs_events import NeedEvent
from .needs_models import get_traits


def evaluate_villager_needs(
    villager_id: str,
    occupation: str,
    current_needs: Mapping[str, float],
    location: str | None,
    weather: str,
    status: str | None,
    last_action: str | None,
) -> tuple[dict[str, float], list[NeedEvent]]:
    traits = get_traits(occupation)
    old = {
        "hunger": float(current_needs.get("hunger", 0.3)),
        "thirst": float(current_needs.get("thirst", 0.2)),
        "energy": float(current_needs.get("energy", 0.8)),
        "warmth": float(current_needs.get("warmth", 1.0)),
        "comfort": float(current_needs.get("comfort", 0.8)),
        "social": float(current_needs.get("social", 0.7)),
    }

    new_needs = dict(old)
    events: list[NeedEvent] = []

    # 1. Hunger (+ decay, - recovery on Eat)
    if last_action == "Eat" or status == "eating":
        new_needs["hunger"] = max(0.0, old["hunger"] - 0.35)
        events.append(NeedEvent("NeedSatisfied", villager_id, "hunger", old["hunger"], new_needs["hunger"]))
    else:
        new_needs["hunger"] = min(1.0, old["hunger"] + 0.02 * traits.hunger_decay_mult)
        if old["hunger"] <= 0.7 < new_needs["hunger"]:
            events.append(NeedEvent("NeedCritical", villager_id, "hunger", old["hunger"], new_needs["hunger"]))

    # 2. Thirst (+ decay, - recovery on Drink)
    if last_action == "Drink" or status == "drinking":
        new_needs["thirst"] = max(0.0, old["thirst"] - 0.35)
        events.append(NeedEvent("NeedSatisfied", villager_id, "thirst", old["thirst"], new_needs["thirst"]))
    else:
        new_needs["thirst"] = min(1.0, old["thirst"] + 0.03 * traits.thirst_decay_mult)
        if old["thirst"] <= 0.7 < new_needs["thirst"]:
            events.append(NeedEvent("NeedCritical", villager_id, "thirst", old["thirst"], new_needs["thirst"]))

    # 3. Energy (+ recovery on Sleep, - decay on action/work)
    if last_action == "Sleep" or status == "sleeping":
        new_needs["energy"] = min(traits.max_energy, old["energy"] + 0.35)
        events.append(NeedEvent("NeedRecovered", villager_id, "energy", old["energy"], new_needs["energy"]))
    else:
        decay = 0.03 if last_action in {"Walk", "Work"} or status == "working" else 0.015
        new_needs["energy"] = max(0.0, old["energy"] - decay * traits.energy_decay_mult)
        if old["energy"] >= 0.3 > new_needs["energy"]:
            events.append(NeedEvent("NeedCritical", villager_id, "energy", old["energy"], new_needs["energy"]))

    # 4. Warmth (shelter/weather)
    is_indoor = location in {"house_1", "house_2", "house_3", "house_4", "farm", "barn", "blacksmith", "storage", "tavern"}
    if is_indoor:
        new_needs["warmth"] = min(1.0, old["warmth"] + 0.2)
    elif weather == "rain":
        new_needs["warmth"] = max(0.0, old["warmth"] - 0.15)
    elif weather == "cloudy":
        new_needs["warmth"] = max(0.0, old["warmth"] - 0.05)
    else:
        new_needs["warmth"] = min(1.0, old["warmth"] + 0.05)

    if old["warmth"] >= 0.3 > new_needs["warmth"]:
        events.append(NeedEvent("NeedCritical", villager_id, "warmth", old["warmth"], new_needs["warmth"]))

    # 5. Comfort
    if is_indoor or status in {"sitting", "resting"}:
        new_needs["comfort"] = min(1.0, old["comfort"] + 0.1)
    elif last_action == "Walk" or status == "working":
        new_needs["comfort"] = max(0.0, old["comfort"] - 0.05)
    else:
        new_needs["comfort"] = min(1.0, old["comfort"] + 0.02)

    # 6. Social
    if last_action == "Talk" or status == "talking" or location in {"tavern", "village_square"}:
        new_needs["social"] = min(1.0, old["social"] + 0.25)
        events.append(NeedEvent("NeedSatisfied", villager_id, "social", old["social"], new_needs["social"]))
    else:
        new_needs["social"] = max(0.0, old["social"] - 0.02 * traits.social_decay_mult)
        if old["social"] >= 0.3 > new_needs["social"]:
            events.append(NeedEvent("NeedCritical", villager_id, "social", old["social"], new_needs["social"]))

    return new_needs, events
