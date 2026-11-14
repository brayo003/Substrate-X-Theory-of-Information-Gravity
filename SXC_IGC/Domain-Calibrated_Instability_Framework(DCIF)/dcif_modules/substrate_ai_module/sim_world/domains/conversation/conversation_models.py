from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

CONVERSATION_TOPICS: tuple[str, ...] = (
    "DailyLife",
    "Work",
    "Needs",
    "Food",
    "Weather",
    "Village",
    "Trade",
    "Agriculture",
    "Family",
    "Health",
    "Relationships",
    "Planning",
    "Teaching",
    "Conflict",
    "Celebration",
    "Emergency",
)

CONVERSATION_INTENTS: tuple[str, ...] = (
    "Greeting",
    "Ask",
    "Answer",
    "Inform",
    "Request",
    "Offer",
    "Teach",
    "Warn",
    "Thank",
    "Comfort",
    "Negotiate",
    "Refuse",
    "Agree",
    "Disagree",
    "Apologize",
    "Celebrate",
)

CONVERSATION_OUTCOMES: tuple[str, ...] = (
    "KnowledgeShared",
    "AgreementReached",
    "ConflictEscalated",
    "ConflictResolved",
    "SkillTaught",
    "TradeNegotiated",
    "SupportGiven",
    "GreetingExchanged",
    "DiscussionCompleted",
    "WarningIssued",
    "ComfortGiven",
    "RequestFulfilled",
    "RequestRefused",
)


@dataclass(slots=True)
class ConversationParticipant:
    entity_id: str
    role: str = "Participant"
    turns_spoken: int = 0
    turns_listened: int = 0
    knowledge_received: tuple[str, ...] = ()
    knowledge_shared: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        self.entity_id = str(self.entity_id)
        self.role = str(self.role)
        self.turns_spoken = int(self.turns_spoken)
        self.turns_listened = int(self.turns_listened)
        self.knowledge_received = tuple(str(k) for k in self.knowledge_received)
        self.knowledge_shared = tuple(str(k) for k in self.knowledge_shared)

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "role": self.role,
            "turns_spoken": self.turns_spoken,
            "turns_listened": self.turns_listened,
            "knowledge_received": list(self.knowledge_received),
            "knowledge_shared": list(self.knowledge_shared),
        }

    @staticmethod
    def from_dict(data: Mapping[str, Any]) -> ConversationParticipant:
        return ConversationParticipant(
            entity_id=str(data.get("entity_id", "p_1")),
            role=str(data.get("role", "Participant")),
            turns_spoken=int(data.get("turns_spoken", 0)),
            turns_listened=int(data.get("turns_listened", 0)),
            knowledge_received=tuple(str(k) for k in data.get("knowledge_received", ())),
            knowledge_shared=tuple(str(k) for k in data.get("knowledge_shared", ())),
        )


@dataclass(slots=True)
class ConversationTopic:
    topic: str
    sub_topic: str = ""
    urgency: float = 0.0
    importance: float = 0.0

    def __post_init__(self) -> None:
        self.topic = str(self.topic)
        self.sub_topic = str(self.sub_topic)
        self.urgency = max(0.0, min(1.0, float(self.urgency)))
        self.importance = max(0.0, min(1.0, float(self.importance)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "topic": self.topic,
            "sub_topic": self.sub_topic,
            "urgency": self.urgency,
            "importance": self.importance,
        }

    @staticmethod
    def from_dict(data: Mapping[str, Any]) -> ConversationTopic:
        return ConversationTopic(
            topic=str(data.get("topic", "DailyLife")),
            sub_topic=str(data.get("sub_topic", "")),
            urgency=float(data.get("urgency", 0.0)),
            importance=float(data.get("importance", 0.0)),
        )


@dataclass(slots=True)
class ConversationTurn:
    turn_index: int
    speaker_id: str
    listener_id: str
    topic: str
    intent: str
    information_exchanged: tuple[str, ...] = ()
    result: str = "Heard"
    tick: int = 0

    def __post_init__(self) -> None:
        self.turn_index = int(self.turn_index)
        self.speaker_id = str(self.speaker_id)
        self.listener_id = str(self.listener_id)
        self.topic = str(self.topic)
        self.intent = str(self.intent)
        self.information_exchanged = tuple(str(i) for i in self.information_exchanged)
        self.result = str(self.result)
        self.tick = int(self.tick)

    def to_dict(self) -> dict[str, Any]:
        return {
            "turn_index": self.turn_index,
            "speaker_id": self.speaker_id,
            "listener_id": self.listener_id,
            "topic": self.topic,
            "intent": self.intent,
            "information_exchanged": list(self.information_exchanged),
            "result": self.result,
            "tick": self.tick,
        }

    @staticmethod
    def from_dict(data: Mapping[str, Any]) -> ConversationTurn:
        return ConversationTurn(
            turn_index=int(data.get("turn_index", 0)),
            speaker_id=str(data.get("speaker_id", "sp_1")),
            listener_id=str(data.get("listener_id", "ls_1")),
            topic=str(data.get("topic", "DailyLife")),
            intent=str(data.get("intent", "Inform")),
            information_exchanged=tuple(str(i) for i in data.get("information_exchanged", ())),
            result=str(data.get("result", "Heard")),
            tick=int(data.get("tick", 0)),
        )


@dataclass(slots=True)
class ConversationMemory:
    entity_id: str
    conversation_id: str
    topic: str
    participants: tuple[str, ...] = ()
    outcome: str = ""
    importance: float = 0.0
    recorded_tick: int = 0
    knowledge_gained: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        self.entity_id = str(self.entity_id)
        self.conversation_id = str(self.conversation_id)
        self.topic = str(self.topic)
        self.participants = tuple(str(p) for p in self.participants)
        self.outcome = str(self.outcome)
        self.importance = max(0.0, min(1.0, float(self.importance)))
        self.recorded_tick = int(self.recorded_tick)
        self.knowledge_gained = tuple(str(k) for k in self.knowledge_gained)

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "conversation_id": self.conversation_id,
            "topic": self.topic,
            "participants": list(self.participants),
            "outcome": self.outcome,
            "importance": self.importance,
            "recorded_tick": self.recorded_tick,
            "knowledge_gained": list(self.knowledge_gained),
        }

    @staticmethod
    def from_dict(data: Mapping[str, Any]) -> ConversationMemory:
        return ConversationMemory(
            entity_id=str(data.get("entity_id", "mem_1")),
            conversation_id=str(data.get("conversation_id", "conv_1")),
            topic=str(data.get("topic", "DailyLife")),
            participants=tuple(str(p) for p in data.get("participants", ())),
            outcome=str(data.get("outcome", "")),
            importance=float(data.get("importance", 0.0)),
            recorded_tick=int(data.get("recorded_tick", 0)),
            knowledge_gained=tuple(str(k) for k in data.get("knowledge_gained", ())),
        )


@dataclass(slots=True)
class ConversationOutcome:
    outcome_type: str
    summary: str = ""
    knowledge_transferred: tuple[str, ...] = ()
    relationship_delta: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
    affected_entities: tuple[str, ...] = ()
    future_goal_hints: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        self.outcome_type = str(self.outcome_type)
        self.summary = str(self.summary)
        self.knowledge_transferred = tuple(str(k) for k in self.knowledge_transferred)
        self.relationship_delta = tuple(max(-1.0, min(1.0, float(v))) for v in self.relationship_delta)
        while len(self.relationship_delta) < 4:
            self.relationship_delta = self.relationship_delta + (0.0,)
        self.relationship_delta = self.relationship_delta[:4]
        self.affected_entities = tuple(str(e) for e in self.affected_entities)
        self.future_goal_hints = tuple(str(g) for g in self.future_goal_hints)

    def to_dict(self) -> dict[str, Any]:
        return {
            "outcome_type": self.outcome_type,
            "summary": self.summary,
            "knowledge_transferred": list(self.knowledge_transferred),
            "relationship_delta": list(self.relationship_delta),
            "affected_entities": list(self.affected_entities),
            "future_goal_hints": list(self.future_goal_hints),
        }

    @staticmethod
    def from_dict(data: Mapping[str, Any]) -> ConversationOutcome:
        return ConversationOutcome(
            outcome_type=str(data.get("outcome_type", "DiscussionCompleted")),
            summary=str(data.get("summary", "")),
            knowledge_transferred=tuple(str(k) for k in data.get("knowledge_transferred", ())),
            relationship_delta=tuple(float(v) for v in data.get("relationship_delta", (0.0, 0.0, 0.0, 0.0))),
            affected_entities=tuple(str(e) for e in data.get("affected_entities", ())),
            future_goal_hints=tuple(str(g) for g in data.get("future_goal_hints", ())),
        )


@dataclass(slots=True)
class ConversationState:
    phase: str = "Idle"
    current_speaker_idx: int = 0
    turns_completed: int = 0
    knowledge_shared_list: tuple[str, ...] = ()
    agreements_reached: tuple[str, ...] = ()
    conflicts_recorded: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        self.phase = str(self.phase)
        self.current_speaker_idx = max(0, int(self.current_speaker_idx))
        self.turns_completed = max(0, int(self.turns_completed))
        self.knowledge_shared_list = tuple(str(k) for k in self.knowledge_shared_list)
        self.agreements_reached = tuple(str(a) for a in self.agreements_reached)
        self.conflicts_recorded = tuple(str(c) for c in self.conflicts_recorded)

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase": self.phase,
            "current_speaker_idx": self.current_speaker_idx,
            "turns_completed": self.turns_completed,
            "knowledge_shared_list": list(self.knowledge_shared_list),
            "agreements_reached": list(self.agreements_reached),
            "conflicts_recorded": list(self.conflicts_recorded),
        }

    @staticmethod
    def from_dict(data: Mapping[str, Any]) -> ConversationState:
        return ConversationState(
            phase=str(data.get("phase", "Idle")),
            current_speaker_idx=int(data.get("current_speaker_idx", 0)),
            turns_completed=int(data.get("turns_completed", 0)),
            knowledge_shared_list=tuple(str(k) for k in data.get("knowledge_shared_list", ())),
            agreements_reached=tuple(str(a) for a in data.get("agreements_reached", ())),
            conflicts_recorded=tuple(str(c) for c in data.get("conflicts_recorded", ())),
        )


@dataclass(slots=True)
class Conversation:
    conversation_id: str
    participants: tuple[ConversationParticipant, ...]
    location: str
    start_tick: int
    topic: ConversationTopic
    end_tick: int = 0
    turn_history: tuple[ConversationTurn, ...] = ()
    outcome: ConversationOutcome | None = None
    state: ConversationState = field(default_factory=ConversationState)

    def __post_init__(self) -> None:
        self.conversation_id = str(self.conversation_id)
        self.participants = tuple(
            p if isinstance(p, ConversationParticipant) else ConversationParticipant.from_dict(p)
            for p in self.participants
        )
        self.location = str(self.location)
        self.start_tick = int(self.start_tick)
        self.topic = self.topic if isinstance(self.topic, ConversationTopic) else ConversationTopic.from_dict(self.topic)
        self.end_tick = int(self.end_tick)
        self.turn_history = tuple(
            t if isinstance(t, ConversationTurn) else ConversationTurn.from_dict(t)
            for t in self.turn_history
        )
        if self.outcome is not None and not isinstance(self.outcome, ConversationOutcome):
            self.outcome = ConversationOutcome.from_dict(self.outcome)
        self.state = self.state if isinstance(self.state, ConversationState) else ConversationState.from_dict(self.state)

    def participant_ids(self) -> list[str]:
        return sorted(set(p.entity_id for p in self.participants))

    def to_dict(self) -> dict[str, Any]:
        return {
            "conversation_id": self.conversation_id,
            "participants": [p.to_dict() for p in self.participants],
            "location": self.location,
            "start_tick": self.start_tick,
            "end_tick": self.end_tick,
            "topic": self.topic.to_dict(),
            "turn_history": [t.to_dict() for t in self.turn_history],
            "outcome": None if self.outcome is None else self.outcome.to_dict(),
            "state": self.state.to_dict(),
        }

    @staticmethod
    def from_dict(data: Mapping[str, Any]) -> Conversation:
        outcome_raw = data.get("outcome", None)
        return Conversation(
            conversation_id=str(data.get("conversation_id", "conv_1")),
            participants=tuple(ConversationParticipant.from_dict(p) for p in data.get("participants", ())),
            location=str(data.get("location", "unknown")),
            start_tick=int(data.get("start_tick", 0)),
            end_tick=int(data.get("end_tick", 0)),
            topic=ConversationTopic.from_dict(data.get("topic", {"topic": "DailyLife"})),
            turn_history=tuple(ConversationTurn.from_dict(t) for t in data.get("turn_history", ())),
            outcome=None if outcome_raw is None else ConversationOutcome.from_dict(outcome_raw),
            state=ConversationState.from_dict(data.get("state", {})),
        )
