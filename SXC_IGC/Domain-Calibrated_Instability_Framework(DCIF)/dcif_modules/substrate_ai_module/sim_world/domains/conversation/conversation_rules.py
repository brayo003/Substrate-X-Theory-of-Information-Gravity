from __future__ import annotations

from typing import Any, Mapping, Sequence

from .conversation_events import (
    AgreementReached,
    ConflictOccurred,
    ConversationEnded,
    ConversationStarted,
    ConversationTurnCompleted,
    KnowledgeShared,
    QuestionAnswered,
    QuestionAsked,
    TeachingOccurred,
)
from .conversation_models import (
    CONVERSATION_INTENTS,
    CONVERSATION_OUTCOMES,
    CONVERSATION_TOPICS,
    Conversation,
    ConversationMemory,
    ConversationOutcome,
    ConversationParticipant,
    ConversationState,
    ConversationTopic,
    ConversationTurn,
)

INTENT_OUTCOME_WEIGHTS: dict[str, dict[str, float]] = {
    "Greeting": {"trust": 0.01, "respect": 0.00, "familiarity": 0.03, "affinity": 0.01},
    "Ask": {"trust": 0.00, "respect": 0.00, "familiarity": 0.02, "affinity": 0.00},
    "Answer": {"trust": 0.02, "respect": 0.01, "familiarity": 0.02, "affinity": 0.01},
    "Inform": {"trust": 0.02, "respect": 0.01, "familiarity": 0.03, "affinity": 0.01},
    "Request": {"trust": 0.00, "respect": 0.00, "familiarity": 0.01, "affinity": 0.00},
    "Offer": {"trust": 0.03, "respect": 0.01, "familiarity": 0.02, "affinity": 0.02},
    "Teach": {"trust": 0.04, "respect": 0.06, "familiarity": 0.03, "affinity": 0.02},
    "Warn": {"trust": 0.03, "respect": 0.02, "familiarity": 0.02, "affinity": 0.01},
    "Thank": {"trust": 0.02, "respect": 0.03, "familiarity": 0.02, "affinity": 0.03},
    "Comfort": {"trust": 0.04, "respect": 0.02, "familiarity": 0.03, "affinity": 0.05},
    "Negotiate": {"trust": 0.01, "respect": 0.01, "familiarity": 0.02, "affinity": 0.00},
    "Refuse": {"trust": -0.03, "respect": -0.01, "familiarity": 0.00, "affinity": -0.02},
    "Agree": {"trust": 0.03, "respect": 0.02, "familiarity": 0.03, "affinity": 0.03},
    "Disagree": {"trust": -0.02, "respect": 0.00, "familiarity": 0.02, "affinity": -0.02},
    "Apologize": {"trust": 0.02, "respect": 0.01, "familiarity": 0.02, "affinity": 0.02},
    "Celebrate": {"trust": 0.03, "respect": 0.02, "familiarity": 0.04, "affinity": 0.05},
}

TOPIC_INTENT_MATRIX: dict[str, dict[str, tuple[str, ...]]] = {
    "DailyLife": {"Greeting", "Inform", "Ask", "Answer", "Celebrate"},
    "Work": {"Inform", "Request", "Offer", "Ask", "Answer", "Agree", "Negotiate"},
    "Needs": {"Request", "Offer", "Inform", "Ask", "Answer", "Thank"},
    "Food": {"Inform", "Ask", "Answer", "Offer", "Share" if "Share" in CONVERSATION_INTENTS else "Offer", "Thank"},
    "Weather": {"Inform", "Warn", "Ask", "Answer"},
    "Village": {"Inform", "Ask", "Answer", "Discuss" if "Discuss" in CONVERSATION_INTENTS else "Inform", "Offer"},
    "Trade": {"Negotiate", "Offer", "Request", "Agree", "Refuse", "Inform"},
    "Agriculture": {"Inform", "Teach", "Ask", "Answer", "Offer"},
    "Family": {"Greeting", "Inform", "Comfort", "Celebrate", "Thank", "Ask", "Answer"},
    "Health": {"Inform", "Warn", "Ask", "Answer", "Comfort"},
    "Relationships": {"Inform", "Ask", "Answer", "Comfort", "Celebrate"},
    "Planning": {"Inform", "Request", "Offer", "Agree", "Ask", "Answer"},
    "Teaching": {"Teach", "Ask", "Answer", "Inform", "Thank"},
    "Conflict": {"Negotiate", "Disagree", "Refuse", "Apologize", "Agree"},
    "Celebration": {"Greeting", "Celebrate", "Inform", "Thank", "Offer"},
    "Emergency": {"Warn", "Inform", "Request", "Offer", "Agree", "Thank"},
}

TOPIC_RELATIONSHIP_DELTAS: dict[str, tuple[float, float, float, float]] = {
    "DailyLife": (0.02, 0.01, 0.03, 0.02),
    "Work": (0.03, 0.03, 0.02, 0.01),
    "Needs": (0.03, 0.01, 0.02, 0.03),
    "Food": (0.03, 0.01, 0.03, 0.03),
    "Weather": (0.02, 0.01, 0.02, 0.01),
    "Village": (0.02, 0.02, 0.03, 0.02),
    "Trade": (0.03, 0.02, 0.02, 0.01),
    "Agriculture": (0.02, 0.02, 0.02, 0.01),
    "Family": (0.03, 0.02, 0.03, 0.04),
    "Health": (0.03, 0.02, 0.02, 0.03),
    "Relationships": (0.03, 0.02, 0.03, 0.04),
    "Planning": (0.01, 0.02, 0.02, 0.01),
    "Teaching": (0.04, 0.06, 0.03, 0.02),
    "Conflict": (-0.10, -0.05, 0.02, -0.10),
    "Celebration": (0.03, 0.02, 0.04, 0.05),
    "Emergency": (0.02, 0.03, 0.02, 0.02),
}


def make_conversation_id(participant_ids: Sequence[str], tick: int) -> str:
    sorted_ids = sorted(str(p) for p in participant_ids)
    ids_part = "_".join(sorted_ids)
    return f"conv:{tick}:{ids_part}"


def make_conversation_memory_id(entity_id: str, conversation_id: str) -> str:
    return f"conv_mem:{conversation_id}:{entity_id}"


def _add_relationship_delta(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
    return (
        max(-1.0, min(1.0, a[0] + b[0])),
        max(-1.0, min(1.0, a[1] + b[1])),
        max(-1.0, min(1.0, a[2] + b[2])),
        max(-1.0, min(1.0, a[3] + b[3])),
    )


def _normalize_topic(topic_name: str) -> str:
    if topic_name in CONVERSATION_TOPICS:
        return topic_name
    lookup = {t.lower(): t for t in CONVERSATION_TOPICS}
    return lookup.get(str(topic_name).lower().replace(" ", ""), "DailyLife")


def _normalize_intent(intent_name: str) -> str:
    if intent_name in CONVERSATION_INTENTS:
        return intent_name
    lookup = {i.lower(): i for i in CONVERSATION_INTENTS}
    return lookup.get(str(intent_name).lower(), "Inform")


def start_conversation(
    participant_ids: Sequence[str],
    location: str,
    tick: int,
    topic: str = "DailyLife",
    sub_topic: str = "",
    urgency: float = 0.0,
    importance: float = 0.2,
) -> tuple[Conversation, list[Any]]:
    norm_topic = _normalize_topic(topic)
    sorted_pids = sorted(str(p) for p in participant_ids)
    if len(sorted_pids) < 2:
        raise ValueError(f"Conversation requires at least 2 participants, got {len(sorted_pids)}: {sorted_pids}")
    participants = tuple(
        ConversationParticipant(
            entity_id=pid,
            role="Initiator" if idx == 0 else "Participant",
        )
        for idx, pid in enumerate(sorted_pids)
    )
    conv = Conversation(
        conversation_id=make_conversation_id(sorted_pids, tick),
        participants=participants,
        location=str(location),
        start_tick=int(tick),
        topic=ConversationTopic(topic=norm_topic, sub_topic=sub_topic, urgency=urgency, importance=importance),
        state=ConversationState(phase="Started", current_speaker_idx=0, turns_completed=0),
    )
    events = [
        ConversationStarted(
            conversation_id=conv.conversation_id,
            participants=tuple(sorted_pids),
            location=conv.location,
            topic=norm_topic,
            tick=int(tick),
        )
    ]
    return conv, events


def add_turn(
    conv: Conversation,
    speaker_id: str,
    listener_id: str,
    intent: str,
    information_exchanged: Sequence[str] = (),
    result: str = "Heard",
    tick: int = 0,
) -> tuple[Conversation, list[Any]]:
    speaker = str(speaker_id)
    listener = str(listener_id)
    norm_intent = _normalize_intent(intent)

    participant_ids = [p.entity_id for p in conv.participants]
    if speaker not in participant_ids or listener not in participant_ids:
        return conv, []

    turn_index = len(conv.turn_history)
    turn = ConversationTurn(
        turn_index=turn_index,
        speaker_id=speaker,
        listener_id=listener,
        topic=conv.topic.topic,
        intent=norm_intent,
        information_exchanged=tuple(str(i) for i in information_exchanged),
        result=str(result),
        tick=int(tick),
    )

    new_participants_list: list[ConversationParticipant] = []
    for p in conv.participants:
        if p.entity_id == speaker:
            shared = tuple(sorted(set(p.knowledge_shared + tuple(str(i) for i in information_exchanged))))
            new_p = ConversationParticipant(
                entity_id=p.entity_id,
                role=p.role,
                turns_spoken=p.turns_spoken + 1,
                turns_listened=p.turns_listened,
                knowledge_received=p.knowledge_received,
                knowledge_shared=shared,
            )
        elif p.entity_id == listener:
            received = tuple(sorted(set(p.knowledge_received + tuple(str(i) for i in information_exchanged))))
            new_p = ConversationParticipant(
                entity_id=p.entity_id,
                role=p.role,
                turns_spoken=p.turns_spoken,
                turns_listened=p.turns_listened + 1,
                knowledge_received=received,
                knowledge_shared=p.knowledge_shared,
            )
        else:
            new_p = p
        new_participants_list.append(new_p)

    next_idx = participant_ids.index(speaker)
    current_idx = next_idx
    new_speaker_idx = (current_idx + 1) % len(participant_ids)

    events: list[Any] = [
        ConversationTurnCompleted(
            conversation_id=conv.conversation_id,
            turn_index=turn_index,
            speaker_id=speaker,
            listener_id=listener,
            intent=norm_intent,
            topic=conv.topic.topic,
            tick=int(tick),
        )
    ]

    if norm_intent == "Ask":
        events.append(
            QuestionAsked(
                conversation_id=conv.conversation_id,
                questioner_id=speaker,
                responder_id=listener,
                question_topic=conv.topic.topic,
                tick=int(tick),
            )
        )
    if norm_intent == "Answer":
        prev_ask = any(
            t.intent == "Ask" and t.listener_id == speaker and t.speaker_id == listener for t in conv.turn_history
        )
        if prev_ask:
            events.append(
                QuestionAnswered(
                    conversation_id=conv.conversation_id,
                    responder_id=speaker,
                    questioner_id=listener,
                    question_topic=conv.topic.topic,
                    answer_result=str(result),
                    tick=int(tick),
                )
            )
    if norm_intent == "Teach":
        events.append(
            TeachingOccurred(
                conversation_id=conv.conversation_id,
                teacher_id=speaker,
                student_id=listener,
                taught_topic=conv.topic.topic,
                tick=int(tick),
            )
        )
    if norm_intent in ("Disagree", "Refuse") and conv.topic.topic == "Conflict":
        events.append(
            ConflictOccurred(
                conversation_id=conv.conversation_id,
                actor_id=speaker,
                opposing_id=listener,
                conflict_topic=conv.topic.topic,
                tick=int(tick),
            )
        )
    if norm_intent == "Agree":
        events.append(
            AgreementReached(
                conversation_id=conv.conversation_id,
                agreeing_entities=tuple(sorted([speaker, listener])),
                agreement_topic=conv.topic.topic,
                tick=int(tick),
            )
        )
    if information_exchanged:
        events.append(
            KnowledgeShared(
                conversation_id=conv.conversation_id,
                from_entity=speaker,
                to_entity=listener,
                knowledge_items=tuple(sorted(set(str(i) for i in information_exchanged))),
                tick=int(tick),
            )
        )

    knowledge_shared_list = tuple(
        sorted(set(conv.state.knowledge_shared_list + tuple(str(i) for i in information_exchanged))))
    agreements_reached = conv.state.agreements_reached
    conflicts_recorded = conv.state.conflicts_recorded
    phase = conv.state.phase
    if norm_intent == "Agree":
        agreements_reached = tuple(sorted(set(agreements_reached + (conv.topic.topic,))))
    if norm_intent in ("Disagree", "Refuse") and conv.topic.topic == "Conflict":
        conflicts_recorded = tuple(sorted(set(conflicts_recorded + (conv.topic.topic,))))
    if len(conv.turn_history) + 1 >= 1:
        phase = "Active"

    new_state = ConversationState(
        phase=phase,
        current_speaker_idx=new_speaker_idx,
        turns_completed=len(conv.turn_history) + 1,
        knowledge_shared_list=knowledge_shared_list,
        agreements_reached=agreements_reached,
        conflicts_recorded=conflicts_recorded,
    )

    new_conv = Conversation(
        conversation_id=conv.conversation_id,
        participants=tuple(new_participants_list),
        location=conv.location,
        start_tick=conv.start_tick,
        end_tick=conv.end_tick,
        topic=conv.topic,
        turn_history=conv.turn_history + (turn,),
        outcome=conv.outcome,
        state=new_state,
    )
    return new_conv, events


def resolve_outcome(conv: Conversation, end_tick: int) -> tuple[Conversation, list[Any]]:
    total_delta: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
    topic_delta = TOPIC_RELATIONSHIP_DELTAS.get(conv.topic.topic, (0.01, 0.01, 0.02, 0.01))
    total_delta = _add_relationship_delta(total_delta, topic_delta)

    for turn in conv.turn_history:
        intent_weights = INTENT_OUTCOME_WEIGHTS.get(turn.intent, {"trust": 0.0, "respect": 0.0, "familiarity": 0.0, "affinity": 0.0})
        idelta = (intent_weights.get("trust", 0.0), intent_weights.get("respect", 0.0), intent_weights.get("familiarity", 0.0), intent_weights.get("affinity", 0.0))
        total_delta = _add_relationship_delta(total_delta, idelta)

    outcome_type = "DiscussionCompleted"
    summary_parts: list[str] = [f"topic:{conv.topic.topic}"]
    if conv.topic.topic == "Teaching" and any(t.intent == "Teach" for t in conv.turn_history):
        outcome_type = "SkillTaught"
    if conv.topic.topic == "Trade" and any(t.intent == "Negotiate" for t in conv.turn_history):
        outcome_type = "TradeNegotiated"
    if conv.topic.topic == "Conflict":
        if conv.state.agreements_reached:
            outcome_type = "ConflictResolved"
        elif conv.state.conflicts_recorded:
            outcome_type = "ConflictEscalated"
    if conv.topic.topic == "Emergency" or conv.state.knowledge_shared_list:
        if outcome_type == "DiscussionCompleted" and conv.state.knowledge_shared_list:
            outcome_type = "KnowledgeShared"

    goal_hints: tuple[str, ...] = ()
    if conv.topic.topic in ("Needs", "Emergency"):
        goal_hints = ("ProvideSupport",)
    if conv.topic.topic == "Teaching":
        goal_hints = ("PracticeSkill",)
    if outcome_type == "ConflictEscalated":
        goal_hints = ("ResolveConflict",)
    if conv.topic.topic == "Trade" and outcome_type == "TradeNegotiated":
        goal_hints = ("ExecuteTrade",)

    affected_entities = tuple(p.entity_id for p in conv.participants)
    outcome = ConversationOutcome(
        outcome_type=outcome_type,
        summary="|".join(summary_parts),
        knowledge_transferred=conv.state.knowledge_shared_list,
        relationship_delta=total_delta,
        affected_entities=tuple(sorted(affected_entities)),
        future_goal_hints=goal_hints,
    )

    duration = max(0, int(end_tick) - conv.start_tick)
    events = [
        ConversationEnded(
            conversation_id=conv.conversation_id,
            outcome=outcome_type,
            duration_ticks=duration,
            tick=int(end_tick),
        )
    ]
    new_state = ConversationState(
        phase="Completed",
        current_speaker_idx=conv.state.current_speaker_idx,
        turns_completed=conv.state.turns_completed,
        knowledge_shared_list=conv.state.knowledge_shared_list,
        agreements_reached=conv.state.agreements_reached,
        conflicts_recorded=conv.state.conflicts_recorded,
    )
    new_conv = Conversation(
        conversation_id=conv.conversation_id,
        participants=conv.participants,
        location=conv.location,
        start_tick=conv.start_tick,
        end_tick=int(end_tick),
        topic=conv.topic,
        turn_history=conv.turn_history,
        outcome=outcome,
        state=new_state,
    )
    return new_conv, events


def build_conversation_memory(conv: Conversation) -> list[ConversationMemory]:
    memories: list[ConversationMemory] = []
    if conv.outcome is None:
        return memories
    if conv.state.phase != "Completed":
        return memories

    outcome_type = conv.outcome.outcome_type
    importance_base = conv.topic.importance
    if outcome_type in ("KnowledgeShared", "SkillTaught", "ConflictEscalated"):
        imp2 = 0.7
    elif conv.topic.topic == "Emergency":
        imp2 = 0.7
    else:
        imp2 = importance_base
    topic_importance = max(0.1, max(conv.topic.urgency, imp2))
    if conv.topic.topic == "Emergency":
        topic_importance = max(topic_importance, 0.9)
    for p in conv.participants:
        gained = tuple(
            sorted(
                set(
                    tuple(conv.state.knowledge_shared_list)
                    + tuple(p.knowledge_received)
                )
            )
        )
        mem = ConversationMemory(
            entity_id=p.entity_id,
            conversation_id=conv.conversation_id,
            topic=conv.topic.topic,
            participants=tuple(sorted(q.entity_id for q in conv.participants)),
            outcome=outcome_type,
            importance=round(max(0.0, min(1.0, topic_importance)), 3),
            recorded_tick=conv.end_tick,
            knowledge_gained=gained,
        )
        memories.append(mem)
    return memories


def summarize_relationship_delta(conv: Conversation) -> tuple[float, float, float, float]:
    if conv.outcome is None:
        return (0.0, 0.0, 0.0, 0.0)
    return conv.outcome.relationship_delta


def lookup_conversations_by_entity(
    conversations: Mapping[str, Conversation] | Mapping[str, Mapping[str, Any]],
    entity_id: str,
) -> list[Conversation]:
    target = str(entity_id)
    found: list[tuple[int, Conversation]] = []
    for key, raw in sorted(conversations.items()):
        if isinstance(raw, Conversation):
            conv = raw
        else:
            conv = Conversation.from_dict(raw)
        if target in conv.participant_ids():
            sort_key = (conv.end_tick if conv.end_tick > 0 else conv.start_tick, key)
            found.append((sort_key, conv))
    found.sort(key=lambda pair: (-pair[0][0], pair[0][1]))
    return [c for _, c in found]


def lookup_conversations_by_topic(
    conversations: Mapping[str, Conversation] | Mapping[str, Mapping[str, Any]],
    topic: str,
) -> list[Conversation]:
    norm = _normalize_topic(topic)
    found: list[tuple[int, str, Conversation]] = []
    for key, raw in sorted(conversations.items()):
        if isinstance(raw, Conversation):
            conv = raw
        else:
            conv = Conversation.from_dict(raw)
        if conv.topic.topic == norm:
            sort_key = (conv.end_tick if conv.end_tick > 0 else conv.start_tick, key)
            found.append((sort_key[0], sort_key[1], conv))
    found.sort(key=lambda triple: (-triple[0], triple[1]))
    return [c for _, _, c in found]


def select_informed_holders(
    conversations: Mapping[str, Conversation] | Mapping[str, Mapping[str, Any]],
    knowledge_item: str,
    candidates: Sequence[str],
) -> list[str]:
    target_knowledge = str(knowledge_item)
    candidate_set = {str(c) for c in candidates}
    holders: list[tuple[int, str]] = []
    for raw in conversations.values():
        conv = raw if isinstance(raw, Conversation) else Conversation.from_dict(raw)
        for p in conv.participants:
            if p.entity_id not in candidate_set:
                continue
            all_shared = list(p.knowledge_shared) + list(conv.state.knowledge_shared_list)
            if any(target_knowledge in str(item) for item in all_shared):
                count = sum(1 for item in all_shared if target_knowledge in str(item))
                holders.append((count, p.entity_id))
    seen: set[str] = set()
    result: list[str] = []
    for count, eid in sorted(holders, key=lambda pair: (-pair[0], pair[1])):
        if eid in seen:
            continue
        seen.add(eid)
        result.append(eid)
    return result


def topic_from_context(trigger: str, sub_topic: str = "") -> ConversationTopic:
    t_lower = str(trigger).lower()
    mapping = [
        ("emergency", "Emergency"),
        ("danger", "Emergency"),
        ("warn", "Emergency"),
        ("storm", "Weather"),
        ("rain", "Weather"),
        ("weather", "Weather"),
        ("argue", "Conflict"),
        ("fight", "Conflict"),
        ("dispute", "Conflict"),
        ("farm", "Agriculture"),
        ("field", "Agriculture"),
        ("harvest", "Agriculture"),
        ("crop", "Agriculture"),
        ("teach", "Teaching"),
        ("learn", "Teaching"),
        ("hungry", "Needs"),
        ("need", "Needs"),
        ("want", "Needs"),
        ("trade", "Trade"),
        ("buy", "Trade"),
        ("sell", "Trade"),
        ("negotiate", "Trade"),
        ("food", "Food"),
        ("eat", "Food"),
        ("meal", "Food"),
        ("dinner", "Food"),
        ("health", "Health"),
        ("sick", "Health"),
        ("work", "Work"),
        ("friend", "Relationships"),
        ("relationship", "Relationships"),
        ("family", "Family"),
        ("plan", "Planning"),
        ("celebrate", "Celebration"),
        ("festival", "Celebration"),
        ("village", "Village"),
    ]
    selected = "DailyLife"
    urgency = 0.0
    importance = 0.2
    for key, topic in mapping:
        if key in t_lower:
            selected = topic
            break
    if "emergency" in t_lower or "danger" in t_lower or "warn" in t_lower:
        urgency = 0.8
        importance = 0.8
    if "teach" in t_lower or "learn" in t_lower:
        importance = 0.6
    if "trade" in t_lower or "buy" in t_lower or "sell" in t_lower or "negotiate" in t_lower:
        importance = 0.5
    return ConversationTopic(topic=selected, sub_topic=str(sub_topic), urgency=urgency, importance=importance)
