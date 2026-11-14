from __future__ import annotations

import copy
from dataclasses import field as _field, dataclass
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from sim_world.core.contracts import TransitionProposal
from sim_world.core.ids import EntityId

from .learning_events import (
    LEARNING_EVENT_TYPES,
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
    make_learning_state_id,
    make_lesson_id,
    make_skill_id,
    next_level_exp,
)
from .learning_rules import (
    SKILL_PRACTICE_BASE_EXP,
    add_experience_to_skill,
    complete_apprenticeship,
    complete_lesson,
    compute_learning_summary,
    ensure_learning_state_for,
    ensure_skill,
    find_skilled_workers,
    get_base_practice_exp,
    get_skill_defect_rate,
    get_skill_efficiency_multiplier,
    get_skill_quality_multiplier,
    lookup_apprentice_of,
    lookup_skills_by_entity,
    record_observation,
    record_practice,
    start_apprenticeship,
    start_lesson,
    summarize_learning_delta,
)


def _extract_context(context: Any) -> dict[str, Any]:
    info: dict[str, Any] = {
        "state": {},
        "world_id": None,
        "tick_number": 0,
        "correlation_id": f"learning_{datetime.now(timezone.utc).strftime('%s')}",
        "revision": None,
    }
    if context is None:
        return info
    for attr in ("current_state", "state", "_state"):
        state = getattr(context, attr, None)
        if isinstance(state, Mapping):
            info["state"] = dict(state)
            break
    raw_world_id = getattr(context, "world_id", None)
    if raw_world_id is None:
        raw_world_id = info["world_id"]
    info["world_id"] = raw_world_id
    info["tick_number"] = int(getattr(context, "current_tick_number", info["tick_number"]) or info["tick_number"])
    tc = getattr(context, "tick_context", None)
    info["tick_context"] = tc
    if tc is not None:
        info["tick_number"] = int(getattr(tc, "tick_number", info["tick_number"]) or info["tick_number"])
        info["correlation_id"] = str(getattr(tc, "correlation_id", info["correlation_id"]) or info["correlation_id"])
    info["revision"] = getattr(context, "committed_revision", None) or getattr(context, "state_revision", None)
    info["committed_revision"] = info["revision"]
    return info


def _id_str(entity: Any) -> str:
    if entity is None:
        return ""
    value = getattr(entity, "value", None)
    if isinstance(value, str):
        return value
    if isinstance(value, EntityId):
        return str(value.value)
    if isinstance(entity, EntityId):
        return str(entity.value)
    return str(entity)


def _read_learning_state(state: Mapping[str, Any], entity_id: str) -> LearningState:
    key = str(entity_id)
    learning_map = state.get("learning_states", {}) if isinstance(state, Mapping) else {}
    if isinstance(learning_map, Mapping):
        raw = learning_map.get(key)
        if isinstance(raw, LearningState):
            return raw
        if isinstance(raw, Mapping):
            return LearningState.from_dict(raw)
    return build_default_learning_state(key)


def _read_learning_states(state: Mapping[str, Any]) -> dict[str, LearningState]:
    learning_map = state.get("learning_states", {}) if isinstance(state, Mapping) else {}
    out: dict[str, LearningState] = {}
    if not isinstance(learning_map, Mapping):
        return out
    for k, v in learning_map.items():
        if isinstance(v, LearningState):
            out[str(k)] = v
        elif isinstance(v, Mapping):
            out[str(k)] = LearningState.from_dict(v)
    return out


def _read_apprenticeships(state: Mapping[str, Any]) -> dict[str, Apprenticeship]:
    apps_map = state.get("learning_apprenticeships", {}) if isinstance(state, Mapping) else {}
    out: dict[str, Apprenticeship] = {}
    if not isinstance(apps_map, Mapping):
        return out
    for k, v in apps_map.items():
        if isinstance(v, Apprenticeship):
            out[str(k)] = v
        elif isinstance(v, Mapping):
            out[str(k)] = Apprenticeship.from_dict(v)
    return out


def _read_lessons(state: Mapping[str, Any]) -> dict[str, Lesson]:
    less = state.get("learning_lessons", {}) if isinstance(state, Mapping) else {}
    out: dict[str, Lesson] = {}
    if not isinstance(less, Mapping):
        return out
    for k, v in less.items():
        if isinstance(v, Lesson):
            out[str(k)] = v
        elif isinstance(v, Mapping):
            out[str(k)] = Lesson.from_dict(v)
    return out


def _make_proposal(
    info: Mapping[str, Any],
    patch_learning: Mapping[str, Any] | None,
    metadata: Mapping[str, Any] | None = None,
    description: str = "learning update",
) -> TransitionProposal | tuple[()]:
    if (patch_learning is None or len(patch_learning) == 0) and not metadata:
        return ()
    patch: dict[str, Any] = {}
    if patch_learning:
        patch["learning"] = dict(patch_learning)
    meta = {
        "domain": "learning",
        "description": str(description),
        "world_id": str(info.get("world_id", "")),
        "tick_number": int(info.get("tick_number", 0)),
    }
    if metadata:
        for mk, mv in metadata.items():
            meta[str(mk)] = mv
    world_id_raw = info.get("world_id")
    world_id = world_id_raw
    tick_ctx = info.get("tick_context")
    tick_id = None
    if tick_ctx is not None:
        tick_id = getattr(tick_ctx, "tick_id", None)
    state_revision = None
    correlation_id = str(info.get("correlation_id") or f"learning:{hash(str(description)) & 0xFFFFFFFF:x}")
    subject = "domain.learning"
    return TransitionProposal(
        world_id=world_id,
        tick_id=tick_id,
        state_revision=state_revision,
        correlation_id=correlation_id,
        subject=subject,
        patch=dict(patch),
        description=str(description),
        metadata=dict(meta),
    )


def register(engine: Any) -> None:
    engine.register_domain("learning", lambda e, ctx: apply(ctx))


def initialize_valley_learning(kernel: Any) -> dict[str, Any]:
    if kernel is None:
        return {}
    state_map = getattr(kernel, "_state", None)
    if state_map is None:
        state_map = {}
    existing = state_map.get("learning_states") if isinstance(state_map, Mapping) else None
    if not isinstance(existing, dict):
        existing = {}
    villager_ids = set()
    for key in ("villagers", "population", "entities"):
        val = state_map.get(key) if isinstance(state_map, Mapping) else None
        if isinstance(val, Mapping):
            for vk in val.keys():
                villager_ids.add(str(vk))
        elif isinstance(val, (list, tuple)):
            for item in val:
                iid = getattr(item, "entity_id", None) or getattr(item, "id", None) or item
                villager_ids.add(_id_str(iid))
    for vid in villager_ids:
        if vid not in existing:
            existing[vid] = build_default_learning_state(vid).to_dict()
    if not isinstance(state_map, dict):
        return {}
    state_map["learning_states"] = existing
    state_map.setdefault("learning_apprenticeships", {})
    state_map.setdefault("learning_lessons", {})
    state_map.setdefault(
        "learning_summary",
        {"entities": len(existing), "total_skills": 0, "total_levels": 0},
    )
    return {
        "learning_states_count": len(existing),
        "apprenticeships": len(state_map["learning_apprenticeships"]),
        "lessons": len(state_map["learning_lessons"]),
    }


def apply(context: Any) -> TransitionProposal | tuple[()]:
    info = _extract_context(context)
    state = info.get("state") or {}
    learning_states = _read_learning_states(state)
    apps = _read_apprenticeships(state)
    lessons = _read_lessons(state)
    if not learning_states and not apps and not lessons:
        return ()
    changed: dict[str, Any] = {}
    events: list[Any] = []

    active_apps = [a for a in apps.values() if a.status == "Active"]
    if active_apps:
        changed_apps = {}
        for app in active_apps:
            increment = min(max(1.0, get_base_practice_exp(app.skill_type) * 0.02), 5.0)
            new_earned = min(app.experience_target + 1000.0, app.experience_earned + increment)
            if new_earned != app.experience_earned:
                updated = Apprenticeship(
                    apprenticeship_id=app.apprenticeship_id,
                    apprentice_id=app.apprentice_id,
                    master_id=app.master_id,
                    skill_type=app.skill_type,
                    status=app.status,
                    start_tick=app.start_tick,
                    end_tick=app.end_tick,
                    experience_target=app.experience_target,
                    experience_earned=new_earned,
                    lessons_completed=app.lessons_completed,
                    practices_completed=app.practices_completed + 1,
                )
                changed_apps[app.apprenticeship_id] = updated.to_dict()
        if changed_apps:
            patch_apps = dict(state.get("learning_apprenticeships", {})) if isinstance(state.get("learning_apprenticeships", {}), Mapping) else {}
            for k, v in changed_apps.items():
                patch_apps[k] = v
            changed["learning_apprenticeships"] = patch_apps

    if not changed and not events:
        return ()
    meta = {
        "auto_progress": bool(active_apps),
        "events": tuple(events),
    }
    return _make_proposal(info, changed, meta, "learning auto apply")


def practice_skill_action(
    context: Any,
    entity_id: Any,
    skill_type: str,
    context_label: str = "",
    success: bool = True,
    practice_count: int = 1,
    skill_bonus_mult: float = 1.0,
    teacher_id: Any = "",
) -> TransitionProposal | tuple[()]:
    info = _extract_context(context)
    state = info.get("state") or {}
    eid = _id_str(entity_id)
    tid = _id_str(teacher_id) if teacher_id else ""
    if not eid:
        return ()
    ls = _read_learning_state(state, eid)
    ls_snap = copy.deepcopy(ls.to_dict())
    new_ls, events = record_practice(
        ls, skill_type, info["tick_number"] or 1, context_label, success, practice_count, skill_bonus_mult, tid
    )
    if new_ls.to_dict() == ls_snap:
        return ()
    new_state_map = dict(state.get("learning_states", {})) if isinstance(state.get("learning_states", {}), Mapping) else {}
    new_state_map[eid] = new_ls.to_dict()
    patch: dict[str, Any] = {"learning_states": new_state_map}
    meta: dict[str, Any] = {
        "action": "practice_skill",
        "entity": eid,
        "skill_type": _normalize_identifier(skill_type, SKILL_TYPES, "Farming"),
        "events": tuple(events),
        "delta": summarize_learning_delta(ls, new_ls),
    }
    if tid:
        meta["teacher"] = tid
    return _make_proposal(info, patch, meta, f"practice skill {skill_type} for {eid}")


def observe_work_action(
    context: Any,
    observer_id: Any,
    practitioner_id: Any,
    skill_type: str,
    context_label: str = "",
    proximity: int = 1,
) -> TransitionProposal | tuple[()]:
    info = _extract_context(context)
    state = info.get("state") or {}
    oid = _id_str(observer_id)
    pid = _id_str(practitioner_id)
    if not oid or not pid or oid == pid:
        return ()
    obs_ls = _read_learning_state(state, oid)
    pract_ls = _read_learning_state(state, pid)
    obs_snap = copy.deepcopy(obs_ls.to_dict())
    new_obs, events = record_observation(
        obs_ls, pract_ls, skill_type, info["tick_number"] or 1, context_label, proximity
    )
    if new_obs.to_dict() == obs_snap:
        return ()
    new_state_map = dict(state.get("learning_states", {})) if isinstance(state.get("learning_states", {}), Mapping) else {}
    new_state_map[oid] = new_obs.to_dict()
    patch: dict[str, Any] = {"learning_states": new_state_map}
    meta: dict[str, Any] = {
        "action": "observe_work",
        "observer_id": oid,
        "practitioner_id": pid,
        "skill_type": _normalize_identifier(skill_type, SKILL_TYPES, "Farming"),
        "events": tuple(events),
    }
    return _make_proposal(info, patch, meta, f"{oid} observes {pid} {skill_type}")


def teach_skill_action(
    context: Any,
    teacher_id: Any,
    student_id: Any,
    skill_type: str,
    success: bool = True,
    teacher_quality: float = 1.0,
) -> TransitionProposal | tuple[()]:
    info = _extract_context(context)
    state = info.get("state") or {}
    tid = _id_str(teacher_id)
    sid = _id_str(student_id)
    if not tid or not sid or tid == sid:
        return ()
    t_state = _read_learning_state(state, tid)
    s_state = _read_learning_state(state, sid)
    tick = info["tick_number"] or 1
    lesson, t1, s1, start_evs = start_lesson(t_state, s_state, skill_type, tick)
    complete, t2, s2, end_evs = complete_lesson(
        lesson, t1, s1, tick, success=success, teacher_quality=teacher_quality
    )
    new_ls_map = dict(state.get("learning_states", {})) if isinstance(state.get("learning_states", {}), Mapping) else {}
    new_ls_map[tid] = t2.to_dict()
    new_ls_map[sid] = s2.to_dict()
    new_lessons_map = dict(state.get("learning_lessons", {})) if isinstance(state.get("learning_lessons", {}), Mapping) else {}
    new_lessons_map[complete.lesson_id] = complete.to_dict()
    patch: dict[str, Any] = {
        "learning_states": new_ls_map,
        "learning_lessons": new_lessons_map,
    }
    all_events = list(start_evs) + list(end_evs)
    meta: dict[str, Any] = {
        "action": "teach_skill",
        "lesson_id": complete.lesson_id,
        "teacher_id": tid,
        "student_id": sid,
        "skill_type": _normalize_identifier(skill_type, SKILL_TYPES, "Farming"),
        "success": success,
        "events": tuple(all_events),
    }
    return _make_proposal(info, patch, meta, f"teach {skill_type} {tid}->{sid}")


def start_apprenticeship_action(
    context: Any,
    apprentice_id: Any,
    master_id: Any,
    skill_type: str,
    experience_target: float | None = None,
) -> TransitionProposal | tuple[()]:
    info = _extract_context(context)
    state = info.get("state") or {}
    aid = _id_str(apprentice_id)
    mid = _id_str(master_id)
    if not aid or not mid or aid == mid:
        return ()
    a_state = _read_learning_state(state, aid)
    m_state = _read_learning_state(state, mid)
    tick = info["tick_number"] or 1
    app, a2, m2, events = start_apprenticeship(
        a_state, m_state, skill_type, start_tick=tick, experience_target=experience_target
    )
    new_ls_map = dict(state.get("learning_states", {})) if isinstance(state.get("learning_states", {}), Mapping) else {}
    new_ls_map[aid] = a2.to_dict()
    new_ls_map[mid] = m2.to_dict()
    new_apps = dict(state.get("learning_apprenticeships", {})) if isinstance(state.get("learning_apprenticeships", {}), Mapping) else {}
    new_apps[app.apprenticeship_id] = app.to_dict()
    patch: dict[str, Any] = {
        "learning_states": new_ls_map,
        "learning_apprenticeships": new_apps,
    }
    meta: dict[str, Any] = {
        "action": "start_apprenticeship",
        "apprenticeship_id": app.apprenticeship_id,
        "apprentice_id": aid,
        "master_id": mid,
        "skill_type": _normalize_identifier(skill_type, SKILL_TYPES, "Farming"),
        "experience_target": app.experience_target,
        "events": tuple(events),
    }
    return _make_proposal(info, patch, meta, f"start apprenticeship {aid}->{mid} ({skill_type})")


def complete_lesson_action(
    context: Any,
    lesson_id: str,
    success: bool = True,
    teacher_quality: float = 1.0,
) -> TransitionProposal | tuple[()]:
    info = _extract_context(context)
    state = info.get("state") or {}
    lid = str(lesson_id)
    lessons_map = _read_lessons(state)
    lesson = lessons_map.get(lid)
    if lesson is None:
        return ()
    t_state = _read_learning_state(state, lesson.teacher_id)
    s_state = _read_learning_state(state, lesson.student_id)
    tick = info["tick_number"] or (lesson.completed_tick + 1)
    completed, t2, s2, events = complete_lesson(lesson, t_state, s_state, tick, success, teacher_quality)
    new_ls_map = dict(state.get("learning_states", {})) if isinstance(state.get("learning_states", {}), Mapping) else {}
    new_ls_map[lesson.teacher_id] = t2.to_dict()
    new_ls_map[lesson.student_id] = s2.to_dict()
    new_lessons = dict(state.get("learning_lessons", {})) if isinstance(state.get("learning_lessons", {}), Mapping) else {}
    new_lessons[lid] = completed.to_dict()
    patch: dict[str, Any] = {
        "learning_states": new_ls_map,
        "learning_lessons": new_lessons,
    }
    meta: dict[str, Any] = {
        "action": "complete_lesson",
        "lesson_id": lid,
        "teacher_id": lesson.teacher_id,
        "student_id": lesson.student_id,
        "skill_type": lesson.skill_type,
        "success": success,
        "events": tuple(events),
    }
    return _make_proposal(info, patch, meta, f"complete lesson {lid}")


def finish_apprenticeship_action(
    context: Any,
    apprenticeship_id: str,
    force: bool = False,
) -> TransitionProposal | tuple[()]:
    info = _extract_context(context)
    state = info.get("state") or {}
    aid = str(apprenticeship_id)
    apps = _read_apprenticeships(state)
    app = apps.get(aid)
    if app is None:
        return ()
    a_state = _read_learning_state(state, app.apprentice_id)
    m_state = _read_learning_state(state, app.master_id)
    tick = info["tick_number"] or max(app.start_tick + 1, 1)
    completed, a2, m2, events = complete_apprenticeship(app, a_state, m_state, tick, force)
    new_ls_map = dict(state.get("learning_states", {})) if isinstance(state.get("learning_states", {}), Mapping) else {}
    new_ls_map[app.apprentice_id] = a2.to_dict()
    new_ls_map[app.master_id] = m2.to_dict()
    new_apps = dict(state.get("learning_apprenticeships", {})) if isinstance(state.get("learning_apprenticeships", {}), Mapping) else {}
    new_apps[aid] = completed.to_dict()
    patch: dict[str, Any] = {
        "learning_states": new_ls_map,
        "learning_apprenticeships": new_apps,
    }
    meta: dict[str, Any] = {
        "action": "finish_apprenticeship",
        "apprenticeship_id": aid,
        "apprentice_id": app.apprentice_id,
        "master_id": app.master_id,
        "skill_type": app.skill_type,
        "status": completed.status,
        "events": tuple(events),
    }
    return _make_proposal(info, patch, meta, f"finish apprenticeship {aid}")


def advance_experience_action(
    context: Any,
    entity_id: Any,
    skill_type: str,
    experience_delta: float,
    source: str = "simulation",
    context_label: str = "",
) -> TransitionProposal | tuple[()]:
    info = _extract_context(context)
    state = info.get("state") or {}
    eid = _id_str(entity_id)
    if not eid:
        return ()
    delta = max(0.0, float(experience_delta))
    if delta <= 0:
        return ()
    ls = _read_learning_state(state, eid)
    ls, skill = ensure_skill(ls, skill_type)
    snap = copy.deepcopy(ls.to_dict())
    new_skill, events = add_experience_to_skill(
        skill, delta, source=source, tick=info["tick_number"] or 1, context=context_label
    )
    new_skills = dict(ls.skills)
    new_skills[new_skill.skill_type] = new_skill
    mastered = sum(1 for s in new_skills.values() if s.is_mastered)
    new_ls = LearningState(
        entity_id=ls.entity_id,
        skills=new_skills,
        students_taught=ls.students_taught,
        teachers_learned_from=ls.teachers_learned_from,
        apprenticeships_as_apprentice=ls.apprenticeships_as_apprentice,
        apprenticeships_as_master=ls.apprenticeships_as_master,
        lessons_as_teacher=ls.lessons_as_teacher,
        lessons_as_student=ls.lessons_as_student,
        lessons_explained=ls.lessons_explained,
        lessons_practiced=ls.lessons_practiced,
        knowledge_shared_count=ls.knowledge_shared_count,
        total_skills_mastered=max(ls.total_skills_mastered, mastered),
    )
    if new_ls.to_dict() == snap:
        return ()
    new_ls_map = dict(state.get("learning_states", {})) if isinstance(state.get("learning_states", {}), Mapping) else {}
    new_ls_map[eid] = new_ls.to_dict()
    patch: dict[str, Any] = {"learning_states": new_ls_map}
    meta: dict[str, Any] = {
        "action": "advance_experience",
        "entity": eid,
        "skill_type": _normalize_identifier(skill_type, SKILL_TYPES, "Farming"),
        "delta": delta,
        "source": str(source),
        "events": tuple(events),
    }
    return _make_proposal(info, patch, meta, f"advance experience {eid} {skill_type}+{delta}")


def find_skilled_workers_for(context: Any, skill_type: str, min_level: int = 1, top_n: int = 10) -> list[tuple[str, int, float]]:
    info = _extract_context(context)
    state = info.get("state") or {}
    states_map = _read_learning_states(state)
    return find_skilled_workers(states_map, skill_type, min_level, top_n=top_n)


def get_learning_states(context: Any) -> dict[str, LearningState]:
    info = _extract_context(context)
    state = info.get("state") or {}
    return _read_learning_states(state)


def get_entity_skills(context: Any, entity_id: Any) -> dict[str, tuple[int, float]]:
    info = _extract_context(context)
    state = info.get("state") or {}
    states_map = _read_learning_states(state)
    eid = _id_str(entity_id)
    return lookup_skills_by_entity(states_map, eid)


def get_learning_summary(context: Any) -> dict[str, Any]:
    info = _extract_context(context)
    state = info.get("state") or {}
    states_map = _read_learning_states(state)
    return compute_learning_summary(states_map)


def get_apprenticeships(context: Any) -> dict[str, Apprenticeship]:
    info = _extract_context(context)
    state = info.get("state") or {}
    return _read_apprenticeships(state)


def get_lessons(context: Any) -> dict[str, Lesson]:
    info = _extract_context(context)
    state = info.get("state") or {}
    return _read_lessons(state)


def generate_learning_goals(kernel: Any) -> TransitionProposal | tuple[()]:
    if kernel is None:
        return ()
    info = {
        "world_id": str(getattr(kernel, "world_id", "") or ""),
        "tick_number": int(getattr(kernel, "current_tick_number", 0) or 0),
        "correlation_id": f"learning_goals_{datetime.now(timezone.utc).strftime('%s')}",
    }
    current_state = getattr(kernel, "_state", None) or {}
    learning_map = current_state.get("learning_states", {}) if isinstance(current_state, Mapping) else {}
    recommended: list[str] = []
    if isinstance(learning_map, Mapping):
        for eid in sorted(learning_map.keys())[:5]:
            recommended.append(str(eid))
    meta = {
        "domain": "learning",
        "action": "generate_learning_goals",
        "candidate_entities": tuple(recommended),
    }
    return _make_proposal(info, {}, meta, "planner learning goals (observe-only)")
