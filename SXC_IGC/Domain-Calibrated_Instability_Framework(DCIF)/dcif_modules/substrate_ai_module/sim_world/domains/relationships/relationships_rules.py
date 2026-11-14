from __future__ import annotations

from typing import Any, Mapping, Sequence

from .relationships_events import (
    ConflictOccurred,
    FriendshipFormed,
    InteractionRecorded,
    RelationshipStrengthened,
    RelationshipWeakened,
    RespectIncreased,
    RespectReduced,
    TrustIncreased,
    TrustReduced,
)
from .relationships_models import Relationship

INTERACTION_DELTAS: dict[str, dict[str, float]] = {
    "WorkedTogether": {"trust": 0.05, "respect": 0.05, "familiarity": 0.10, "affinity": 0.05},
    "SharedMeal": {"trust": 0.05, "respect": 0.02, "familiarity": 0.10, "affinity": 0.10},
    "Conversation": {"trust": 0.02, "respect": 0.02, "familiarity": 0.08, "affinity": 0.05},
    "Talk": {"trust": 0.02, "respect": 0.02, "familiarity": 0.08, "affinity": 0.05},
    "Trade": {"trust": 0.05, "respect": 0.05, "familiarity": 0.05, "affinity": 0.02},
    "Gift": {"trust": 0.10, "respect": 0.05, "familiarity": 0.08, "affinity": 0.12},
    "Share": {"trust": 0.08, "respect": 0.05, "familiarity": 0.08, "affinity": 0.08},
    "Helped": {"trust": 0.15, "respect": 0.10, "familiarity": 0.10, "affinity": 0.10},
    "Ignored": {"trust": -0.05, "respect": -0.02, "familiarity": -0.02, "affinity": -0.05},
    "Conflict": {"trust": -0.20, "respect": -0.15, "familiarity": 0.05, "affinity": -0.20},
    "Competition": {"trust": -0.02, "respect": 0.05, "familiarity": 0.05, "affinity": -0.05},
}


def make_relationship_key(entity_a: str, entity_b: str) -> str:
    sorted_ids = sorted([str(entity_a), str(entity_b)])
    return f"rel:{sorted_ids[0]}:{sorted_ids[1]}"


def apply_interaction(
    rel: Relationship,
    interaction_type: str,
    actor_id: str,
    target_id: str,
    tick: int = 0,
) -> tuple[Relationship, list[Any]]:
    deltas = INTERACTION_DELTAS.get(interaction_type, {"familiarity": 0.05, "affinity": 0.02})
    events: list[Any] = []

    old_strength = rel.strength
    old_trust = rel.trust
    old_respect = rel.respect
    old_type = rel.relationship_type

    new_trust = max(0.0, min(1.0, rel.trust + deltas.get("trust", 0.0)))
    new_respect = max(0.0, min(1.0, rel.respect + deltas.get("respect", 0.0)))
    new_fam = max(0.0, min(1.0, rel.familiarity + deltas.get("familiarity", 0.0)))
    new_aff = max(0.0, min(1.0, rel.affinity + deltas.get("affinity", 0.0)))

    # Interaction record entry
    rec_entry = {
        "interaction_type": interaction_type,
        "actor_id": actor_id,
        "target_id": target_id,
        "tick": tick,
    }
    history = list(rel.interaction_history)
    history.append(rec_entry)

    # Check relationship type upgrade
    new_type = old_type
    if old_type in ("Stranger", "Acquaintance") and new_trust >= 0.6 and new_aff >= 0.6:
        new_type = "Friend"
        events.append(FriendshipFormed(relationship_id=rel.relationship_id, entity_a=rel.entity_a, entity_b=rel.entity_b, tick=tick))

    updated = Relationship(
        relationship_id=rel.relationship_id,
        entity_a=rel.entity_a,
        entity_b=rel.entity_b,
        relationship_type=new_type,
        trust=new_trust,
        respect=new_respect,
        familiarity=new_fam,
        affinity=new_aff,
        interaction_history=tuple(history),
        last_interaction_tick=tick,
    )
    updated.strength = updated.calculate_strength()

    # Events emission
    events.append(
        InteractionRecorded(
            relationship_id=rel.relationship_id,
            interaction_type=interaction_type,
            actor_id=actor_id,
            target_id=target_id,
            tick=tick,
        )
    )

    if new_trust > old_trust:
        events.append(TrustIncreased(relationship_id=rel.relationship_id, delta=round(new_trust - old_trust, 3), new_trust=new_trust, tick=tick))
    elif new_trust < old_trust:
        events.append(TrustReduced(relationship_id=rel.relationship_id, delta=round(old_trust - new_trust, 3), new_trust=new_trust, tick=tick))

    if new_respect > old_respect:
        events.append(RespectIncreased(relationship_id=rel.relationship_id, delta=round(new_respect - old_respect, 3), new_respect=new_respect, tick=tick))
    elif new_respect < old_respect:
        events.append(RespectReduced(relationship_id=rel.relationship_id, delta=round(old_respect - new_respect, 3), new_respect=new_respect, tick=tick))

    if updated.strength > old_strength:
        events.append(RelationshipStrengthened(relationship_id=rel.relationship_id, old_strength=old_strength, new_strength=updated.strength, tick=tick))
    elif updated.strength < old_strength:
        events.append(RelationshipWeakened(relationship_id=rel.relationship_id, old_strength=old_strength, new_strength=updated.strength, tick=tick))

    if interaction_type == "Conflict":
        events.append(ConflictOccurred(relationship_id=rel.relationship_id, actor_id=actor_id, target_id=target_id, tick=tick))

    return updated, events


def decay_familiarity(rel: Relationship, current_tick: int) -> tuple[Relationship, list[Any]]:
    idle_ticks = current_tick - rel.last_interaction_tick
    if idle_ticks < 48 or rel.familiarity <= 0.05:
        return rel, []

    decay_amount = 0.01 * (idle_ticks // 24)
    new_fam = max(0.05, rel.familiarity - decay_amount)

    if new_fam == rel.familiarity:
        return rel, []

    updated = Relationship(
        relationship_id=rel.relationship_id,
        entity_a=rel.entity_a,
        entity_b=rel.entity_b,
        relationship_type=rel.relationship_type,
        trust=rel.trust,
        respect=rel.respect,
        familiarity=new_fam,
        affinity=rel.affinity,
        interaction_history=rel.interaction_history,
        last_interaction_tick=rel.last_interaction_tick,
    )
    updated.strength = updated.calculate_strength()

    events = []
    if updated.strength < rel.strength:
        events.append(RelationshipWeakened(relationship_id=rel.relationship_id, old_strength=rel.strength, new_strength=updated.strength, tick=current_tick))

    return updated, events


TYPE_PREFERENCE_WEIGHT: dict[str, float] = {
    "Family": 1.00,
    "Friend": 0.92,
    "Mentor": 0.85,
    "Student": 0.83,
    "Leader": 0.80,
    "Follower": 0.78,
    "Coworker": 0.70,
    "Neighbor": 0.60,
    "Acquaintance": 0.40,
    "Stranger": 0.10,
}


def _preference_score(rel: Relationship, context: str = "general") -> float:
    type_w = TYPE_PREFERENCE_WEIGHT.get(rel.relationship_type, 0.10)
    trust_c = rel.trust
    fam_c = rel.familiarity
    strength_c = rel.strength
    if context == "trade":
        base = 0.40 * trust_c + 0.20 * type_w + 0.25 * strength_c + 0.15 * fam_c
    elif context == "help":
        base = 0.35 * trust_c + 0.30 * type_w + 0.20 * strength_c + 0.15 * fam_c
    elif context == "conversation":
        base = 0.25 * trust_c + 0.30 * type_w + 0.20 * strength_c + 0.25 * fam_c
    elif context == "cooperation":
        base = 0.30 * trust_c + 0.25 * type_w + 0.30 * strength_c + 0.15 * fam_c
    elif context == "leadership":
        base = 0.20 * trust_c + 0.35 * type_w + 0.30 * rel.respect + 0.15 * fam_c
    else:
        base = 0.30 * trust_c + 0.30 * type_w + 0.25 * strength_c + 0.15 * fam_c
    return round(max(0.0, min(1.0, base)), 3)


def rank_social_partners(
    relationships: Mapping[str, Relationship] | Mapping[str, Mapping[str, Any]],
    actor_id: str,
    candidate_ids: Sequence[str],
    context: str = "general",
) -> list[tuple[str, float]]:
    actor_key = str(actor_id)
    candidate_keys = [str(c) for c in candidate_ids]
    scored: list[tuple[str, float]] = []
    for cid in sorted(candidate_keys):
        key = make_relationship_key(actor_key, cid)
        raw_rel = relationships.get(key)
        if raw_rel is None:
            scored.append((cid, TYPE_PREFERENCE_WEIGHT["Stranger"]))
            continue
        if isinstance(raw_rel, Relationship):
            rel = raw_rel
        else:
            rel = Relationship.from_dict(raw_rel)
        scored.append((cid, _preference_score(rel, context=context)))
    scored.sort(key=lambda item: (-item[1], item[0]))
    return scored


def prefer_trade_partner(
    relationships: Mapping[str, Relationship] | Mapping[str, Mapping[str, Any]],
    actor_id: str,
    candidate_ids: Sequence[str],
) -> list[tuple[str, float]]:
    return rank_social_partners(relationships, actor_id, candidate_ids, context="trade")


def prefer_help_partner(
    relationships: Mapping[str, Relationship] | Mapping[str, Mapping[str, Any]],
    actor_id: str,
    candidate_ids: Sequence[str],
) -> list[tuple[str, float]]:
    return rank_social_partners(relationships, actor_id, candidate_ids, context="help")


def prefer_conversation_partner(
    relationships: Mapping[str, Relationship] | Mapping[str, Mapping[str, Any]],
    actor_id: str,
    candidate_ids: Sequence[str],
) -> list[tuple[str, float]]:
    return rank_social_partners(relationships, actor_id, candidate_ids, context="conversation")


def prefer_cooperation_partner(
    relationships: Mapping[str, Relationship] | Mapping[str, Mapping[str, Any]],
    actor_id: str,
    candidate_ids: Sequence[str],
) -> list[tuple[str, float]]:
    return rank_social_partners(relationships, actor_id, candidate_ids, context="cooperation")


def prefer_leader_candidate(
    relationships: Mapping[str, Relationship] | Mapping[str, Mapping[str, Any]],
    actor_id: str,
    candidate_ids: Sequence[str],
) -> list[tuple[str, float]]:
    return rank_social_partners(relationships, actor_id, candidate_ids, context="leadership")


def cooperation_willingness(
    relationships: Mapping[str, Relationship] | Mapping[str, Mapping[str, Any]],
    actor_id: str,
    target_id: str,
) -> float:
    actor_key = str(actor_id)
    target_key = str(target_id)
    key = make_relationship_key(actor_key, target_key)
    raw_rel = relationships.get(key)
    if raw_rel is None:
        return TYPE_PREFERENCE_WEIGHT["Stranger"]
    rel = raw_rel if isinstance(raw_rel, Relationship) else Relationship.from_dict(raw_rel)
    return _preference_score(rel, context="cooperation")


def resource_sharing_willingness(
    relationships: Mapping[str, Relationship] | Mapping[str, Mapping[str, Any]],
    actor_id: str,
    target_id: str,
) -> float:
    actor_key = str(actor_id)
    target_key = str(target_id)
    key = make_relationship_key(actor_key, target_key)
    raw_rel = relationships.get(key)
    if raw_rel is None:
        return TYPE_PREFERENCE_WEIGHT["Stranger"] * 0.5
    rel = raw_rel if isinstance(raw_rel, Relationship) else Relationship.from_dict(raw_rel)
    return round(max(0.0, min(1.0, 0.50 * rel.trust + 0.30 * rel.strength + 0.20 * rel.affinity)), 3)
