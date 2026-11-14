from __future__ import annotations

from typing import Any, Mapping, Sequence

from ...core.contracts import TransitionProposal
from ...simulation.simulation_engine import SimulationEngine
from .relationships_events import (
    RelationshipCreated,
)
from .relationships_models import Relationship
from .relationships_rules import (
    INTERACTION_DELTAS,
    apply_interaction,
    decay_familiarity,
    make_relationship_key,
    prefer_cooperation_partner,
    prefer_conversation_partner,
    prefer_help_partner,
    prefer_leader_candidate,
    prefer_trade_partner,
    rank_social_partners,
    cooperation_willingness,
    resource_sharing_willingness,
)


def register(engine: SimulationEngine) -> None:
    engine.register_domain("relationships", lambda engine, context: apply(context))


def _extract_context(ctx: Any) -> tuple[dict[str, Any], Any, int]:
    state = dict(getattr(ctx, "current_state", None) or getattr(ctx, "world_state", {}))
    world_id = ctx.world_id
    tick_number = int(getattr(ctx, "current_tick_number", None) or getattr(ctx, "tick_number", 0))
    return state, world_id, tick_number


def initialize_valley_relationships(kernel: Any) -> dict[str, Relationship]:
    entities = kernel.entity_registry.list_entities() if hasattr(kernel, "entity_registry") else []
    human_ids = [e.display_name for e in entities if getattr(e, "type", "") == "human"]
    if not human_ids:
        human_ids = ["Mira", "Joren", "Elan"]

    relationships: dict[str, Relationship] = {}
    for i in range(len(human_ids)):
        for j in range(i + 1, len(human_ids)):
            e_a, e_b = human_ids[i], human_ids[j]
            key = make_relationship_key(e_a, e_b)
            # Default preset relationships
            rel_type = "Neighbor"
            trust_val = 0.5
            if (e_a, e_b) in [("Mira", "Joren"), ("Joren", "Mira")]:
                rel_type = "Family"
                trust_val = 0.8
            rel = Relationship(
                relationship_id=key,
                entity_a=e_a,
                entity_b=e_b,
                relationship_type=rel_type,
                trust=trust_val,
                respect=0.6,
                familiarity=0.5,
                affinity=0.6,
            )
            relationships[key] = rel

    rel_dict = {k: v.to_dict() for k, v in relationships.items()}
    if hasattr(kernel, "_state") and isinstance(kernel._state, dict):
        kernel._state["relationships"] = rel_dict

    return relationships


def apply(context: Any) -> tuple[TransitionProposal, ...]:
    world_state = dict(context.world_state)
    tick = int(context.tick_number)
    rel_data = dict(world_state.get("relationships", {}))
    prior_rel_keys = set(world_state.get("_relationships_prior_keys", ()))

    updated_rels: dict[str, Any] = {}
    events: list[dict[str, Any]] = []

    for rkey, rdict in sorted(rel_data.items()):
        rel_obj = Relationship.from_dict(rdict)
        if rkey not in prior_rel_keys:
            events.append(
                RelationshipCreated(
                    relationship_id=rel_obj.relationship_id,
                    entity_a=rel_obj.entity_a,
                    entity_b=rel_obj.entity_b,
                    relationship_type=rel_obj.relationship_type,
                    tick=tick,
                ).to_dict()
            )
        decayed_obj, decay_events = decay_familiarity(rel_obj, tick)
        updated_rels[rkey] = decayed_obj.to_dict()
        events.extend([e.to_dict() for e in decay_events])

    patch = {
        "relationships": updated_rels,
        "_relationships_prior_keys": tuple(sorted(updated_rels.keys())),
    }

    # Fix: Ensure state_revision is None when there's no current revision
    state_revision = context.committed_revision
    if state_revision == 0 and context.committed_revision is None:
        state_revision = None
    
    return (
        TransitionProposal(
            world_id=context.world_id,
            tick_id=context.tick_context.tick_id,
            state_revision=state_revision,
            correlation_id=context.tick_context.correlation_id,
            subject="domain.relationships",
            patch=patch,
            description="relationships domain decay & sync update",
            metadata={"domain": "relationships", "events": events},
        ),
    )


def record_social_interaction(
    ctx: Any,
    actor_id: Any,
    target_id: Any,
    interaction_type: str = "Talk",
) -> TransitionProposal:
    actor_key = str(actor_id.value) if hasattr(actor_id, "value") else str(actor_id)
    target_key = str(target_id.value) if hasattr(target_id, "value") else str(target_id)
    world_state, world_id, tick_number = _extract_context(ctx)

    rel_data = dict(world_state.get("relationships", {}))
    key = make_relationship_key(actor_key, target_key)
    existing_dict = rel_data.get(key)

    is_new = existing_dict is None
    if existing_dict is not None:
        rel_obj = Relationship.from_dict(existing_dict)
    else:
        rel_obj = Relationship(relationship_id=key, entity_a=actor_key, entity_b=target_key)

    updated_rel, events = apply_interaction(
        rel=rel_obj,
        interaction_type=interaction_type,
        actor_id=actor_key,
        target_id=target_key,
        tick=tick_number,
    )

    if is_new:
        events.insert(
            0,
            RelationshipCreated(
                relationship_id=key,
                entity_a=actor_key,
                entity_b=target_key,
                relationship_type=updated_rel.relationship_type,
                tick=tick_number,
            ),
        )

    rel_data[key] = updated_rel.to_dict()
    patch = {"relationships": rel_data}

    return TransitionProposal(
        world_id=world_id,
        tick_id=getattr(getattr(ctx, "tick_context", None), "tick_id", None),
        state_revision=None,
        correlation_id=f"social:{interaction_type}:{actor_key}:{target_key}",
        subject=f"SocialInteraction:{interaction_type}",
        patch=patch,
        description=f"{actor_key} {interaction_type} with {target_key}",
        metadata={
            "domain": "relationships",
            "actor_id": actor_key,
            "target_id": target_key,
            "interaction_type": interaction_type,
            "is_new_relationship": is_new,
            "events": [e.to_dict() for e in events],
        },
    )


def talk_to_villager(ctx: Any, actor_id: Any, target_id: Any) -> TransitionProposal:
    return record_social_interaction(ctx, actor_id, target_id, "Talk")


def converse(ctx: Any, actor_id: Any, target_id: Any) -> TransitionProposal:
    return record_social_interaction(ctx, actor_id, target_id, "Conversation")


def help_villager(ctx: Any, actor_id: Any, target_id: Any) -> TransitionProposal:
    return record_social_interaction(ctx, actor_id, target_id, "Helped")


def share_resource(ctx: Any, actor_id: Any, target_id: Any, resource_type: str = "food", quantity: float = 1.0) -> TransitionProposal:
    return record_social_interaction(ctx, actor_id, target_id, "Share")


def shared_meal(ctx: Any, actor_id: Any, target_id: Any) -> TransitionProposal:
    return record_social_interaction(ctx, actor_id, target_id, "SharedMeal")


def give_gift(ctx: Any, actor_id: Any, target_id: Any) -> TransitionProposal:
    return record_social_interaction(ctx, actor_id, target_id, "Gift")


def give_item(ctx: Any, actor_id: Any, target_id: Any) -> TransitionProposal:
    return record_social_interaction(ctx, actor_id, target_id, "Gift")


def receive_item(ctx: Any, actor_id: Any, target_id: Any) -> TransitionProposal:
    return record_social_interaction(ctx, actor_id, target_id, "Gift")


def trade_with(ctx: Any, actor_id: Any, target_id: Any) -> TransitionProposal:
    return record_social_interaction(ctx, actor_id, target_id, "Trade")


def teach_skill(ctx: Any, mentor_id: Any, student_id: Any) -> TransitionProposal:
    return record_social_interaction(ctx, mentor_id, student_id, "WorkedTogether")


def work_together(ctx: Any, actor_id: Any, target_id: Any) -> TransitionProposal:
    return record_social_interaction(ctx, actor_id, target_id, "WorkedTogether")


def visit(ctx: Any, actor_id: Any, target_id: Any) -> TransitionProposal:
    return record_social_interaction(ctx, actor_id, target_id, "Conversation")


def ignore_villager(ctx: Any, actor_id: Any, target_id: Any) -> TransitionProposal:
    return record_social_interaction(ctx, actor_id, target_id, "Ignored")


def resolve_conflict(ctx: Any, actor_id: Any, target_id: Any) -> TransitionProposal:
    return record_social_interaction(ctx, actor_id, target_id, "Conversation")


def start_conflict(ctx: Any, actor_id: Any, target_id: Any) -> TransitionProposal:
    return record_social_interaction(ctx, actor_id, target_id, "Conflict")


def compete_with(ctx: Any, actor_id: Any, target_id: Any) -> TransitionProposal:
    return record_social_interaction(ctx, actor_id, target_id, "Competition")


def _load_rel_dict(kernel_or_state: Any) -> dict[str, Any]:
    if hasattr(kernel_or_state, "current_state"):
        return dict(dict(kernel_or_state.current_state).get("relationships", {}))
    if isinstance(kernel_or_state, Mapping):
        as_dict = dict(kernel_or_state)
        if "relationships" in as_dict:
            inner = as_dict["relationships"]
            if isinstance(inner, Mapping):
                return dict(inner)
            return {}
        rel_keys = any(isinstance(k, str) and str(k).startswith("rel:") for k in as_dict.keys())
        if rel_keys:
            return as_dict
        return {}
    return {}


def rank_partners(
    kernel_or_state: Any,
    actor_id: Any,
    candidate_ids: Sequence[Any],
    context: str = "general",
) -> list[tuple[str, float]]:
    rels = _load_rel_dict(kernel_or_state)
    actor_key = str(actor_id.value) if hasattr(actor_id, "value") else str(actor_id)
    cand_keys = [(str(c.value) if hasattr(c, "value") else str(c)) for c in candidate_ids]
    return rank_social_partners(rels, actor_key, cand_keys, context=context)


def trade_preferences(
    kernel_or_state: Any,
    actor_id: Any,
    candidate_ids: Sequence[Any],
) -> list[tuple[str, float]]:
    rels = _load_rel_dict(kernel_or_state)
    actor_key = str(actor_id.value) if hasattr(actor_id, "value") else str(actor_id)
    cand_keys = [(str(c.value) if hasattr(c, "value") else str(c)) for c in candidate_ids]
    return prefer_trade_partner(rels, actor_key, cand_keys)


def help_preferences(
    kernel_or_state: Any,
    actor_id: Any,
    candidate_ids: Sequence[Any],
) -> list[tuple[str, float]]:
    rels = _load_rel_dict(kernel_or_state)
    actor_key = str(actor_id.value) if hasattr(actor_id, "value") else str(actor_id)
    cand_keys = [(str(c.value) if hasattr(c, "value") else str(c)) for c in candidate_ids]
    return prefer_help_partner(rels, actor_key, cand_keys)


def conversation_preferences(
    kernel_or_state: Any,
    actor_id: Any,
    candidate_ids: Sequence[Any],
) -> list[tuple[str, float]]:
    rels = _load_rel_dict(kernel_or_state)
    actor_key = str(actor_id.value) if hasattr(actor_id, "value") else str(actor_id)
    cand_keys = [(str(c.value) if hasattr(c, "value") else str(c)) for c in candidate_ids]
    return prefer_conversation_partner(rels, actor_key, cand_keys)


def cooperation_preferences(
    kernel_or_state: Any,
    actor_id: Any,
    candidate_ids: Sequence[Any],
) -> list[tuple[str, float]]:
    rels = _load_rel_dict(kernel_or_state)
    actor_key = str(actor_id.value) if hasattr(actor_id, "value") else str(actor_id)
    cand_keys = [(str(c.value) if hasattr(c, "value") else str(c)) for c in candidate_ids]
    return prefer_cooperation_partner(rels, actor_key, cand_keys)


def leader_preferences(
    kernel_or_state: Any,
    actor_id: Any,
    candidate_ids: Sequence[Any],
) -> list[tuple[str, float]]:
    rels = _load_rel_dict(kernel_or_state)
    actor_key = str(actor_id.value) if hasattr(actor_id, "value") else str(actor_id)
    cand_keys = [(str(c.value) if hasattr(c, "value") else str(c)) for c in candidate_ids]
    return prefer_leader_candidate(rels, actor_key, cand_keys)


def willingness_to_cooperate(kernel_or_state: Any, actor_id: Any, target_id: Any) -> float:
    rels = _load_rel_dict(kernel_or_state)
    actor_key = str(actor_id.value) if hasattr(actor_id, "value") else str(actor_id)
    target_key = str(target_id.value) if hasattr(target_id, "value") else str(target_id)
    return cooperation_willingness(rels, actor_key, target_key)


def willingness_to_share(kernel_or_state: Any, actor_id: Any, target_id: Any) -> float:
    rels = _load_rel_dict(kernel_or_state)
    actor_key = str(actor_id.value) if hasattr(actor_id, "value") else str(actor_id)
    target_key = str(target_id.value) if hasattr(target_id, "value") else str(target_id)
    return resource_sharing_willingness(rels, actor_key, target_key)


def generate_relationship_goals(kernel: Any) -> list[Any]:
    manager = kernel.planner_engine.goal_manager
    goals = []

    human_entities = [e for e in kernel.entity_registry.list_entities() if getattr(e, "type", "") == "human"]
    if len(human_entities) < 2:
        return goals

    world_state = dict(kernel.current_state)
    rel_data = dict(world_state.get("relationships", {}))

    actor = human_entities[0]

    candidates = [e for e in human_entities[1:5]]
    if not candidates:
        return goals

    cand_keys = [str(e.display_name) for e in candidates]
    ranked = prefer_conversation_partner(rel_data, str(actor.display_name), cand_keys)
    if not ranked:
        return goals

    best_key = ranked[0][0]
    best_score = ranked[0][1]
    target = next((e for e in candidates if str(e.display_name) == best_key), candidates[0])

    key = make_relationship_key(str(actor.display_name), str(target.display_name))
    rel_dict = rel_data.get(key)
    fam = 0.0
    if rel_dict is not None:
        fam = float(rel_dict.get("familiarity", 0.0))

    if fam < 0.5 or best_score < 0.7:
        goal = manager.create_goal(
            subject=f"Talk to {target.display_name}",
            kind="Talk",
            entity_id=actor.entity_id,
            target_state={"target_id": target.entity_id, "action": "Conversation"},
            priority=max(8, int(round((1.0 - best_score) * 20))),
            created_tick=kernel.current_tick_number,
            metadata={
                "target_name": target.display_name,
                "preference_score": best_score,
                "familiarity": fam,
            },
        )
        goals.append(goal)

    if best_score > 0.7 and fam < 0.7:
        goal2 = manager.create_goal(
            subject=f"Visit {target.display_name}",
            kind="Visit",
            entity_id=actor.entity_id,
            target_state={"target_id": target.entity_id, "action": "Visit"},
            priority=10,
            created_tick=kernel.current_tick_number,
            metadata={"target_name": target.display_name, "preference_score": best_score},
        )
        goals.append(goal2)

    return goals
