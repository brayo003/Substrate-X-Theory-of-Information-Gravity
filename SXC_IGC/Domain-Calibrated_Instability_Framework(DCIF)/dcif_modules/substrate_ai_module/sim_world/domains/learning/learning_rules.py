from __future__ import annotations

from dataclasses import dataclass, replace as _dc_replace
from typing import Any, Mapping, Sequence

from .learning_events import (
    ApprenticeshipCompleted,
    ApprenticeshipStarted,
    ExperienceGained,
    KnowledgeTransferred,
    LessonCompleted,
    LessonStarted,
    LevelIncreased,
    ObservationLearning,
    SkillMastered,
    SkillPracticeCompleted,
    SkillPracticeStarted,
    TeacherAssigned,
)
from .learning_models import (
    APPRENTICESHIP_STATUSES,
    LESSON_STATUSES,
    LEVEL_EXP_TABLE,
    LEVEL_NAMES,
    MAX_LEVEL,
    SKILL_TO_OCCUPATION,
    SKILL_TYPES,
    Apprenticeship,
    LearningState,
    Lesson,
    PracticeRecord,
    Skill,
    TeacherRecord,
    _normalize_identifier,
    _to_tuple_of_str,
    build_default_learning_state,
    build_default_skills_for,
    level_from_experience,
    make_apprenticeship_id,
    make_lesson_id,
    make_skill_id,
    next_level_exp,
)


SKILL_PRACTICE_BASE_EXP: dict[str, float] = {
    "Farming": 15.0,
    "Cooking": 12.0,
    "Blacksmithing": 20.0,
    "Carpentry": 14.0,
    "Hunting": 18.0,
    "Trading": 10.0,
    "Leadership": 8.0,
    "Medicine": 16.0,
    "Crafting": 13.0,
    "Social": 7.0,
}


def get_base_practice_exp(skill_type: str) -> float:
    st = _normalize_identifier(skill_type, SKILL_TYPES, "Farming")
    return float(SKILL_PRACTICE_BASE_EXP.get(st, 10.0))


def ensure_skill(state: LearningState, skill_type: str) -> tuple[LearningState, Skill]:
    st = _normalize_identifier(skill_type, SKILL_TYPES, "Farming")
    skill = state.get_skill(st)
    if skill is not None:
        return state, skill
    sid = make_skill_id(state.entity_id, st)
    new_skill = Skill(
        skill_id=sid,
        skill_type=st,
        entity_id=state.entity_id,
        experience=0.0,
        level=0,
    )
    new_skills = dict(state.skills)
    new_skills[st] = new_skill
    new_state = LearningState(
        entity_id=state.entity_id,
        skills=new_skills,
        students_taught=state.students_taught,
        teachers_learned_from=state.teachers_learned_from,
        apprenticeships_as_apprentice=state.apprenticeships_as_apprentice,
        apprenticeships_as_master=state.apprenticeships_as_master,
        lessons_as_teacher=state.lessons_as_teacher,
        lessons_as_student=state.lessons_as_student,
        lessons_explained=state.lessons_explained,
        lessons_practiced=state.lessons_practiced,
        knowledge_shared_count=state.knowledge_shared_count,
        total_skills_mastered=state.total_skills_mastered,
    )
    return new_state, new_skill


def add_experience_to_skill(
    skill: Skill,
    delta: float,
    source: str,
    tick: int,
    context: str = "",
    teacher_id: str = "",
) -> tuple[Skill, list[Any]]:
    delta = max(0.0, float(delta))
    if delta <= 0.0:
        return skill, []
    exp_before = skill.experience
    level_before = skill.level
    new_exp = exp_before + delta
    new_level_raw = level_from_experience(new_exp, skill.max_level)
    mastered_before = skill.is_mastered

    new_history = list(skill.practice_history)
    if context:
        new_history.append(PracticeRecord(
            tick=tick,
            skill_type=skill.skill_type,
            context=context,
            experience_gained=delta,
        ))

    new_teachers = list(skill.teacher_history)
    if teacher_id:
        existing = None
        for idx, tr in enumerate(new_teachers):
            if tr.teacher_id == teacher_id and tr.skill_type == skill.skill_type:
                existing = idx
                break
        if existing is None:
            new_teachers.append(TeacherRecord(
                teacher_id=teacher_id,
                skill_type=skill.skill_type,
                first_tick=tick,
                last_tick=tick,
                total_lessons=1,
            ))
        else:
            old = new_teachers[existing]
            new_teachers[existing] = TeacherRecord(
                teacher_id=old.teacher_id,
                skill_type=old.skill_type,
                first_tick=old.first_tick,
                last_tick=max(old.last_tick, tick),
                total_lessons=old.total_lessons + 1,
            )

    updated = Skill(
        skill_id=skill.skill_id,
        skill_type=skill.skill_type,
        entity_id=skill.entity_id,
        experience=new_exp,
        level=max(skill.level, new_level_raw),
        max_level=skill.max_level,
        last_practiced_tick=max(skill.last_practiced_tick, tick),
        teacher_history=tuple(new_teachers),
        practice_history=tuple(new_history),
    )

    events: list[Any] = []
    events.append(ExperienceGained(
        entity_id=skill.entity_id,
        skill_type=skill.skill_type,
        experience_before=exp_before,
        experience_after=new_exp,
        experience_delta=delta,
        source=source,
        tick=tick,
    ))
    if new_level_raw > level_before:
        events.append(LevelIncreased(
            entity_id=skill.entity_id,
            skill_type=skill.skill_type,
            level_before=level_before,
            level_after=new_level_raw,
            experience_at_level=new_exp,
            tick=tick,
        ))
    if (not mastered_before) and updated.is_mastered:
        events.append(SkillMastered(
            entity_id=skill.entity_id,
            skill_type=skill.skill_type,
            master_level=updated.level,
            total_experience=new_exp,
            tick=tick,
        ))
    return updated, events


def _replace_skill_in_state(state: LearningState, new_skill: Skill) -> LearningState:
    new_skills = dict(state.skills)
    new_skills[new_skill.skill_type] = new_skill
    mastered = sum(1 for s in new_skills.values() if s.is_mastered)
    return LearningState(
        entity_id=state.entity_id,
        skills=new_skills,
        students_taught=state.students_taught,
        teachers_learned_from=state.teachers_learned_from,
        apprenticeships_as_apprentice=state.apprenticeships_as_apprentice,
        apprenticeships_as_master=state.apprenticeships_as_master,
        lessons_as_teacher=state.lessons_as_teacher,
        lessons_as_student=state.lessons_as_student,
        lessons_explained=state.lessons_explained,
        lessons_practiced=state.lessons_practiced,
        knowledge_shared_count=state.knowledge_shared_count,
        total_skills_mastered=max(state.total_skills_mastered, mastered),
    )


def ensure_learning_state_for(states_map: Mapping[str, LearningState], entity_id: str) -> LearningState:
    key = str(entity_id)
    if key in states_map:
        ls = states_map[key]
        if isinstance(ls, LearningState):
            return ls
    return build_default_learning_state(key)


def record_practice(
    state: LearningState,
    skill_type: str,
    tick: int,
    context: str = "",
    success: bool = True,
    practice_count: int = 1,
    skill_bonus_mult: float = 1.0,
    teacher_id: str = "",
) -> tuple[LearningState, list[Any]]:
    state, skill = ensure_skill(state, skill_type)
    events: list[Any] = []
    events.append(SkillPracticeStarted(
        entity_id=state.entity_id,
        skill_type=skill.skill_type,
        context=context,
        tick=tick,
    ))
    if not success:
        events.append(SkillPracticeCompleted(
            entity_id=state.entity_id,
            skill_type=skill.skill_type,
            context=context,
            success=False,
            tick=tick,
        ))
        return state, events
    base = get_base_practice_exp(skill.skill_type)
    pc = max(1, int(practice_count))
    mult = max(0.0, float(skill_bonus_mult))
    total = base * float(pc) * mult
    if skill.level > 5:
        total *= 1.0 + 0.05 * (skill.level - 5)
    new_skill, exp_events = add_experience_to_skill(
        skill, total, source="practice", tick=tick, context=context, teacher_id=teacher_id
    )
    events.extend(exp_events)
    events.append(SkillPracticeCompleted(
        entity_id=state.entity_id,
        skill_type=skill.skill_type,
        context=context,
        success=True,
        tick=tick,
    ))
    new_state = _replace_skill_in_state(state, new_skill)
    return new_state, events


def record_observation(
    observer_state: LearningState,
    practitioner_state: LearningState,
    skill_type: str,
    tick: int,
    context: str = "",
    proximity: int = 1,
) -> tuple[LearningState, list[Any]]:
    observer_state, observer_skill = ensure_skill(observer_state, skill_type)
    pract_skill = practitioner_state.get_skill(skill_type)
    events: list[Any] = []
    if pract_skill is None:
        return observer_state, events
    pract_exp = get_base_practice_exp(skill_type)
    pract_level = pract_skill.level
    obs_mult = 0.10 + min(0.15 * pract_level, 0.50)
    prox = max(0.5, 1.0 / max(1, int(proximity)))
    gained = pract_exp * obs_mult * prox
    if gained <= 0:
        return observer_state, events
    new_skill, exp_events = add_experience_to_skill(
        observer_skill, gained, source="observation", tick=tick, context=f"observed:{practitioner_state.entity_id}"
    )
    events.append(ObservationLearning(
        observer_id=observer_state.entity_id,
        practitioner_id=practitioner_state.entity_id,
        skill_type=observer_skill.skill_type,
        context=context,
        experience_gained=gained,
        tick=tick,
    ))
    events.extend(exp_events)
    new_state = _replace_skill_in_state(observer_state, new_skill)
    return new_state, events


def start_lesson(
    teacher_state: LearningState,
    student_state: LearningState,
    skill_type: str,
    tick: int,
) -> tuple[Lesson, LearningState, LearningState, list[Any]]:
    st = _normalize_identifier(skill_type, SKILL_TYPES, "Farming")
    teacher_state, t_skill = ensure_skill(teacher_state, st)
    lid = make_lesson_id(teacher_state.entity_id, student_state.entity_id, st, tick)
    lesson = Lesson(
        lesson_id=lid,
        teacher_id=teacher_state.entity_id,
        student_id=student_state.entity_id,
        skill_type=st,
        status="Started",
        scheduled_tick=tick,
        started_tick=tick,
        completed_tick=0,
        experience_transferred=0.0,
        teacher_experience_before=t_skill.experience,
        student_experience_before=0.0,
    )
    events: list[Any] = []
    events.append(LessonStarted(
        lesson_id=lid,
        teacher_id=teacher_state.entity_id,
        student_id=student_state.entity_id,
        skill_type=st,
        tick=tick,
    ))
    if teacher_state.entity_id not in student_state.teachers_learned_from:
        new_teachers_student = tuple(list(student_state.teachers_learned_from) + [teacher_state.entity_id])
    else:
        new_teachers_student = student_state.teachers_learned_from
    if student_state.entity_id not in teacher_state.students_taught:
        new_students_taught = tuple(list(teacher_state.students_taught) + [student_state.entity_id])
    else:
        new_students_taught = teacher_state.students_taught
    teacher_out = LearningState(
        entity_id=teacher_state.entity_id,
        skills=dict(teacher_state.skills),
        students_taught=new_students_taught,
        teachers_learned_from=teacher_state.teachers_learned_from,
        apprenticeships_as_apprentice=teacher_state.apprenticeships_as_apprentice,
        apprenticeships_as_master=teacher_state.apprenticeships_as_master,
        lessons_as_teacher=tuple(list(teacher_state.lessons_as_teacher) + [lid]),
        lessons_as_student=teacher_state.lessons_as_student,
        lessons_explained=teacher_state.lessons_explained,
        lessons_practiced=teacher_state.lessons_practiced,
        knowledge_shared_count=teacher_state.knowledge_shared_count,
        total_skills_mastered=teacher_state.total_skills_mastered,
    )
    student_out = LearningState(
        entity_id=student_state.entity_id,
        skills=dict(student_state.skills),
        students_taught=student_state.students_taught,
        teachers_learned_from=new_teachers_student,
        apprenticeships_as_apprentice=student_state.apprenticeships_as_apprentice,
        apprenticeships_as_master=student_state.apprenticeships_as_master,
        lessons_as_teacher=student_state.lessons_as_teacher,
        lessons_as_student=tuple(list(student_state.lessons_as_student) + [lid]),
        lessons_explained=student_state.lessons_explained,
        lessons_practiced=student_state.lessons_practiced,
        knowledge_shared_count=student_state.knowledge_shared_count,
        total_skills_mastered=student_state.total_skills_mastered,
    )
    events.append(TeacherAssigned(
        teacher_id=teacher_state.entity_id,
        student_id=student_state.entity_id,
        skill_type=st,
        start_tick=tick,
        tick=tick,
    ))
    return lesson, teacher_out, student_out, events


def complete_lesson(
    lesson: Lesson,
    teacher_state: LearningState,
    student_state: LearningState,
    tick: int,
    success: bool = True,
    teacher_quality: float = 1.0,
) -> tuple[Lesson, LearningState, LearningState, list[Any]]:
    events: list[Any] = []
    st = lesson.skill_type
    teacher_state, t_skill = ensure_skill(teacher_state, st)
    student_state, s_skill = ensure_skill(student_state, st)

    if not success:
        updated_lesson = Lesson(
            lesson_id=lesson.lesson_id,
            teacher_id=lesson.teacher_id,
            student_id=lesson.student_id,
            skill_type=st,
            status="Failed",
            scheduled_tick=lesson.scheduled_tick,
            started_tick=lesson.started_tick,
            completed_tick=tick,
            experience_transferred=0.0,
            teacher_experience_before=lesson.teacher_experience_before,
            student_experience_before=lesson.student_experience_before,
        )
        events.append(LessonCompleted(
            lesson_id=lesson.lesson_id,
            teacher_id=lesson.teacher_id,
            student_id=lesson.student_id,
            skill_type=st,
            success=False,
            experience_transferred=0.0,
            tick=tick,
        ))
        t_out = LearningState(**{**teacher_state.to_dict(), "lessons_explained": tuple(list(teacher_state.lessons_explained) + [lesson.lesson_id])})
        s_out = LearningState(**{**student_state.to_dict(), "lessons_practiced": tuple(list(student_state.lessons_practiced) + [lesson.lesson_id])})
        return updated_lesson, t_out, s_out, events

    base_xfer = get_base_practice_exp(st) * 1.8
    teacher_level = t_skill.level
    student_level = s_skill.level
    level_gap = max(1, teacher_level - student_level + 2)
    xfer = base_xfer * min(2.0, float(level_gap) / 2.0) * max(0.0, float(teacher_quality))
    if xfer < 0:
        xfer = 0.0
    teacher_gain = max(0.0, get_base_practice_exp(st) * 0.15)
    new_t_skill, t_events = add_experience_to_skill(
        t_skill, teacher_gain, source="teaching", tick=tick, context=f"taught:{student_state.entity_id}"
    )
    new_s_skill, s_events = add_experience_to_skill(
        s_skill, xfer, source="teaching", tick=tick, context=f"taught by:{teacher_state.entity_id}", teacher_id=teacher_state.entity_id
    )
    events.append(KnowledgeTransferred(
        from_entity_id=teacher_state.entity_id,
        to_entity_id=student_state.entity_id,
        skill_type=st,
        experience_amount=xfer,
        context="lesson_complete",
        tick=tick,
    ))
    events.extend(t_events)
    events.extend(s_events)
    events.append(LessonCompleted(
        lesson_id=lesson.lesson_id,
        teacher_id=lesson.teacher_id,
        student_id=lesson.student_id,
        skill_type=st,
        success=True,
        experience_transferred=xfer,
        tick=tick,
    ))
    updated_lesson = Lesson(
        lesson_id=lesson.lesson_id,
        teacher_id=lesson.teacher_id,
        student_id=lesson.student_id,
        skill_type=st,
        status="Completed",
        scheduled_tick=lesson.scheduled_tick,
        started_tick=lesson.started_tick,
        completed_tick=tick,
        experience_transferred=xfer,
        teacher_experience_before=lesson.teacher_experience_before,
        student_experience_before=s_skill.experience,
    )
    t_state_exp = _replace_skill_in_state(teacher_state, new_t_skill)
    t_out = LearningState(
        entity_id=t_state_exp.entity_id,
        skills=t_state_exp.skills,
        students_taught=t_state_exp.students_taught,
        teachers_learned_from=t_state_exp.teachers_learned_from,
        apprenticeships_as_apprentice=t_state_exp.apprenticeships_as_apprentice,
        apprenticeships_as_master=t_state_exp.apprenticeships_as_master,
        lessons_as_teacher=t_state_exp.lessons_as_teacher,
        lessons_as_student=t_state_exp.lessons_as_student,
        lessons_explained=tuple(list(t_state_exp.lessons_explained) + [lesson.lesson_id]),
        lessons_practiced=t_state_exp.lessons_practiced,
        knowledge_shared_count=t_state_exp.knowledge_shared_count + 1,
        total_skills_mastered=t_state_exp.total_skills_mastered,
    )
    s_state_exp = _replace_skill_in_state(student_state, new_s_skill)
    s_out = LearningState(
        entity_id=s_state_exp.entity_id,
        skills=s_state_exp.skills,
        students_taught=s_state_exp.students_taught,
        teachers_learned_from=s_state_exp.teachers_learned_from,
        apprenticeships_as_apprentice=s_state_exp.apprenticeships_as_apprentice,
        apprenticeships_as_master=s_state_exp.apprenticeships_as_master,
        lessons_as_teacher=s_state_exp.lessons_as_teacher,
        lessons_as_student=s_state_exp.lessons_as_student,
        lessons_explained=s_state_exp.lessons_explained,
        lessons_practiced=tuple(list(s_state_exp.lessons_practiced) + [lesson.lesson_id]),
        knowledge_shared_count=s_state_exp.knowledge_shared_count,
        total_skills_mastered=s_state_exp.total_skills_mastered,
    )
    return updated_lesson, t_out, s_out, events


def start_apprenticeship(
    apprentice_state: LearningState,
    master_state: LearningState,
    skill_type: str,
    start_tick: int,
    experience_target: float | None = None,
) -> tuple[Apprenticeship, LearningState, LearningState, list[Any]]:
    st = _normalize_identifier(skill_type, SKILL_TYPES, "Farming")
    master_state, m_skill = ensure_skill(master_state, st)
    if experience_target is None:
        target = LEVEL_EXP_TABLE[4] if len(LEVEL_EXP_TABLE) > 4 else 500.0
    else:
        target = max(0.0, float(experience_target))
    aid = make_apprenticeship_id(apprentice_state.entity_id, master_state.entity_id, st)
    app = Apprenticeship(
        apprenticeship_id=aid,
        apprentice_id=apprentice_state.entity_id,
        master_id=master_state.entity_id,
        skill_type=st,
        status="Active",
        start_tick=start_tick,
        end_tick=0,
        experience_target=target,
        experience_earned=0.0,
        lessons_completed=0,
        practices_completed=0,
    )
    events: list[Any] = [ApprenticeshipStarted(
        apprenticeship_id=aid,
        apprentice_id=apprentice_state.entity_id,
        master_id=master_state.entity_id,
        skill_type=st,
        experience_target=target,
        tick=start_tick,
    )]
    new_master = LearningState(
        entity_id=master_state.entity_id,
        skills=dict(master_state.skills),
        students_taught=master_state.students_taught,
        teachers_learned_from=master_state.teachers_learned_from,
        apprenticeships_as_apprentice=master_state.apprenticeships_as_apprentice,
        apprenticeships_as_master=tuple(list(master_state.apprenticeships_as_master) + [aid]),
        lessons_as_teacher=master_state.lessons_as_teacher,
        lessons_as_student=master_state.lessons_as_student,
        lessons_explained=master_state.lessons_explained,
        lessons_practiced=master_state.lessons_practiced,
        knowledge_shared_count=master_state.knowledge_shared_count,
        total_skills_mastered=master_state.total_skills_mastered,
    )
    new_apprentice = LearningState(
        entity_id=apprentice_state.entity_id,
        skills=dict(apprentice_state.skills),
        students_taught=apprentice_state.students_taught,
        teachers_learned_from=tuple(list(apprentice_state.teachers_learned_from) + ([master_state.entity_id] if master_state.entity_id not in apprentice_state.teachers_learned_from else [])),
        apprenticeships_as_apprentice=tuple(list(apprentice_state.apprenticeships_as_apprentice) + [aid]),
        apprenticeships_as_master=apprentice_state.apprenticeships_as_master,
        lessons_as_teacher=apprentice_state.lessons_as_teacher,
        lessons_as_student=apprentice_state.lessons_as_student,
        lessons_explained=apprentice_state.lessons_explained,
        lessons_practiced=apprentice_state.lessons_practiced,
        knowledge_shared_count=apprentice_state.knowledge_shared_count,
        total_skills_mastered=apprentice_state.total_skills_mastered,
    )
    return app, new_apprentice, new_master, events


def complete_apprenticeship(
    app: Apprenticeship,
    apprentice_state: LearningState,
    master_state: LearningState,
    tick: int,
    force: bool = False,
) -> tuple[Apprenticeship, LearningState, LearningState, list[Any]]:
    events: list[Any] = []
    st = app.skill_type
    apprentice_state, a_skill = ensure_skill(apprentice_state, st)
    finished = force or app.experience_earned >= 0.8 * max(1.0, app.experience_target)
    new_status = "Completed" if finished else "Terminated"
    new_app = Apprenticeship(
        apprenticeship_id=app.apprenticeship_id,
        apprentice_id=app.apprentice_id,
        master_id=app.master_id,
        skill_type=st,
        status=new_status,
        start_tick=app.start_tick,
        end_tick=max(app.start_tick, tick),
        experience_target=app.experience_target,
        experience_earned=app.experience_earned,
        lessons_completed=app.lessons_completed,
        practices_completed=app.practices_completed,
    )
    events.append(ApprenticeshipCompleted(
        apprenticeship_id=app.apprenticeship_id,
        apprentice_id=app.apprentice_id,
        master_id=app.master_id,
        skill_type=st,
        total_experience=a_skill.experience,
        final_level=a_skill.level,
        tick=tick,
    ))
    return new_app, apprentice_state, master_state, events


def get_skill_efficiency_multiplier(level: int, max_level: int = MAX_LEVEL) -> float:
    lv = max(0, min(int(level), max_level))
    return 1.0 + 0.08 * lv


def get_skill_defect_rate(level: int, max_level: int = MAX_LEVEL) -> float:
    lv = max(0, min(int(level), max_level))
    return max(0.0, 0.20 - 0.02 * lv)


def get_skill_quality_multiplier(level: int, max_level: int = MAX_LEVEL) -> float:
    lv = max(0, min(int(level), max_level))
    return 1.0 + 0.10 * lv


def find_skilled_workers(
    states_map: Mapping[str, LearningState],
    skill_type: str,
    min_level: int = 1,
    candidate_ids: Sequence[str] | None = None,
    top_n: int = 10,
) -> list[tuple[str, int, float]]:
    st = _normalize_identifier(skill_type, SKILL_TYPES, "Farming")
    results: list[tuple[str, int, float]] = []
    if candidate_ids is None:
        keys = list(states_map.keys())
    else:
        keys = [str(k) for k in candidate_ids]
    for eid in keys:
        if eid not in states_map:
            continue
        ls = states_map[eid]
        if not isinstance(ls, LearningState):
            continue
        skill = ls.get_skill(st)
        if skill is None:
            continue
        if skill.level < min_level:
            continue
        results.append((eid, skill.level, skill.experience))
    results.sort(key=lambda t: (-t[1], -t[2]))
    return results[: max(1, int(top_n))]


def lookup_skills_by_entity(
    states_map: Mapping[str, LearningState],
    entity_id: str,
) -> dict[str, tuple[int, float]]:
    out: dict[str, tuple[int, float]] = {}
    key = str(entity_id)
    if key not in states_map:
        return out
    ls = states_map[key]
    if not isinstance(ls, LearningState):
        return out
    for st in SKILL_TYPES:
        s = ls.get_skill(st)
        if s is None:
            out[st] = (0, 0.0)
        else:
            out[st] = (s.level, s.experience)
    return out


def lookup_apprentice_of(
    apps_map: Mapping[str, Apprenticeship],
    master_id: str,
    status: str = "Active",
) -> list[Apprenticeship]:
    out = []
    for app in apps_map.values():
        if not isinstance(app, Apprenticeship):
            continue
        if app.master_id != master_id:
            continue
        if status and app.status != status:
            continue
        out.append(app)
    return out


def compute_learning_summary(
    states_map: Mapping[str, LearningState],
) -> dict[str, Any]:
    entities = len(states_map)
    total_skills = 0
    total_levels = 0
    mastered = 0
    total_experience = 0.0
    teachers: set[str] = set()
    students: set[str] = set()
    for ls in states_map.values():
        if not isinstance(ls, LearningState):
            continue
        total_skills += ls.skill_count
        total_levels += ls.total_levels
        mastered += ls.total_skills_mastered
        for s in ls.skills.values():
            total_experience += s.experience
        for t in ls.teachers_learned_from:
            teachers.add(t)
        for s2 in ls.students_taught:
            students.add(s2)
    return {
        "entities": entities,
        "total_skills": total_skills,
        "total_levels": total_levels,
        "total_mastered": mastered,
        "total_experience": round(total_experience, 4),
        "unique_teachers": len(teachers),
        "unique_students": len(students),
    }


def summarize_learning_delta(
    before: LearningState,
    after: LearningState,
) -> dict[str, tuple[int, float, float]]:
    out: dict[str, tuple[int, float, float]] = {}
    for st in SKILL_TYPES:
        b_lv, b_exp = (0, 0.0)
        a_lv, a_exp = (0, 0.0)
        bs = before.get_skill(st)
        if bs is not None:
            b_lv, b_exp = bs.level, bs.experience
        a_s = after.get_skill(st)
        if a_s is not None:
            a_lv, a_exp = a_s.level, a_s.experience
        lv_delta = a_lv - b_lv
        exp_delta = a_exp - b_exp
        if lv_delta != 0 or abs(exp_delta) > 1e-9:
            out[st] = (lv_delta, exp_delta, a_exp)
    return out
