from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    val = hash(s) % (2**32)
    return abs(val)


SKILL_TYPES: tuple[str, ...] = (
    "Farming",
    "Cooking",
    "Blacksmithing",
    "Carpentry",
    "Hunting",
    "Trading",
    "Leadership",
    "Medicine",
    "Crafting",
    "Social",
)


SKILL_TO_OCCUPATION: tuple[tuple[str, str], ...] = (
    ("Farming", "Farmer"),
    ("Cooking", "Cook"),
    ("Blacksmithing", "Blacksmith"),
    ("Carpentry", "Carpenter"),
    ("Hunting", "Farmer"),
    ("Trading", "Carpenter"),
    ("Leadership", "Farmer"),
    ("Medicine", "Cook"),
    ("Crafting", "Blacksmith"),
    ("Social", "Cook"),
)


APPRENTICESHIP_STATUSES: tuple[str, ...] = (
    "Pending",
    "Active",
    "Completed",
    "Terminated",
)


LESSON_STATUSES: tuple[str, ...] = (
    "Scheduled",
    "Started",
    "Explained",
    "Practiced",
    "Completed",
    "Failed",
)


LEVEL_NAMES: tuple[str, ...] = (
    "Novice",
    "Apprentice",
    "Journeyman",
    "Expert",
    "Master",
    "Grandmaster",
)


MAX_LEVEL: int = 10


def _exp_for_level(level: int) -> float:
    lv = max(0, int(level))
    return float(lv * lv * 50 + lv * 25)


LEVEL_EXP_TABLE: tuple[float, ...] = tuple(_exp_for_level(i) for i in range(MAX_LEVEL + 2))


def _normalize_identifier(value: Any, allowed: Sequence[str], fallback: str) -> str:
    raw = str(value).strip() if value is not None else ""
    if raw in allowed:
        return raw
    lowered = {str(a).lower(): a for a in allowed}
    if raw.lower() in lowered:
        return lowered[raw.lower()]
    return str(fallback)


def _to_tuple_of_str(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, (tuple, list)):
        return tuple(str(x) for x in value)
    return (str(value),)


def _to_tuple_of_tuples(value: Any) -> tuple[tuple[Any, ...], ...]:
    if value is None:
        return ()
    if isinstance(value, (tuple, list)):
        out = []
        for item in value:
            if isinstance(item, Mapping):
                out.append(tuple(item.get(k) for k in sorted(item.keys())))
            elif isinstance(item, (tuple, list)):
                out.append(tuple(item))
            else:
                out.append((item,))
        return tuple(out)
    return ()


def make_skill_id(entity_id: str, skill_type: str) -> str:
    seed = f"skill:{entity_id}:{skill_type}"
    short = deterministic_hash(seed)
    return f"skill:{skill_type}:{entity_id}:{short}"


def make_learning_state_id(entity_id: str) -> str:
    seed = f"learning:{entity_id}"
    short = deterministic_hash(seed)
    return f"ls:{entity_id}:{short}"


def make_apprenticeship_id(apprentice_id: str, master_id: str, skill_type: str) -> str:
    seed = f"apprentice:{apprentice_id}:{master_id}:{skill_type}"
    short = deterministic_hash(seed)
    return f"app:{skill_type}:{apprentice_id}:{short}"


def make_lesson_id(teacher_id: str, student_id: str, skill_type: str, tick: int) -> str:
    seed = f"lesson:{teacher_id}:{student_id}:{skill_type}:{tick}"
    short = deterministic_hash(seed)
    return f"lesson:{skill_type}:{teacher_id}:{tick}:{short}"


def level_from_experience(exp: float, max_level: int = MAX_LEVEL) -> int:
    e = max(0.0, float(exp))
    for lv in range(max_level, -1, -1):
        if e >= LEVEL_EXP_TABLE[lv]:
            return min(lv, max_level)
    return 0


def next_level_exp(current_level: int, max_level: int = MAX_LEVEL) -> float:
    lv = max(0, min(int(current_level), max_level))
    if lv >= max_level:
        return LEVEL_EXP_TABLE[max_level]
    return LEVEL_EXP_TABLE[lv + 1]


def level_name(level: int, max_level: int = MAX_LEVEL) -> str:
    lv = max(0, min(int(level), max_level))
    if lv <= 0:
        return LEVEL_NAMES[0]
    if lv <= 2:
        return LEVEL_NAMES[1]
    if lv <= 4:
        return LEVEL_NAMES[2]
    if lv <= 6:
        return LEVEL_NAMES[3]
    if lv <= 8:
        return LEVEL_NAMES[4]
    return LEVEL_NAMES[5]


@dataclass(slots=True)
class PracticeRecord:
    tick: int
    skill_type: str
    context: str = ""
    experience_gained: float = 0.0

    def __post_init__(self) -> None:
        self.tick = max(0, int(self.tick))
        self.skill_type = _normalize_identifier(self.skill_type, SKILL_TYPES, "Farming")
        self.context = str(self.context)
        self.experience_gained = max(0.0, float(self.experience_gained))

    def to_dict(self) -> dict[str, Any]:
        return {
            "tick": self.tick,
            "skill_type": self.skill_type,
            "context": self.context,
            "experience_gained": self.experience_gained,
        }

    @staticmethod
    def from_dict(data: Mapping[str, Any]) -> "PracticeRecord":
        return PracticeRecord(
            tick=int(data.get("tick", 0)),
            skill_type=str(data.get("skill_type", "Farming")),
            context=str(data.get("context", "")),
            experience_gained=float(data.get("experience_gained", 0.0)),
        )


def _to_practice_history(value: Any) -> tuple[PracticeRecord, ...]:
    if value is None:
        return ()
    items = list(value) if isinstance(value, (list, tuple)) else [value]
    out = []
    for item in items:
        if isinstance(item, PracticeRecord):
            out.append(item)
        elif isinstance(item, Mapping):
            out.append(PracticeRecord.from_dict(item))
        else:
            continue
    return tuple(out)


@dataclass(slots=True)
class TeacherRecord:
    teacher_id: str
    skill_type: str
    first_tick: int
    last_tick: int
    total_lessons: int = 0

    def __post_init__(self) -> None:
        self.teacher_id = str(self.teacher_id)
        self.skill_type = _normalize_identifier(self.skill_type, SKILL_TYPES, "Farming")
        self.first_tick = max(0, int(self.first_tick))
        self.last_tick = max(self.first_tick, int(self.last_tick))
        self.total_lessons = max(0, int(self.total_lessons))

    def to_dict(self) -> dict[str, Any]:
        return {
            "teacher_id": self.teacher_id,
            "skill_type": self.skill_type,
            "first_tick": self.first_tick,
            "last_tick": self.last_tick,
            "total_lessons": self.total_lessons,
        }

    @staticmethod
    def from_dict(data: Mapping[str, Any]) -> "TeacherRecord":
        return TeacherRecord(
            teacher_id=str(data.get("teacher_id", "")),
            skill_type=str(data.get("skill_type", "Farming")),
            first_tick=int(data.get("first_tick", 0)),
            last_tick=int(data.get("last_tick", 0)),
            total_lessons=int(data.get("total_lessons", 0)),
        )


def _to_teacher_history(value: Any) -> tuple[TeacherRecord, ...]:
    if value is None:
        return ()
    items = list(value) if isinstance(value, (list, tuple)) else [value]
    out = []
    for item in items:
        if isinstance(item, TeacherRecord):
            out.append(item)
        elif isinstance(item, Mapping):
            out.append(TeacherRecord.from_dict(item))
        else:
            continue
    return tuple(out)


@dataclass(slots=True)
class Skill:
    skill_id: str
    skill_type: str
    entity_id: str
    experience: float = 0.0
    level: int = 0
    max_level: int = MAX_LEVEL
    last_practiced_tick: int = 0
    teacher_history: tuple[TeacherRecord, ...] = ()
    practice_history: tuple[PracticeRecord, ...] = ()

    def __post_init__(self) -> None:
        self.skill_id = str(self.skill_id)
        self.skill_type = _normalize_identifier(self.skill_type, SKILL_TYPES, "Farming")
        self.entity_id = str(self.entity_id)
        self.experience = max(0.0, float(self.experience))
        self.max_level = max(1, min(int(self.max_level), MAX_LEVEL))
        self.level = max(0, min(int(self.level), self.max_level))
        expected_level = level_from_experience(self.experience, self.max_level)
        if expected_level > self.level:
            self.level = expected_level
        self.last_practiced_tick = max(0, int(self.last_practiced_tick))
        self.teacher_history = _to_teacher_history(self.teacher_history)
        self.practice_history = _to_practice_history(self.practice_history)

    @property
    def level_name(self) -> str:
        return level_name(self.level, self.max_level)

    @property
    def next_level_exp(self) -> float:
        return next_level_exp(self.level, self.max_level)

    @property
    def experience_to_next(self) -> float:
        return max(0.0, self.next_level_exp - self.experience)

    @property
    def progress_pct(self) -> float:
        cur = LEVEL_EXP_TABLE[self.level] if self.level < len(LEVEL_EXP_TABLE) else 0.0
        nxt = self.next_level_exp
        if nxt <= cur:
            return 0.0
        have = max(0.0, self.experience - cur)
        return min(1.0, have / (nxt - cur))

    @property
    def is_mastered(self) -> bool:
        return self.level >= self.max_level

    def to_dict(self) -> dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "skill_type": self.skill_type,
            "entity_id": self.entity_id,
            "experience": self.experience,
            "level": self.level,
            "max_level": self.max_level,
            "last_practiced_tick": self.last_practiced_tick,
            "teacher_history": [t.to_dict() for t in self.teacher_history],
            "practice_history": [p.to_dict() for p in self.practice_history],
        }

    @staticmethod
    def from_dict(data: Mapping[str, Any]) -> "Skill":
        return Skill(
            skill_id=str(data.get("skill_id", "skill_1")),
            skill_type=str(data.get("skill_type", "Farming")),
            entity_id=str(data.get("entity_id", "")),
            experience=float(data.get("experience", 0.0)),
            level=int(data.get("level", 0)),
            max_level=int(data.get("max_level", MAX_LEVEL)),
            last_practiced_tick=int(data.get("last_practiced_tick", 0)),
            teacher_history=tuple(data.get("teacher_history", ())),
            practice_history=tuple(data.get("practice_history", ())),
        )


@dataclass(slots=True)
class Apprenticeship:
    apprenticeship_id: str
    apprentice_id: str
    master_id: str
    skill_type: str
    status: str = "Pending"
    start_tick: int = 0
    end_tick: int = 0
    experience_target: float = 0.0
    experience_earned: float = 0.0
    lessons_completed: int = 0
    practices_completed: int = 0

    def __post_init__(self) -> None:
        self.apprenticeship_id = str(self.apprenticeship_id)
        self.apprentice_id = str(self.apprentice_id)
        self.master_id = str(self.master_id)
        self.skill_type = _normalize_identifier(self.skill_type, SKILL_TYPES, "Farming")
        self.status = _normalize_identifier(self.status, APPRENTICESHIP_STATUSES, "Pending")
        self.start_tick = max(0, int(self.start_tick))
        self.end_tick = max(self.start_tick, int(self.end_tick))
        self.experience_target = max(0.0, float(self.experience_target))
        self.experience_earned = max(0.0, min(float(self.experience_earned), self.experience_target if self.experience_target > 0 else float(self.experience_earned)))
        self.lessons_completed = max(0, int(self.lessons_completed))
        self.practices_completed = max(0, int(self.practices_completed))

    @property
    def is_active(self) -> bool:
        return self.status == "Active"

    @property
    def is_completed(self) -> bool:
        return self.status == "Completed"

    @property
    def progress_pct(self) -> float:
        if self.experience_target <= 0:
            return 0.0
        return min(1.0, self.experience_earned / self.experience_target)

    def to_dict(self) -> dict[str, Any]:
        return {
            "apprenticeship_id": self.apprenticeship_id,
            "apprentice_id": self.apprentice_id,
            "master_id": self.master_id,
            "skill_type": self.skill_type,
            "status": self.status,
            "start_tick": self.start_tick,
            "end_tick": self.end_tick,
            "experience_target": self.experience_target,
            "experience_earned": self.experience_earned,
            "lessons_completed": self.lessons_completed,
            "practices_completed": self.practices_completed,
        }

    @staticmethod
    def from_dict(data: Mapping[str, Any]) -> "Apprenticeship":
        return Apprenticeship(
            apprenticeship_id=str(data.get("apprenticeship_id", "app_1")),
            apprentice_id=str(data.get("apprentice_id", "")),
            master_id=str(data.get("master_id", "")),
            skill_type=str(data.get("skill_type", "Farming")),
            status=str(data.get("status", "Pending")),
            start_tick=int(data.get("start_tick", 0)),
            end_tick=int(data.get("end_tick", 0)),
            experience_target=float(data.get("experience_target", 0.0)),
            experience_earned=float(data.get("experience_earned", 0.0)),
            lessons_completed=int(data.get("lessons_completed", 0)),
            practices_completed=int(data.get("practices_completed", 0)),
        )


@dataclass(slots=True)
class Lesson:
    lesson_id: str
    teacher_id: str
    student_id: str
    skill_type: str
    status: str = "Scheduled"
    scheduled_tick: int = 0
    started_tick: int = 0
    completed_tick: int = 0
    experience_transferred: float = 0.0
    teacher_experience_before: float = 0.0
    student_experience_before: float = 0.0

    def __post_init__(self) -> None:
        self.lesson_id = str(self.lesson_id)
        self.teacher_id = str(self.teacher_id)
        self.student_id = str(self.student_id)
        self.skill_type = _normalize_identifier(self.skill_type, SKILL_TYPES, "Farming")
        self.status = _normalize_identifier(self.status, LESSON_STATUSES, "Scheduled")
        self.scheduled_tick = max(0, int(self.scheduled_tick))
        self.started_tick = max(self.scheduled_tick, int(self.started_tick))
        self.completed_tick = max(self.started_tick, int(self.completed_tick))
        self.experience_transferred = max(0.0, float(self.experience_transferred))
        self.teacher_experience_before = max(0.0, float(self.teacher_experience_before))
        self.student_experience_before = max(0.0, float(self.student_experience_before))

    @property
    def is_started(self) -> bool:
        return self.status in ("Started", "Explained", "Practiced")

    @property
    def is_complete(self) -> bool:
        return self.status in ("Completed", "Failed")

    def to_dict(self) -> dict[str, Any]:
        return {
            "lesson_id": self.lesson_id,
            "teacher_id": self.teacher_id,
            "student_id": self.student_id,
            "skill_type": self.skill_type,
            "status": self.status,
            "scheduled_tick": self.scheduled_tick,
            "started_tick": self.started_tick,
            "completed_tick": self.completed_tick,
            "experience_transferred": self.experience_transferred,
            "teacher_experience_before": self.teacher_experience_before,
            "student_experience_before": self.student_experience_before,
        }

    @staticmethod
    def from_dict(data: Mapping[str, Any]) -> "Lesson":
        return Lesson(
            lesson_id=str(data.get("lesson_id", "lesson_1")),
            teacher_id=str(data.get("teacher_id", "")),
            student_id=str(data.get("student_id", "")),
            skill_type=str(data.get("skill_type", "Farming")),
            status=str(data.get("status", "Scheduled")),
            scheduled_tick=int(data.get("scheduled_tick", 0)),
            started_tick=int(data.get("started_tick", 0)),
            completed_tick=int(data.get("completed_tick", 0)),
            experience_transferred=float(data.get("experience_transferred", 0.0)),
            teacher_experience_before=float(data.get("teacher_experience_before", 0.0)),
            student_experience_before=float(data.get("student_experience_before", 0.0)),
        )


@dataclass(slots=True)
class LearningState:
    entity_id: str
    skills: dict[str, Skill] = field(default_factory=dict)
    students_taught: tuple[str, ...] = ()
    teachers_learned_from: tuple[str, ...] = ()
    apprenticeships_as_apprentice: tuple[str, ...] = ()
    apprenticeships_as_master: tuple[str, ...] = ()
    lessons_as_teacher: tuple[str, ...] = ()
    lessons_as_student: tuple[str, ...] = ()
    lessons_explained: tuple[str, ...] = ()
    lessons_practiced: tuple[str, ...] = ()
    knowledge_shared_count: int = 0
    total_skills_mastered: int = 0

    def __post_init__(self) -> None:
        self.entity_id = str(self.entity_id)
        if isinstance(self.skills, Mapping):
            raw_skills: dict[str, Any] = {str(k): v for k, v in self.skills.items()}
        elif isinstance(self.skills, dict):
            raw_skills = self.skills
        else:
            raw_skills = {}
        norm_skills: dict[str, Skill] = {}
        for k, v in raw_skills.items():
            if isinstance(v, Skill):
                norm_skills[str(k)] = v
            elif isinstance(v, Mapping):
                norm_skills[str(k)] = Skill.from_dict(v)
        self.skills = norm_skills
        self.students_taught = _to_tuple_of_str(self.students_taught)
        self.teachers_learned_from = _to_tuple_of_str(self.teachers_learned_from)
        self.apprenticeships_as_apprentice = _to_tuple_of_str(self.apprenticeships_as_apprentice)
        self.apprenticeships_as_master = _to_tuple_of_str(self.apprenticeships_as_master)
        self.lessons_as_teacher = _to_tuple_of_str(self.lessons_as_teacher)
        self.lessons_as_student = _to_tuple_of_str(self.lessons_as_student)
        self.lessons_explained = _to_tuple_of_str(self.lessons_explained)
        self.lessons_practiced = _to_tuple_of_str(self.lessons_practiced)
        self.knowledge_shared_count = max(0, int(self.knowledge_shared_count))
        mastered = sum(1 for s in self.skills.values() if s.is_mastered)
        if self.total_skills_mastered < mastered:
            self.total_skills_mastered = mastered

    @property
    def skill_count(self) -> int:
        return len(self.skills)

    @property
    def total_levels(self) -> int:
        return sum(s.level for s in self.skills.values())

    def get_skill(self, skill_type: str) -> Skill | None:
        st = _normalize_identifier(skill_type, SKILL_TYPES, "Farming")
        if st in self.skills:
            return self.skills[st]
        for s in self.skills.values():
            if s.skill_type == skill_type:
                return s
        return None

    def get_level(self, skill_type: str) -> int:
        s = self.get_skill(skill_type)
        return s.level if s else 0

    def get_experience(self, skill_type: str) -> float:
        s = self.get_skill(skill_type)
        return s.experience if s else 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "skills": {k: v.to_dict() for k, v in self.skills.items()},
            "students_taught": list(self.students_taught),
            "teachers_learned_from": list(self.teachers_learned_from),
            "apprenticeships_as_apprentice": list(self.apprenticeships_as_apprentice),
            "apprenticeships_as_master": list(self.apprenticeships_as_master),
            "lessons_as_teacher": list(self.lessons_as_teacher),
            "lessons_as_student": list(self.lessons_as_student),
            "lessons_explained": list(self.lessons_explained),
            "lessons_practiced": list(self.lessons_practiced),
            "knowledge_shared_count": self.knowledge_shared_count,
            "total_skills_mastered": self.total_skills_mastered,
        }

    @staticmethod
    def from_dict(data: Mapping[str, Any]) -> "LearningState":
        return LearningState(
            entity_id=str(data.get("entity_id", "")),
            skills=dict(data.get("skills", {})),
            students_taught=tuple(data.get("students_taught", ())),
            teachers_learned_from=tuple(data.get("teachers_learned_from", ())),
            apprenticeships_as_apprentice=tuple(data.get("apprenticeships_as_apprentice", ())),
            apprenticeships_as_master=tuple(data.get("apprenticeships_as_master", ())),
            lessons_as_teacher=tuple(data.get("lessons_as_teacher", ())),
            lessons_as_student=tuple(data.get("lessons_as_student", ())),
            lessons_explained=tuple(data.get("lessons_explained", ())),
            lessons_practiced=tuple(data.get("lessons_practiced", ())),
            knowledge_shared_count=int(data.get("knowledge_shared_count", 0)),
            total_skills_mastered=int(data.get("total_skills_mastered", 0)),
        )


def build_default_skills_for(entity_id: str) -> dict[str, Skill]:
    out: dict[str, Skill] = {}
    for st in SKILL_TYPES:
        sid = make_skill_id(entity_id, st)
        out[st] = Skill(
            skill_id=sid,
            skill_type=st,
            entity_id=entity_id,
            experience=0.0,
            level=0,
            max_level=MAX_LEVEL,
            last_practiced_tick=0,
            teacher_history=(),
            practice_history=(),
        )
    return out


def build_default_learning_state(entity_id: str) -> LearningState:
    return LearningState(
        entity_id=entity_id,
        skills=build_default_skills_for(entity_id),
    )
