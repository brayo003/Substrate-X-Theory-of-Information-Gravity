from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ConversationStarted:
    conversation_id: str
    participants: tuple[str, ...]
    location: str
    topic: str
    tick: int = 0
    event_type: str = field(default="ConversationStarted", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "conversation_id": self.conversation_id,
            "participants": list(self.participants),
            "location": self.location,
            "topic": self.topic,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class ConversationTurnCompleted:
    conversation_id: str
    turn_index: int
    speaker_id: str
    listener_id: str
    intent: str
    topic: str
    tick: int = 0
    event_type: str = field(default="ConversationTurnCompleted", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "conversation_id": self.conversation_id,
            "turn_index": self.turn_index,
            "speaker_id": self.speaker_id,
            "listener_id": self.listener_id,
            "intent": self.intent,
            "topic": self.topic,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class KnowledgeShared:
    conversation_id: str
    from_entity: str
    to_entity: str
    knowledge_items: tuple[str, ...]
    tick: int = 0
    event_type: str = field(default="KnowledgeShared", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "conversation_id": self.conversation_id,
            "from_entity": self.from_entity,
            "to_entity": self.to_entity,
            "knowledge_items": list(self.knowledge_items),
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class QuestionAsked:
    conversation_id: str
    questioner_id: str
    responder_id: str
    question_topic: str
    tick: int = 0
    event_type: str = field(default="QuestionAsked", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "conversation_id": self.conversation_id,
            "questioner_id": self.questioner_id,
            "responder_id": self.responder_id,
            "question_topic": self.question_topic,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class QuestionAnswered:
    conversation_id: str
    responder_id: str
    questioner_id: str
    question_topic: str
    answer_result: str
    tick: int = 0
    event_type: str = field(default="QuestionAnswered", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "conversation_id": self.conversation_id,
            "responder_id": self.responder_id,
            "questioner_id": self.questioner_id,
            "question_topic": self.question_topic,
            "answer_result": self.answer_result,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class AgreementReached:
    conversation_id: str
    agreeing_entities: tuple[str, ...]
    agreement_topic: str
    tick: int = 0
    event_type: str = field(default="AgreementReached", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "conversation_id": self.conversation_id,
            "agreeing_entities": list(self.agreeing_entities),
            "agreement_topic": self.agreement_topic,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class ConflictOccurred:
    conversation_id: str
    actor_id: str
    opposing_id: str
    conflict_topic: str
    tick: int = 0
    event_type: str = field(default="ConflictOccurred", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "conversation_id": self.conversation_id,
            "actor_id": self.actor_id,
            "opposing_id": self.opposing_id,
            "conflict_topic": self.conflict_topic,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class TeachingOccurred:
    conversation_id: str
    teacher_id: str
    student_id: str
    taught_topic: str
    tick: int = 0
    event_type: str = field(default="TeachingOccurred", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "conversation_id": self.conversation_id,
            "teacher_id": self.teacher_id,
            "student_id": self.student_id,
            "taught_topic": self.taught_topic,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class ConversationEnded:
    conversation_id: str
    outcome: str
    duration_ticks: int
    tick: int = 0
    event_type: str = field(default="ConversationEnded", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "conversation_id": self.conversation_id,
            "outcome": self.outcome,
            "duration_ticks": self.duration_ticks,
            "tick": self.tick,
        }
