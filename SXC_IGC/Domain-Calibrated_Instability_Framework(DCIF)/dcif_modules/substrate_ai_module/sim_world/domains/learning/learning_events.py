from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from .learning_models import (
    SKILL_TYPES,
    _normalize_identifier,
    _to_tuple_of_str,
)


LEARNING_EVENT_TYPES: tuple[str, ...] = (
    "SkillPracticeStarted",
    "SkillPracticeCompleted",
    "ExperienceGained",
    "LevelIncreased",
    "LessonStarted",
    "LessonCompleted",
    "TeacherAssigned",
    "ApprenticeshipStarted",
    "ApprenticeshipCompleted",
    "ObservationLearning",
    "SkillMastered",
    "KnowledgeTransferred",
)


@dataclass(frozen=True, slots=True)
class SkillPracticeStarted:
    entity_id: str
    skill_type: str
    context: str
    tick: int
    event_type: str = field(default="SkillPracticeStarted", init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "entity_id", str(self.entity_id))
        object.__setattr__(
            self, "skill_type", _normalize_identifier(self.skill_type, SKILL_TYPES, "Farming")
        )
        object.__setattr__(self, "context", str(self.context))
        object.__setattr__(self, "tick", max(0, int(self.tick)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "skill_type": self.skill_type,
            "context": self.context,
            "tick": self.tick,
            "event_type": self.event_type,
        }


@dataclass(frozen=True, slots=True)
class SkillPracticeCompleted:
    entity_id: str
    skill_type: str
    context: str
    success: bool
    tick: int
    event_type: str = field(default="SkillPracticeCompleted", init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "entity_id", str(self.entity_id))
        object.__setattr__(
            self, "skill_type", _normalize_identifier(self.skill_type, SKILL_TYPES, "Farming")
        )
        object.__setattr__(self, "context", str(self.context))
        object.__setattr__(self, "success", bool(self.success))
        object.__setattr__(self, "tick", max(0, int(self.tick)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "skill_type": self.skill_type,
            "context": self.context,
            "success": self.success,
            "tick": self.tick,
            "event_type": self.event_type,
        }


@dataclass(frozen=True, slots=True)
class ExperienceGained:
    entity_id: str
    skill_type: str
    experience_before: float
    experience_after: float
    experience_delta: float
    source: str
    tick: int
    event_type: str = field(default="ExperienceGained", init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "entity_id", str(self.entity_id))
        object.__setattr__(
            self, "skill_type", _normalize_identifier(self.skill_type, SKILL_TYPES, "Farming")
        )
        eb = max(0.0, float(self.experience_before))
        ea = max(0.0, float(self.experience_after))
        if ea < eb:
            ea = eb
        delta = ea - eb
        object.__setattr__(self, "experience_before", eb)
        object.__setattr__(self, "experience_after", ea)
        object.__setattr__(self, "experience_delta", max(0.0, delta))
        object.__setattr__(self, "source", str(self.source))
        object.__setattr__(self, "tick", max(0, int(self.tick)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "skill_type": self.skill_type,
            "experience_before": self.experience_before,
            "experience_after": self.experience_after,
            "experience_delta": self.experience_delta,
            "source": self.source,
            "tick": self.tick,
            "event_type": self.event_type,
        }


@dataclass(frozen=True, slots=True)
class LevelIncreased:
    entity_id: str
    skill_type: str
    level_before: int
    level_after: int
    experience_at_level: float
    tick: int
    event_type: str = field(default="LevelIncreased", init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "entity_id", str(self.entity_id))
        object.__setattr__(
            self, "skill_type", _normalize_identifier(self.skill_type, SKILL_TYPES, "Farming")
        )
        lb = max(0, int(self.level_before))
        la = max(lb, int(self.level_after))
        object.__setattr__(self, "level_before", lb)
        object.__setattr__(self, "level_after", la)
        object.__setattr__(self, "experience_at_level", max(0.0, float(self.experience_at_level)))
        object.__setattr__(self, "tick", max(0, int(self.tick)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "skill_type": self.skill_type,
            "level_before": self.level_before,
            "level_after": self.level_after,
            "experience_at_level": self.experience_at_level,
            "tick": self.tick,
            "event_type": self.event_type,
        }


@dataclass(frozen=True, slots=True)
class LessonStarted:
    lesson_id: str
    teacher_id: str
    student_id: str
    skill_type: str
    tick: int
    event_type: str = field(default="LessonStarted", init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "lesson_id", str(self.lesson_id))
        object.__setattr__(self, "teacher_id", str(self.teacher_id))
        object.__setattr__(self, "student_id", str(self.student_id))
        object.__setattr__(
            self, "skill_type", _normalize_identifier(self.skill_type, SKILL_TYPES, "Farming")
        )
        object.__setattr__(self, "tick", max(0, int(self.tick)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "lesson_id": self.lesson_id,
            "teacher_id": self.teacher_id,
            "student_id": self.student_id,
            "skill_type": self.skill_type,
            "tick": self.tick,
            "event_type": self.event_type,
        }


@dataclass(frozen=True, slots=True)
class LessonCompleted:
    lesson_id: str
    teacher_id: str
    student_id: str
    skill_type: str
    success: bool
    experience_transferred: float
    tick: int
    event_type: str = field(default="LessonCompleted", init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "lesson_id", str(self.lesson_id))
        object.__setattr__(self, "teacher_id", str(self.teacher_id))
        object.__setattr__(self, "student_id", str(self.student_id))
        object.__setattr__(
            self, "skill_type", _normalize_identifier(self.skill_type, SKILL_TYPES, "Farming")
        )
        object.__setattr__(self, "success", bool(self.success))
        object.__setattr__(
            self, "experience_transferred", max(0.0, float(self.experience_transferred))
        )
        object.__setattr__(self, "tick", max(0, int(self.tick)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "lesson_id": self.lesson_id,
            "teacher_id": self.teacher_id,
            "student_id": self.student_id,
            "skill_type": self.skill_type,
            "success": self.success,
            "experience_transferred": self.experience_transferred,
            "tick": self.tick,
            "event_type": self.event_type,
        }


@dataclass(frozen=True, slots=True)
class TeacherAssigned:
    teacher_id: str
    student_id: str
    skill_type: str
    start_tick: int
    tick: int
    event_type: str = field(default="TeacherAssigned", init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "teacher_id", str(self.teacher_id))
        object.__setattr__(self, "student_id", str(self.student_id))
        object.__setattr__(
            self, "skill_type", _normalize_identifier(self.skill_type, SKILL_TYPES, "Farming")
        )
        st = max(0, int(self.start_tick))
        object.__setattr__(self, "start_tick", st)
        object.__setattr__(self, "tick", max(st, int(self.tick)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "teacher_id": self.teacher_id,
            "student_id": self.student_id,
            "skill_type": self.skill_type,
            "start_tick": self.start_tick,
            "tick": self.tick,
            "event_type": self.event_type,
        }


@dataclass(frozen=True, slots=True)
class ApprenticeshipStarted:
    apprenticeship_id: str
    apprentice_id: str
    master_id: str
    skill_type: str
    experience_target: float
    tick: int
    event_type: str = field(default="ApprenticeshipStarted", init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "apprenticeship_id", str(self.apprenticeship_id))
        object.__setattr__(self, "apprentice_id", str(self.apprentice_id))
        object.__setattr__(self, "master_id", str(self.master_id))
        object.__setattr__(
            self, "skill_type", _normalize_identifier(self.skill_type, SKILL_TYPES, "Farming")
        )
        object.__setattr__(self, "experience_target", max(0.0, float(self.experience_target)))
        object.__setattr__(self, "tick", max(0, int(self.tick)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "apprenticeship_id": self.apprenticeship_id,
            "apprentice_id": self.apprentice_id,
            "master_id": self.master_id,
            "skill_type": self.skill_type,
            "experience_target": self.experience_target,
            "tick": self.tick,
            "event_type": self.event_type,
        }


@dataclass(frozen=True, slots=True)
class ApprenticeshipCompleted:
    apprenticeship_id: str
    apprentice_id: str
    master_id: str
    skill_type: str
    total_experience: float
    final_level: int
    tick: int
    event_type: str = field(default="ApprenticeshipCompleted", init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "apprenticeship_id", str(self.apprenticeship_id))
        object.__setattr__(self, "apprentice_id", str(self.apprentice_id))
        object.__setattr__(self, "master_id", str(self.master_id))
        object.__setattr__(
            self, "skill_type", _normalize_identifier(self.skill_type, SKILL_TYPES, "Farming")
        )
        object.__setattr__(self, "total_experience", max(0.0, float(self.total_experience)))
        object.__setattr__(self, "final_level", max(0, int(self.final_level)))
        object.__setattr__(self, "tick", max(0, int(self.tick)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "apprenticeship_id": self.apprenticeship_id,
            "apprentice_id": self.apprentice_id,
            "master_id": self.master_id,
            "skill_type": self.skill_type,
            "total_experience": self.total_experience,
            "final_level": self.final_level,
            "tick": self.tick,
            "event_type": self.event_type,
        }


@dataclass(frozen=True, slots=True)
class ObservationLearning:
    observer_id: str
    practitioner_id: str
    skill_type: str
    context: str
    experience_gained: float
    tick: int
    event_type: str = field(default="ObservationLearning", init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "observer_id", str(self.observer_id))
        object.__setattr__(self, "practitioner_id", str(self.practitioner_id))
        object.__setattr__(
            self, "skill_type", _normalize_identifier(self.skill_type, SKILL_TYPES, "Farming")
        )
        object.__setattr__(self, "context", str(self.context))
        object.__setattr__(self, "experience_gained", max(0.0, float(self.experience_gained)))
        object.__setattr__(self, "tick", max(0, int(self.tick)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "observer_id": self.observer_id,
            "practitioner_id": self.practitioner_id,
            "skill_type": self.skill_type,
            "context": self.context,
            "experience_gained": self.experience_gained,
            "tick": self.tick,
            "event_type": self.event_type,
        }


@dataclass(frozen=True, slots=True)
class SkillMastered:
    entity_id: str
    skill_type: str
    master_level: int
    total_experience: float
    tick: int
    event_type: str = field(default="SkillMastered", init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "entity_id", str(self.entity_id))
        object.__setattr__(
            self, "skill_type", _normalize_identifier(self.skill_type, SKILL_TYPES, "Farming")
        )
        object.__setattr__(self, "master_level", max(0, int(self.master_level)))
        object.__setattr__(self, "total_experience", max(0.0, float(self.total_experience)))
        object.__setattr__(self, "tick", max(0, int(self.tick)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "skill_type": self.skill_type,
            "master_level": self.master_level,
            "total_experience": self.total_experience,
            "tick": self.tick,
            "event_type": self.event_type,
        }


@dataclass(frozen=True, slots=True)
class KnowledgeTransferred:
    from_entity_id: str
    to_entity_id: str
    skill_type: str
    experience_amount: float
    context: str
    tick: int
    event_type: str = field(default="KnowledgeTransferred", init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "from_entity_id", str(self.from_entity_id))
        object.__setattr__(self, "to_entity_id", str(self.to_entity_id))
        object.__setattr__(
            self, "skill_type", _normalize_identifier(self.skill_type, SKILL_TYPES, "Farming")
        )
        object.__setattr__(self, "experience_amount", max(0.0, float(self.experience_amount)))
        object.__setattr__(self, "context", str(self.context))
        object.__setattr__(self, "tick", max(0, int(self.tick)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "from_entity_id": self.from_entity_id,
            "to_entity_id": self.to_entity_id,
            "skill_type": self.skill_type,
            "experience_amount": self.experience_amount,
            "context": self.context,
            "tick": self.tick,
            "event_type": self.event_type,
        }
