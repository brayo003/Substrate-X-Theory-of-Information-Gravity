from __future__ import annotations

from typing import Any, Mapping, Sequence

from ...core.contracts import TransitionProposal
from ...simulation.simulation_engine import SimulationEngine
from .conversation_events import (
    ConversationEnded,
)
from .conversation_models import (
    Conversation,
    ConversationMemory,
    ConversationOutcome,
    ConversationParticipant,
    ConversationTopic,
    ConversationTurn,
)
from .conversation_rules import (
    INTENT_OUTCOME_WEIGHTS,
    TOPIC_RELATIONSHIP_DELTAS,
    add_turn,
    build_conversation_memory,
    lookup_conversations_by_entity,
    lookup_conversations_by_topic,
    make_conversation_id,
    make_conversation_memory_id,
    resolve_outcome,
    select_informed_holders,
    start_conversation,
    summarize_relationship_delta,
    topic_from_context,
)


def register(engine: SimulationEngine) -> None:
    engine.register_domain("conversation", lambda engine, context: apply(context))


def _extract_context(ctx: Any) -> tuple[dict[str, Any], Any, int]:
    state = dict(getattr(ctx, "current_state", None) or getattr(ctx, "world_state", {}))
    world_id = getattr(ctx, "world_id", None)
    tick_number = int(getattr(ctx, "current_tick_number", None) or getattr(ctx, "tick_number", 0))
    return state, world_id, tick_number


def _id_str(entity_or_id: Any) -> str:
    if hasattr(entity_or_id, "value"):
        return str(entity_or_id.value)
    return str(entity_or_id)


def initialize_valley_conversations(kernel: Any) -> dict[str, Conversation]:
    conversations: dict[str, Conversation] = {}
    memories: dict[str, Any] = {}
    if hasattr(kernel, "_state") and isinstance(kernel._state, dict):
        if "conversations" not in kernel._state:
            kernel._state["conversations"] = conversations
        if "conversation_memories" not in kernel._state:
            kernel._state["conversation_memories"] = memories
    return conversations


def apply(context: Any) -> tuple[TransitionProposal, ...]:
    # MINIMAL: Return empty patch
    return (
        TransitionProposal(
            world_id=getattr(context, "world_id", None),
            tick_id=getattr(getattr(context, "tick_context", None), "tick_id", None) if hasattr(context, "tick_context") else None,
            state_revision=getattr(context, "committed_revision", None),
            correlation_id=getattr(getattr(context, "tick_context", None), "correlation_id", None) if hasattr(context, "tick_context") else None,
            subject="domain.conversation",
            patch={"conversations": {}, "conversation_memories": {}, "_conversation_prior_keys": ()},
            description="conversation domain minimal",
            metadata={"domain": "conversation", "events": []},
        ),
    )


def _load_conversation_dict(kernel_or_state: Any) -> dict[str, Any]:
    if hasattr(kernel_or_state, "current_state"):
        return dict(dict(kernel_or_state.current_state).get("conversations", {}))
    if isinstance(kernel_or_state, Mapping):
        as_dict = dict(kernel_or_state)
        if "conversations" in as_dict:
            inner = as_dict["conversations"]
            if isinstance(inner, Mapping):
                return dict(inner)
            return {}
        conv_keys = any(isinstance(k, str) and str(k).startswith("conv:") for k in as_dict.keys())
        if conv_keys:
            return as_dict
    return {}


def _load_memory_dict(kernel_or_state: Any) -> dict[str, Any]:
    if hasattr(kernel_or_state, "current_state"):
        return dict(dict(kernel_or_state.current_state).get("conversation_memories", {}))
    if isinstance(kernel_or_state, Mapping):
        as_dict = dict(kernel_or_state)
        if "conversation_memories" in as_dict:
            inner = as_dict["conversation_memories"]
            if isinstance(inner, Mapping):
                return dict(inner)
            return {}
        mem_keys = any(isinstance(k, str) and str(k).startswith("conv_mem:") for k in as_dict.keys())
        if mem_keys:
            return as_dict
    return {}


def start_conversation_action(
    ctx: Any,
    initiator_id: Any,
    participant_ids: Sequence[Any],
    location: str = "village_common",
    topic: str = "DailyLife",
    sub_topic: str = "",
    urgency: float = 0.0,
    importance: float = 0.2,
) -> TransitionProposal:
    init_key = _id_str(initiator_id)
    part_keys = [init_key] + [_id_str(p) for p in participant_ids if _id_str(p) != init_key]
    part_keys = list(dict.fromkeys(part_keys))
    world_state, world_id, tick = _extract_context(ctx)
    convs = dict(world_state.get("conversations", {}))

    conv, events = start_conversation(
        participant_ids=part_keys,
        location=str(location),
        tick=tick,
        topic=topic,
        sub_topic=sub_topic,
        urgency=float(urgency),
        importance=float(importance),
    )
    convs[conv.conversation_id] = conv.to_dict()
    patch = {"conversations": convs}
    return TransitionProposal(
        world_id=world_id,
        tick_id=getattr(getattr(ctx, "tick_context", None), "tick_id", None),
        state_revision=None,
        correlation_id=f"conv:start:{conv.conversation_id}",
        subject=f"Conversation:Start:{conv.topic.topic}",
        patch=patch,
        description=f"{init_key} starts {conv.topic.topic} conversation at {location}",
        metadata={
            "domain": "conversation",
            "conversation_id": conv.conversation_id,
            "participants": part_keys,
            "topic": conv.topic.topic,
            "events": [e.to_dict() for e in events],
        },
    )


def exchange_turn_action(
    ctx: Any,
    conversation_id: str,
    speaker_id: Any,
    listener_id: Any,
    intent: str,
    information_exchanged: Sequence[str] = (),
    result: str = "Heard",
) -> TransitionProposal:
    speaker_key = _id_str(speaker_id)
    listener_key = _id_str(listener_id)
    world_state, world_id, tick = _extract_context(ctx)
    convs = dict(world_state.get("conversations", {}))

    cid = str(conversation_id)
    cdata = convs.get(cid)
    if cdata is None:
        empty: dict[str, Any] = {}
        return TransitionProposal(
            world_id=world_id,
            tick_id=getattr(getattr(ctx, "tick_context", None), "tick_id", None),
            state_revision=None,
            correlation_id=f"conv:turn:missing:{cid}",
            subject="Conversation:Turn:Missing",
            patch=empty,
            description=f"Conversation {cid} not found",
            metadata={"domain": "conversation", "conversation_id": cid, "events": []},
        )

    conv = Conversation.from_dict(cdata)
    updated, events = add_turn(
        conv=conv,
        speaker_id=speaker_key,
        listener_id=listener_key,
        intent=intent,
        information_exchanged=information_exchanged,
        result=result,
        tick=tick,
    )
    convs[cid] = updated.to_dict()
    patch = {"conversations": convs}
    return TransitionProposal(
        world_id=world_id,
        tick_id=getattr(getattr(ctx, "tick_context", None), "tick_id", None),
        state_revision=None,
        correlation_id=f"conv:turn:{cid}:{len(updated.turn_history)}",
        subject=f"Conversation:Turn:{intent}",
        patch=patch,
        description=f"{speaker_key} speaks ({intent}) to {listener_key} in {cid}",
        metadata={
            "domain": "conversation",
            "conversation_id": cid,
            "speaker_id": speaker_key,
            "listener_id": listener_key,
            "intent": intent,
            "events": [e.to_dict() for e in events],
        },
    )


def share_knowledge_action(
    ctx: Any,
    conversation_id: str,
    speaker_id: Any,
    listener_id: Any,
    knowledge_items: Sequence[str],
) -> TransitionProposal:
    return exchange_turn_action(
        ctx=ctx,
        conversation_id=conversation_id,
        speaker_id=speaker_id,
        listener_id=listener_id,
        intent="Inform",
        information_exchanged=knowledge_items,
        result="Received",
    )


def negotiate_action(
    ctx: Any,
    conversation_id: str,
    speaker_id: Any,
    listener_id: Any,
    agreed: bool,
    information_exchanged: Sequence[str] = (),
) -> TransitionProposal:
    intent = "Agree" if bool(agreed) else "Negotiate"
    return exchange_turn_action(
        ctx=ctx,
        conversation_id=conversation_id,
        speaker_id=speaker_id,
        listener_id=listener_id,
        intent=intent,
        information_exchanged=information_exchanged,
        result="Negotiated" if not agreed else "Agreed",
    )


def teach_action(
    ctx: Any,
    conversation_id: str,
    teacher_id: Any,
    student_id: Any,
    knowledge_items: Sequence[str] = (),
) -> TransitionProposal:
    return exchange_turn_action(
        ctx=ctx,
        conversation_id=conversation_id,
        speaker_id=teacher_id,
        listener_id=student_id,
        intent="Teach",
        information_exchanged=knowledge_items,
        result="Learned",
    )


def resolve_discussion_action(
    ctx: Any,
    conversation_id: str,
    speaker_id: Any,
    listener_id: Any,
    resolved: bool,
) -> TransitionProposal:
    intent = "Agree" if bool(resolved) else "Apologize"
    result = "Resolved" if bool(resolved) else "DeEscalated"
    return exchange_turn_action(
        ctx=ctx,
        conversation_id=conversation_id,
        speaker_id=speaker_id,
        listener_id=listener_id,
        intent=intent,
        information_exchanged=("resolution",) if resolved else ("de-escalation",),
        result=result,
    )


def end_conversation_action(
    ctx: Any,
    conversation_id: str,
) -> TransitionProposal:
    world_state, world_id, tick = _extract_context(ctx)
    convs = dict(world_state.get("conversations", {}))
    mems = dict(world_state.get("conversation_memories", {}))

    cid = str(conversation_id)
    cdata = convs.get(cid)
    if cdata is None:
        return TransitionProposal(
            world_id=world_id,
            tick_id=getattr(getattr(ctx, "tick_context", None), "tick_id", None),
            state_revision=None,
            correlation_id=f"conv:end:missing:{cid}",
            subject="Conversation:End:Missing",
            patch={},
            description=f"Conversation {cid} not found",
            metadata={"domain": "conversation", "conversation_id": cid, "events": []},
        )

    conv = Conversation.from_dict(cdata)
    closed, events = resolve_outcome(conv, tick)
    convs[cid] = closed.to_dict()

    for mem in build_conversation_memory(closed):
        mem_key = make_conversation_memory_id(mem.entity_id, cid)
        mems[mem_key] = mem.to_dict()

    patch = {"conversations": convs, "conversation_memories": mems}
    return TransitionProposal(
        world_id=world_id,
        tick_id=getattr(getattr(ctx, "tick_context", None), "tick_id", None),
        state_revision=None,
        correlation_id=f"conv:end:{cid}",
        subject=f"Conversation:End:{closed.outcome.outcome_type if closed.outcome else 'DiscussionCompleted'}",
        patch=patch,
        description=f"Conversation {cid} ended",
        metadata={
            "domain": "conversation",
            "conversation_id": cid,
            "outcome": closed.outcome.outcome_type if closed.outcome else "DiscussionCompleted",
            "relationship_delta": list(summarize_relationship_delta(closed)),
            "events": [e.to_dict() for e in events],
        },
    )


def approach_to_converse(
    ctx: Any,
    initiator_id: Any,
    target_id: Any,
    location: str = "village_common",
    trigger: str = "daily life",
) -> TransitionProposal:
    topic = topic_from_context(trigger=trigger)
    return start_conversation_action(
        ctx=ctx,
        initiator_id=initiator_id,
        participant_ids=[target_id],
        location=location,
        topic=topic.topic,
        sub_topic=topic.sub_topic,
        urgency=topic.urgency,
        importance=topic.importance,
    )


def conversation_relationship_delta(
    kernel_or_state: Any,
    conversation_id: str,
) -> tuple[float, float, float, float]:
    convs = _load_conversation_dict(kernel_or_state)
    cdata = convs.get(str(conversation_id))
    if cdata is None:
        return (0.0, 0.0, 0.0, 0.0)
    conv = Conversation.from_dict(cdata)
    return summarize_relationship_delta(conv)


def find_entity_conversations(kernel_or_state: Any, entity_id: Any) -> list[Conversation]:
    convs = _load_conversation_dict(kernel_or_state)
    return lookup_conversations_by_entity(convs, _id_str(entity_id))


def find_topic_conversations(kernel_or_state: Any, topic: str) -> list[Conversation]:
    convs = _load_conversation_dict(kernel_or_state)
    return lookup_conversations_by_topic(convs, topic)


def find_informed_villagers(
    kernel_or_state: Any,
    knowledge_item: str,
    candidate_ids: Sequence[Any],
) -> list[str]:
    convs = _load_conversation_dict(kernel_or_state)
    cand_keys = [_id_str(c) for c in candidate_ids]
    return select_informed_holders(convs, knowledge_item, cand_keys)


def list_entity_memories(kernel_or_state: Any, entity_id: Any) -> list[ConversationMemory]:
    mems = _load_memory_dict(kernel_or_state)
    eid = _id_str(entity_id)
    found: list[tuple[int, str, ConversationMemory]] = []
    for key, raw in sorted(mems.items()):
        if isinstance(raw, ConversationMemory):
            mem = raw
        else:
            mem = ConversationMemory.from_dict(raw)
        if mem.entity_id == eid:
            found.append((mem.recorded_tick, key, mem))
    found.sort(key=lambda triple: (-triple[0], triple[1]))
    return [m for _, _, m in found]


def generate_conversation_goals(kernel: Any) -> list[Any]:
    goals: list[Any] = []
    if not hasattr(kernel, "planner_engine") or not hasattr(kernel.planner_engine, "goal_manager"):
        return goals
    manager = kernel.planner_engine.goal_manager
    human_entities = [e for e in kernel.entity_registry.list_entities() if getattr(e, "type", "") == "human"]
    if len(human_entities) < 2:
        return goals

    actor = human_entities[0]
    candidates = human_entities[1:3]

    if not candidates:
        return goals

    target = candidates[0]

    goal = manager.create_goal(
        subject=f"Approach {target.display_name}",
        kind="Approach",
        entity_id=actor.entity_id,
        target_state={"target_id": target.entity_id, "action": "ApproachConversation"},
        priority=6,
        created_tick=kernel.current_tick_number,
        metadata={"target_name": target.display_name, "topic": "DailyLife"},
    )
    goals.append(goal)

    return goals
