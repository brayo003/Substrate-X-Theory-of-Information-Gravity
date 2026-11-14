from __future__ import annotations

import copy
import unittest
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping

from sim_world import KernelConfig, WorldKernel
from sim_world.core.contracts import TickContext, TransitionProposal
from sim_world.core.ids import TickId
from sim_world.domains import register_all
from sim_world.domains.agriculture import initialize_valley_agriculture
from sim_world.domains.conversation import (
    initialize_valley_conversations,
    teach_action,
    start_conversation_action,
    end_conversation_action,
    resolve_outcome,
    add_turn,
    start_conversation,
)
from sim_world.domains.economy import initialize_valley_economy
from sim_world.domains.learning import (
    APPRENTICESHIP_STATUSES,
    LEARNING_EVENT_TYPES,
    LEVEL_EXP_TABLE,
    LEVEL_NAMES,
    LESSON_STATUSES,
    MAX_LEVEL,
    SKILL_PRACTICE_BASE_EXP,
    SKILL_TO_OCCUPATION,
    SKILL_TYPES,
    Apprenticeship,
    ApprenticeshipCompleted,
    ApprenticeshipStarted,
    ExperienceGained,
    KnowledgeTransferred,
    LearningState,
    Lesson,
    LessonCompleted,
    LessonStarted,
    LevelIncreased,
    ObservationLearning,
    PracticeRecord,
    Skill,
    SkillMastered,
    SkillPracticeCompleted,
    SkillPracticeStarted,
    TeacherAssigned,
    TeacherRecord,
    add_experience_to_skill,
    advance_experience_action,
    apply,
    build_default_learning_state,
    build_default_skills_for,
    complete_apprenticeship,
    complete_lesson,
    complete_lesson_action,
    compute_learning_summary,
    ensure_learning_state_for,
    ensure_skill,
    finish_apprenticeship_action,
    find_skilled_workers,
    find_skilled_workers_for,
    generate_learning_goals,
    get_apprenticeships,
    get_base_practice_exp,
    get_entity_skills,
    get_learning_states,
    get_learning_summary,
    get_lessons,
    get_skill_defect_rate,
    get_skill_efficiency_multiplier,
    get_skill_quality_multiplier,
    initialize_valley_learning,
    level_from_experience,
    level_name,
    lookup_apprentice_of,
    lookup_skills_by_entity,
    make_apprenticeship_id,
    make_learning_state_id,
    make_lesson_id,
    make_skill_id,
    next_level_exp,
    observe_work_action,
    practice_skill_action,
    record_observation,
    record_practice,
    start_apprenticeship,
    start_lesson,
    summarize_learning_delta,
    teach_skill_action,
)
from sim_world.domains.population import initialize_valley_population
from sim_world.domains.relationships import initialize_valley_relationships
from sim_world.domains.resources import initialize_valley_resources
from sim_world.domains.terrain import initialize_valley_terrain


class Loop9LearningTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = KernelConfig(
            world_name="valley_world_learning",
            seed="learning-seed-009",
            initial_state={"mode": "valley_learning_simulation"},
        )
        self.kernel = WorldKernel(self.config)
        register_all(self.kernel.simulation_engine)
        self.terrain_entities = initialize_valley_terrain(self.kernel)
        self.villager_entities = initialize_valley_population(self.kernel)
        self.building_entities = initialize_valley_resources(self.kernel)
        self.crop_fields = initialize_valley_agriculture(self.kernel)
        self.economy_state = initialize_valley_economy(self.kernel)
        self.relationships_state = initialize_valley_relationships(self.kernel)
        self.conversation_state = initialize_valley_conversations(self.kernel)
        self.learning_state = initialize_valley_learning(self.kernel)

    def _create_tick_context(self, correlation_id: str = "test_learn_correlation") -> TickContext:
        tick_id = TickId.new(self.kernel.world_id, self.kernel.current_tick_number)
        rev = self.kernel.current_revision.revision_id if self.kernel.current_revision else None
        return TickContext(
            world_id=self.kernel.world_id,
            tick_id=tick_id,
            state_revision=rev,
            parent_revision=rev,
            timestamp=datetime.now(timezone.utc),
            correlation_id=correlation_id,
        )

    def _make_ctx(self) -> Any:
        return type("Ctx", (), {
            "current_state": dict(self.kernel.current_state),
            "world_id": self.kernel.world_id,
            "current_tick_number": int(self.kernel.current_tick_number),
            "tick_context": self._create_tick_context(),
            "committed_revision": self.kernel.current_revision.revision_id if self.kernel.current_revision else None,
        })()

    # ============================================================
    # Initial skill assignment and model validation
    # ============================================================

    def test_core_skill_types_registered(self) -> None:
        expected_skills = (
            "Farming", "Cooking", "Blacksmithing", "Carpentry", "Hunting",
            "Trading", "Leadership", "Medicine", "Crafting", "Social",
        )
        for sk in expected_skills:
            self.assertIn(sk, SKILL_TYPES)
        self.assertEqual(len(SKILL_TYPES), 10)

    def test_status_constants_registered(self) -> None:
        for status in ("Pending", "Active", "Completed", "Terminated"):
            self.assertIn(status, APPRENTICESHIP_STATUSES)
        for status in ("Scheduled", "Started", "Explained", "Practiced", "Completed", "Failed"):
            self.assertIn(status, LESSON_STATUSES)
        for name in ("Novice", "Apprentice", "Journeyman", "Expert", "Master", "Grandmaster"):
            self.assertIn(name, LEVEL_NAMES)
        self.assertEqual(MAX_LEVEL, 10)

    def test_event_types_registered(self) -> None:
        required_events = (
            "SkillPracticeStarted", "SkillPracticeCompleted", "ExperienceGained",
            "LevelIncreased", "LessonStarted", "LessonCompleted", "TeacherAssigned",
            "ApprenticeshipStarted", "ApprenticeshipCompleted", "ObservationLearning",
            "SkillMastered", "KnowledgeTransferred",
        )
        for evt in required_events:
            self.assertIn(evt, LEARNING_EVENT_TYPES)
        self.assertEqual(len(LEARNING_EVENT_TYPES), 12)

    def test_skill_model_fields(self) -> None:
        sid = make_skill_id("Mira", "Farming")
        s = Skill(
            skill_id=sid,
            skill_type="Farming",
            entity_id="Mira",
            experience=250.0,
            level=1,
            max_level=MAX_LEVEL,
            last_practiced_tick=5,
            teacher_history=(TeacherRecord(
                teacher_id="Joren", skill_type="Farming", first_tick=1, last_tick=3, total_lessons=2
            ),),
            practice_history=(PracticeRecord(
                tick=3, skill_type="Farming", context="planted_wheat", experience_gained=15.0
            ),),
        )
        self.assertEqual(s.skill_id, sid)
        self.assertEqual(s.skill_type, "Farming")
        self.assertEqual(s.entity_id, "Mira")
        self.assertGreaterEqual(s.level, level_from_experience(250.0))
        self.assertIn(s.level_name, LEVEL_NAMES)
        self.assertGreaterEqual(s.next_level_exp, 250.0)
        self.assertGreaterEqual(s.progress_pct, 0.0)
        self.assertLessEqual(s.progress_pct, 1.0)
        self.assertFalse(s.is_mastered)

        d = s.to_dict()
        self.assertIsInstance(d, dict)
        restored = Skill.from_dict(d)
        self.assertEqual(restored.skill_id, s.skill_id)
        self.assertEqual(restored.level, s.level)
        self.assertEqual(restored.experience, s.experience)
        self.assertEqual(restored.last_practiced_tick, s.last_practiced_tick)

    def test_learning_state_model_fields(self) -> None:
        ls = build_default_learning_state("Mira")
        self.assertEqual(ls.entity_id, "Mira")
        self.assertEqual(ls.skill_count, len(SKILL_TYPES))
        self.assertEqual(ls.total_levels, 0)
        for st in SKILL_TYPES:
            self.assertIsNotNone(ls.get_skill(st))
            self.assertEqual(ls.get_level(st), 0)
            self.assertEqual(ls.get_experience(st), 0.0)

        d = ls.to_dict()
        self.assertIsInstance(d, dict)
        restored = LearningState.from_dict(d)
        self.assertEqual(restored.entity_id, ls.entity_id)
        self.assertEqual(restored.skill_count, ls.skill_count)
        self.assertEqual(restored.get_level("Farming"), 0)

    def test_initial_skill_assignment_for_villagers(self) -> None:
        learning_map = self.kernel.current_state.get("learning_states", {})
        self.assertTrue(isinstance(learning_map, (dict, Mapping)))
        state_count = self.learning_state.get("learning_states_count", 0)
        self.assertGreaterEqual(state_count, 1)
        self.assertGreaterEqual(len(learning_map), 1)
        for lid, lval in learning_map.items():
            lsd: dict[str, Any]
            if hasattr(lval, "to_dict"):
                lsd = lval.to_dict()
            elif isinstance(lval, MappingProxyType):
                lsd = {str(k): (dict(v) if isinstance(v, MappingProxyType) else v) for k, v in lval.items()}
                if "skills" in lsd:
                    inner = lsd["skills"]
                    if isinstance(inner, MappingProxyType):
                        lsd["skills"] = {
                            str(sk): (dict(sv) if isinstance(sv, MappingProxyType) else sv)
                            for sk, sv in inner.items()
                        }
            elif isinstance(lval, dict):
                lsd = lval
            else:
                continue
            ls = LearningState.from_dict(lsd)
            self.assertGreaterEqual(ls.skill_count, len(SKILL_TYPES))
            self.assertEqual(ls.entity_id, lsd.get("entity_id", ls.entity_id))
            break
        self.assertIn("learning_apprenticeships", self.kernel.current_state)
        self.assertIn("learning_lessons", self.kernel.current_state)

    def test_level_progression_table(self) -> None:
        self.assertEqual(len(LEVEL_EXP_TABLE), MAX_LEVEL + 2)
        self.assertEqual(LEVEL_EXP_TABLE[0], 0.0)
        for i in range(1, MAX_LEVEL + 1):
            self.assertGreater(LEVEL_EXP_TABLE[i], LEVEL_EXP_TABLE[i - 1])

        self.assertEqual(level_from_experience(-1.0), 0)
        self.assertEqual(level_from_experience(0.0), 0)
        lv5_threshold = LEVEL_EXP_TABLE[5]
        self.assertEqual(level_from_experience(lv5_threshold), 5)
        self.assertEqual(level_from_experience(LEVEL_EXP_TABLE[MAX_LEVEL] + 1000.0), MAX_LEVEL)

    def test_level_names_deterministic(self) -> None:
        self.assertEqual(level_name(0), "Novice")
        self.assertEqual(level_name(1), "Apprentice")
        self.assertEqual(level_name(3), "Journeyman")
        self.assertEqual(level_name(5), "Expert")
        self.assertEqual(level_name(7), "Master")
        self.assertEqual(level_name(9), "Grandmaster")
        self.assertEqual(level_name(MAX_LEVEL), "Grandmaster")
        self.assertEqual(level_name(-5), "Novice")

    def test_id_generation_deterministic(self) -> None:
        sid1 = make_skill_id("Mira", "Farming")
        sid2 = make_skill_id("Mira", "Farming")
        self.assertEqual(sid1, sid2, "skill ids must be deterministic")
        self.assertIn("Farming", sid1)
        self.assertIn("Mira", sid1)

        lsid1 = make_learning_state_id("Mira")
        lsid2 = make_learning_state_id("Mira")
        self.assertEqual(lsid1, lsid2)

        aid1 = make_apprenticeship_id("Pell", "Joren", "Blacksmithing")
        aid2 = make_apprenticeship_id("Pell", "Joren", "Blacksmithing")
        self.assertEqual(aid1, aid2)

        lid1 = make_lesson_id("Joren", "Pell", "Blacksmithing", 10)
        lid2 = make_lesson_id("Joren", "Pell", "Blacksmithing", 10)
        self.assertEqual(lid1, lid2)
        lid3 = make_lesson_id("Joren", "Pell", "Blacksmithing", 11)
        self.assertNotEqual(lid1, lid3)

    # ============================================================
    # Experience accumulation & level progression
    # ============================================================

    def test_experience_cannot_be_negative(self) -> None:
        ls = build_default_learning_state("Mira")
        ls, skill = ensure_skill(ls, "Farming")
        updated, evts = add_experience_to_skill(skill, -50.0, source="bad", tick=1)
        self.assertEqual(updated.experience, 0.0)
        self.assertEqual(evts, [])

    def test_experience_accumulation_deterministic(self) -> None:
        ls = build_default_learning_state("Mira")
        base = get_base_practice_exp("Farming")
        self.assertEqual(base, SKILL_PRACTICE_BASE_EXP["Farming"])

        ls, evts = record_practice(ls, "Farming", tick=1, context="plant_crops", success=True, practice_count=1)
        farming_exp = ls.get_experience("Farming")
        self.assertAlmostEqual(farming_exp, base, places=4)

        ls2, evts2 = record_practice(ls, "Farming", tick=2, context="plant_crops", success=True, practice_count=1)
        self.assertAlmostEqual(ls2.get_experience("Farming"), base * 2, places=4)

    def test_cancelled_work_grants_no_experience(self) -> None:
        ls = build_default_learning_state("Mira")
        ls, evts = record_practice(ls, "Farming", tick=1, context="plant_crops", success=False)
        self.assertEqual(ls.get_experience("Farming"), 0.0)
        self.assertEqual(ls.get_level("Farming"), 0)
        ev_types = [getattr(e, "event_type", str(type(e).__name__)) for e in evts]
        self.assertIn("SkillPracticeStarted", ev_types)
        self.assertIn("SkillPracticeCompleted", ev_types)
        self.assertNotIn("ExperienceGained", ev_types)

    def test_level_progression_through_practice(self) -> None:
        ls = build_default_learning_state("Mira")
        tick = 0
        levels_seen = {0}
        for round_idx in range(60):
            tick += 1
            ls, _ = record_practice(ls, "Farming", tick=tick, context=f"round_{round_idx}", success=True, practice_count=2)
            lv = ls.get_level("Farming")
            levels_seen.add(lv)
            if lv >= 3:
                break
        self.assertGreaterEqual(ls.get_level("Farming"), 1)
        self.assertGreater(len(levels_seen), 1)
        self.assertGreater(ls.get_experience("Farming"), 0.0)

    def test_level_increased_event_emitted(self) -> None:
        ls = build_default_learning_state("Mira")
        ls, skill = ensure_skill(ls, "Farming")
        near_level_2 = LEVEL_EXP_TABLE[2] - 1.0
        updated, evts1 = add_experience_to_skill(skill, near_level_2, source="warmup", tick=1)
        before_types = [e.event_type for e in evts1 if hasattr(e, "event_type")]

        updated2, evts2 = add_experience_to_skill(updated, 10.0, source="push", tick=2)
        after_types = [e.event_type for e in evts2 if hasattr(e, "event_type")]
        self.assertIn("ExperienceGained", after_types)
        level_events = [e for e in evts2 if isinstance(e, LevelIncreased)]
        self.assertGreaterEqual(len(level_events), 1)
        self.assertGreater(level_events[0].level_after, level_events[0].level_before)

    def test_skill_mastered_event_on_max_level(self) -> None:
        ls = build_default_learning_state("Mira")
        ls, skill = ensure_skill(ls, "Cooking")
        master_exp = LEVEL_EXP_TABLE[MAX_LEVEL] + 50.0
        updated, evts = add_experience_to_skill(skill, master_exp, source="lifetime", tick=99)
        mastered_events = [e for e in evts if isinstance(e, SkillMastered)]
        self.assertGreaterEqual(len(mastered_events), 1)
        self.assertTrue(updated.is_mastered)

    # ============================================================
    # Practice experience
    # ============================================================

    def test_practice_base_exp_all_skills(self) -> None:
        for st in SKILL_TYPES:
            base = get_base_practice_exp(st)
            self.assertGreater(base, 0.0)
            ls = build_default_learning_state("T")
            ls, _ = record_practice(ls, st, tick=1, context="t", success=True)
            self.assertAlmostEqual(ls.get_experience(st), base, places=4)

    def test_skill_type_normalization_invalid(self) -> None:
        ls = build_default_learning_state("Mira")
        ls, evts = record_practice(ls, "NotASkill", tick=1, context="x", success=True)
        self.assertGreater(ls.get_experience("Farming"), 0.0)

    def test_practice_history_recorded(self) -> None:
        ls = build_default_learning_state("Mira")
        ls, _ = record_practice(ls, "Blacksmithing", tick=3, context="forge_iron", success=True)
        ls, _ = record_practice(ls, "Blacksmithing", tick=5, context="forge_tools", success=True)
        skill = ls.get_skill("Blacksmithing")
        self.assertGreaterEqual(len(skill.practice_history), 2)
        contexts = [p.context for p in skill.practice_history]
        self.assertIn("forge_iron", contexts)
        self.assertIn("forge_tools", contexts)
        ticks = sorted([p.tick for p in skill.practice_history])
        self.assertEqual(ticks[0], 3)

    def test_last_practiced_tick_updates(self) -> None:
        ls = build_default_learning_state("Mira")
        ls, _ = record_practice(ls, "Medicine", tick=7, context="heal", success=True)
        self.assertEqual(ls.get_skill("Medicine").last_practiced_tick, 7)
        ls, _ = record_practice(ls, "Medicine", tick=20, context="heal_again", success=True)
        self.assertEqual(ls.get_skill("Medicine").last_practiced_tick, 20)

    def test_teacher_history_recorded_in_practice(self) -> None:
        ls = build_default_learning_state("Pell")
        ls, _ = record_practice(
            ls, "Blacksmithing", tick=10, context="forge", success=True, teacher_id="Joren"
        )
        skill = ls.get_skill("Blacksmithing")
        self.assertGreaterEqual(len(skill.teacher_history), 1)
        tr = skill.teacher_history[0]
        self.assertEqual(tr.teacher_id, "Joren")
        self.assertEqual(tr.skill_type, "Blacksmithing")
        self.assertEqual(tr.first_tick, 10)
        self.assertEqual(tr.total_lessons, 1)

    # ============================================================
    # Observation learning
    # ============================================================

    def test_observation_learning_gains_small_exp(self) -> None:
        master = build_default_learning_state("Joren")
        master, _ = record_practice(master, "Blacksmithing", 1, "warmup", True, 10)
        master, _ = record_practice(master, "Blacksmithing", 2, "warmup2", True, 10)
        apprentice = build_default_learning_state("Pell")

        apprentice_after, evts = record_observation(
            apprentice, master, "Blacksmithing", tick=5, context="observing_forge", proximity=1
        )
        obs_events = [e for e in evts if isinstance(e, ObservationLearning)]
        self.assertGreaterEqual(len(obs_events), 1)
        self.assertEqual(obs_events[0].observer_id, "Pell")
        self.assertEqual(obs_events[0].practitioner_id, "Joren")

        direct = build_default_learning_state("X")
        direct, _ = record_practice(direct, "Blacksmithing", tick=5, context="forge", success=True)
        self.assertGreater(
            direct.get_experience("Blacksmithing"),
            apprentice_after.get_experience("Blacksmithing"),
            "observation must never exceed direct practice",
        )

    def test_observation_requires_skill_on_practitioner(self) -> None:
        master = LearningState(entity_id="Joren", skills={})
        apprentice = build_default_learning_state("Pell")
        apprentice_after, evts = record_observation(
            apprentice, master, "Blacksmithing", tick=5, context="obs", proximity=1
        )
        self.assertEqual(apprentice_after.get_experience("Blacksmithing"), 0.0)
        self.assertEqual(evts, [])

    def test_observation_proximity_effect(self) -> None:
        master = build_default_learning_state("Joren")
        master, _ = record_practice(master, "Farming", 1, "warm", True, 8)
        near = build_default_learning_state("Near")
        far = build_default_learning_state("Far")
        near, _ = record_observation(near, master, "Farming", tick=5, context="n", proximity=1)
        far, _ = record_observation(far, master, "Farming", tick=5, context="f", proximity=5)
        self.assertGreater(
            near.get_experience("Farming"),
            far.get_experience("Farming"),
            "closer observers should learn more",
        )

    def test_observation_never_exceeds_practice(self) -> None:
        master = build_default_learning_state("Joren")
        for t in range(1, 21):
            master, _ = record_practice(master, "Cooking", t, "warm", True, 1)
        obs = build_default_learning_state("O")
        for t in range(1, 21):
            obs, _ = record_observation(obs, master, "Cooking", tick=t, context="watch", proximity=1)
        direct = build_default_learning_state("D")
        for t in range(1, 21):
            direct, _ = record_practice(direct, "Cooking", tick=t, context="cook", success=True)
        self.assertGreater(
            direct.get_experience("Cooking"),
            obs.get_experience("Cooking"),
            "cumulative observation must remain below direct practice",
        )

    # ============================================================
    # Teaching experience
    # ============================================================

    def test_start_lesson_creates_models_and_events(self) -> None:
        teacher = build_default_learning_state("Joren")
        teacher, _ = record_practice(teacher, "Farming", 1, "warm", True, 10)
        student = build_default_learning_state("Pell")

        lesson, t_out, s_out, events = start_lesson(teacher, student, "Farming", tick=10)
        self.assertIsInstance(lesson, Lesson)
        self.assertEqual(lesson.teacher_id, "Joren")
        self.assertEqual(lesson.student_id, "Pell")
        self.assertEqual(lesson.status, "Started")
        self.assertEqual(lesson.started_tick, 10)

        ev_types = [e.event_type for e in events if hasattr(e, "event_type")]
        self.assertIn("LessonStarted", ev_types)
        self.assertIn("TeacherAssigned", ev_types)
        self.assertIn("Joren", s_out.teachers_learned_from)
        self.assertIn("Pell", t_out.students_taught)
        self.assertIn(lesson.lesson_id, t_out.lessons_as_teacher)
        self.assertIn(lesson.lesson_id, s_out.lessons_as_student)

    def test_complete_lesson_success_transfers_knowledge(self) -> None:
        teacher = build_default_learning_state("Joren")
        for t in range(1, 21):
            teacher, _ = record_practice(teacher, "Farming", t, "warm", True, 1)
        student = build_default_learning_state("Pell")

        lesson, t1, s1, ev_s = start_lesson(teacher, student, "Farming", tick=5)
        completed, t2, s2, ev_c = complete_lesson(lesson, t1, s1, tick=10, success=True, teacher_quality=1.0)

        self.assertEqual(completed.status, "Completed")
        self.assertGreater(s2.get_experience("Farming"), s1.get_experience("Farming"))
        self.assertGreater(t2.get_experience("Farming"), t1.get_experience("Farming"))

        ev_types_c = [e.event_type for e in ev_c if hasattr(e, "event_type")]
        self.assertIn("KnowledgeTransferred", ev_types_c)
        self.assertIn("LessonCompleted", ev_types_c)
        self.assertIn("ExperienceGained", ev_types_c)

    def test_failed_lesson_no_knowledge_transfer(self) -> None:
        teacher = build_default_learning_state("Joren")
        teacher, _ = record_practice(teacher, "Farming", 1, "w", True, 5)
        student = build_default_learning_state("Pell")

        lesson, t1, s1, _ = start_lesson(teacher, student, "Farming", tick=5)
        completed, t2, s2, ev_c = complete_lesson(lesson, t1, s1, tick=10, success=False)

        self.assertEqual(completed.status, "Failed")
        self.assertEqual(s2.get_experience("Farming"), 0.0)
        lc = [e for e in ev_c if isinstance(e, LessonCompleted)]
        self.assertEqual(len(lc), 1)
        self.assertFalse(lc[0].success)
        self.assertEqual(lc[0].experience_transferred, 0.0)

    def test_teacher_history_records_instruction(self) -> None:
        teacher = build_default_learning_state("Joren")
        teacher, _ = record_practice(teacher, "Medicine", 1, "w", True, 5)
        student = build_default_learning_state("Mira")
        lesson, t1, s1, _ = start_lesson(teacher, student, "Medicine", tick=3)
        _, t2, s2, _ = complete_lesson(lesson, t1, s1, tick=5, success=True)
        med_skill = s2.get_skill("Medicine")
        teachers = [t for t in med_skill.teacher_history if t.teacher_id == "Joren"]
        self.assertGreaterEqual(len(teachers), 1)
        self.assertGreaterEqual(teachers[0].total_lessons, 1)

    def test_teaching_requires_two_entities(self) -> None:
        ctx = self._make_ctx()
        prop = teach_skill_action(ctx, "Only", "Only", "Farming")
        self.assertEqual(prop, ())

    # ============================================================
    # Apprenticeship progression
    # ============================================================

    def test_start_apprenticeship(self) -> None:
        master = build_default_learning_state("Joren")
        master, _ = record_practice(master, "Blacksmithing", 1, "w", True, 15)
        apprentice = build_default_learning_state("Pell")

        app, a_state, m_state, events = start_apprenticeship(
            apprentice, master, "Blacksmithing", start_tick=10
        )
        self.assertIsInstance(app, Apprenticeship)
        self.assertEqual(app.status, "Active")
        self.assertEqual(app.apprentice_id, "Pell")
        self.assertEqual(app.master_id, "Joren")
        self.assertGreater(app.experience_target, 0.0)
        start_evts = [e for e in events if isinstance(e, ApprenticeshipStarted)]
        self.assertEqual(len(start_evts), 1)
        self.assertIn(app.apprenticeship_id, a_state.apprenticeships_as_apprentice)
        self.assertIn(app.apprenticeship_id, m_state.apprenticeships_as_master)

    def test_complete_apprenticeship_when_target_met(self) -> None:
        master = build_default_learning_state("Joren")
        apprentice = build_default_learning_state("Pell")
        app, a_state, m_state, _ = start_apprenticeship(
            apprentice, master, "Blacksmithing", start_tick=10, experience_target=200.0
        )
        a_state, _ = record_practice(a_state, "Blacksmithing", 11, "forge", True, 20)
        a_state, _ = record_practice(a_state, "Blacksmithing", 12, "forge2", True, 20)
        skill_exp = a_state.get_experience("Blacksmithing")
        app_earned = Apprenticeship(
            apprenticeship_id=app.apprenticeship_id,
            apprentice_id=app.apprentice_id,
            master_id=app.master_id,
            skill_type=app.skill_type,
            status=app.status,
            start_tick=app.start_tick,
            end_tick=0,
            experience_target=app.experience_target,
            experience_earned=skill_exp,
            lessons_completed=0,
            practices_completed=2,
        )
        updated_app, _, _, evts = complete_apprenticeship(app_earned, a_state, m_state, tick=50)
        comp_evts = [e for e in evts if isinstance(e, ApprenticeshipCompleted)]
        self.assertEqual(len(comp_evts), 1)
        self.assertEqual(comp_evts[0].final_level, a_state.get_level("Blacksmithing"))
        self.assertEqual(updated_app.status, "Completed")

    def test_force_complete_apprenticeship(self) -> None:
        master = build_default_learning_state("Joren")
        apprentice = build_default_learning_state("Pell")
        app, a_state, m_state, _ = start_apprenticeship(
            apprentice, master, "Carpentry", start_tick=5, experience_target=1e9
        )
        updated_app, _, _, evts = complete_apprenticeship(app, a_state, m_state, tick=20, force=True)
        self.assertEqual(updated_app.status, "Completed")
        comp_evts = [e for e in evts if isinstance(e, ApprenticeshipCompleted)]
        self.assertEqual(len(comp_evts), 1)

    def test_apprenticeship_models_serialize_roundtrip(self) -> None:
        aid = make_apprenticeship_id("A", "M", "Cooking")
        app = Apprenticeship(
            apprenticeship_id=aid,
            apprentice_id="A",
            master_id="M",
            skill_type="Cooking",
            status="Active",
            start_tick=10,
            end_tick=0,
            experience_target=500.0,
            experience_earned=120.0,
            lessons_completed=3,
            practices_completed=5,
        )
        d = app.to_dict()
        restored = Apprenticeship.from_dict(d)
        self.assertEqual(restored.apprenticeship_id, aid)
        self.assertEqual(restored.status, "Active")
        self.assertEqual(restored.progress_pct, app.progress_pct)
        self.assertTrue(restored.is_active)
        self.assertFalse(restored.is_completed)

    def test_lesson_models_serialize_roundtrip(self) -> None:
        lid = make_lesson_id("T", "S", "Medicine", 7)
        lesson = Lesson(
            lesson_id=lid,
            teacher_id="T",
            student_id="S",
            skill_type="Medicine",
            status="Completed",
            scheduled_tick=5,
            started_tick=7,
            completed_tick=9,
            experience_transferred=33.5,
            teacher_experience_before=100.0,
            student_experience_before=0.0,
        )
        d = lesson.to_dict()
        restored = Lesson.from_dict(d)
        self.assertEqual(restored.lesson_id, lid)
        self.assertTrue(restored.is_complete)
        self.assertFalse(restored.is_started)

    def test_lookup_apprentice_of(self) -> None:
        app1 = Apprenticeship(
            apprenticeship_id=make_apprenticeship_id("Pell", "Joren", "B"),
            apprentice_id="Pell", master_id="Joren", skill_type="Blacksmithing", status="Active",
            start_tick=1, experience_target=500.0,
        )
        app2 = Apprenticeship(
            apprenticeship_id=make_apprenticeship_id("Mira", "Joren", "F"),
            apprentice_id="Mira", master_id="Joren", skill_type="Farming", status="Active",
            start_tick=2, experience_target=300.0,
        )
        app3 = Apprenticeship(
            apprenticeship_id=make_apprenticeship_id("Lina", "Someone", "S"),
            apprentice_id="Lina", master_id="Someone", skill_type="Social", status="Active",
            start_tick=3, experience_target=100.0,
        )
        apps = {a.apprenticeship_id: a for a in (app1, app2, app3)}
        joren_apps = lookup_apprentice_of(apps, "Joren", "Active")
        ids = sorted(a.apprentice_id for a in joren_apps)
        self.assertEqual(ids, ["Mira", "Pell"])

    # ============================================================
    # Planner: skilled worker selection
    # ============================================================

    def test_find_skilled_workers_sorts_by_level_then_exp(self) -> None:
        mira = build_default_learning_state("Mira")
        joren = build_default_learning_state("Joren")
        lina = build_default_learning_state("Lina")

        mira, _ = record_practice(mira, "Farming", 1, "plant", True, 10)
        joren, _ = record_practice(joren, "Farming", 1, "plant", True, 30)
        lina, _ = record_practice(lina, "Farming", 1, "plant", True, 5)

        states = {
            "Mira": mira,
            "Joren": joren,
            "Lina": lina,
        }
        ranked = find_skilled_workers(states, "Farming", min_level=0, top_n=3)
        self.assertEqual(len(ranked), 3)
        self.assertEqual(ranked[0][0], "Joren")
        self.assertEqual(ranked[-1][0], "Lina")

    def test_find_skilled_workers_min_level_filter(self) -> None:
        mira = build_default_learning_state("Mira")
        joren = build_default_learning_state("Joren")
        for _ in range(3):
            mira, _ = record_practice(mira, "Blacksmithing", 1, "x", True, 20)
        states = {"Mira": mira, "Joren": joren}
        high = find_skilled_workers(states, "Blacksmithing", min_level=5, top_n=5)
        self.assertEqual(len(high), 0)
        any_lv = find_skilled_workers(states, "Blacksmithing", min_level=0, top_n=5)
        self.assertGreaterEqual(len(any_lv), 1)

    def test_find_skilled_workers_for_action_on_kernel(self) -> None:
        villager_ids = sorted(self.villager_entities.keys())
        first = villager_ids[0]
        second = villager_ids[1]
        first_str = str(first.value) if hasattr(first, "value") else str(first)
        second_str = str(second.value) if hasattr(second, "value") else str(second)

        ctx1 = self._make_ctx()
        p1 = practice_skill_action(ctx1, first, "Farming", context_label="plant_wheat", success=True, practice_count=15)
        if isinstance(p1, TransitionProposal):
            tc_skilled = self._create_tick_context("skilled_farm_commit")
            self.kernel.commit_state(tc_skilled, [p1])

        ctx2 = self._make_ctx()
        ranked = find_skilled_workers_for(ctx2, "Farming", min_level=0, top_n=10)
        self.assertIsInstance(ranked, list)
        self.assertGreaterEqual(len(ranked), 1)

    def test_lookup_skills_by_entity(self) -> None:
        states = {
            "Mira": build_default_learning_state("Mira"),
        }
        info = lookup_skills_by_entity(states, "Mira")
        self.assertEqual(len(info), len(SKILL_TYPES))
        for st in SKILL_TYPES:
            lv, exp = info[st]
            self.assertEqual(lv, 0)
            self.assertEqual(exp, 0.0)

    # ============================================================
    # Skill effects on simulation (efficiency/quality/defect)
    # ============================================================

    def test_skill_efficiency_increases_with_level(self) -> None:
        base = get_skill_efficiency_multiplier(0)
        for lv in range(1, MAX_LEVEL + 1):
            self.assertGreater(get_skill_efficiency_multiplier(lv), base)

    def test_skill_defect_rate_decreases_with_level(self) -> None:
        base = get_skill_defect_rate(0)
        for lv in range(1, MAX_LEVEL + 1):
            self.assertLessEqual(get_skill_defect_rate(lv), base)
        self.assertGreaterEqual(get_skill_defect_rate(MAX_LEVEL), 0.0)

    def test_skill_quality_increases_with_level(self) -> None:
        base = get_skill_quality_multiplier(0)
        for lv in range(1, MAX_LEVEL + 1):
            self.assertGreater(get_skill_quality_multiplier(lv), base)

    def test_farming_efficiency_higher_for_higher_skill(self) -> None:
        low = build_default_learning_state("Low")
        high = build_default_learning_state("High")
        high, _ = record_practice(high, "Farming", 1, "plant", True, 40)
        low_mult = get_skill_efficiency_multiplier(low.get_level("Farming"))
        high_mult = get_skill_efficiency_multiplier(high.get_level("Farming"))
        self.assertGreater(high_mult, low_mult)

    def test_medicine_better_recovery_outcomes_with_level(self) -> None:
        lv_0_quality = get_skill_quality_multiplier(0)
        lv_5_quality = get_skill_quality_multiplier(5)
        lv_max_defect = get_skill_defect_rate(MAX_LEVEL)
        self.assertGreater(lv_5_quality, lv_0_quality)
        self.assertLessEqual(lv_max_defect, get_skill_defect_rate(0))

    # ============================================================
    # Proposal generation and kernel authority
    # ============================================================

    def test_practice_skill_action_returns_proposal(self) -> None:
        villagers = sorted(self.villager_entities.keys())
        v = villagers[0]
        ctx = self._make_ctx()
        prop = practice_skill_action(ctx, v, "Farming", context_label="plant_crops", success=True)
        self.assertIsInstance(prop, TransitionProposal)
        self.assertEqual(type(prop.patch), MappingProxyType)
        md = dict(prop.metadata)
        self.assertEqual(md.get("domain"), "learning")
        self.assertEqual(md.get("action"), "practice_skill")
        self.assertIn("events", md)

    def test_observe_work_action_returns_proposal(self) -> None:
        villagers = sorted(self.villager_entities.keys())
        v1 = villagers[0]
        v2 = villagers[1]

        ctx1 = self._make_ctx()
        warm = practice_skill_action(ctx1, v1, "Blacksmithing", context_label="forge", success=True, practice_count=10)
        if isinstance(warm, TransitionProposal):
            tc_obs = self._create_tick_context("obs_warmup_commit")
            self.kernel.commit_state(tc_obs, [warm])

        ctx2 = self._make_ctx()
        prop = observe_work_action(ctx2, v2, v1, "Blacksmithing", context_label="observing", proximity=1)
        if prop != ():
            self.assertIsInstance(prop, TransitionProposal)
            md = dict(prop.metadata)
            self.assertEqual(md.get("action"), "observe_work")
            self.assertIn(md.get("observer_id"), {str(v2), str(v2.value) if hasattr(v2, "value") else str(v2)})

    def test_teach_skill_action_returns_proposal(self) -> None:
        villagers = sorted(self.villager_entities.keys())
        t = villagers[0]
        s = villagers[1]
        ctx1 = self._make_ctx()
        warm = practice_skill_action(ctx1, t, "Medicine", context_label="heal_warmup", success=True, practice_count=8)
        if isinstance(warm, TransitionProposal):
            tc_teach = self._create_tick_context("teach_warmup_commit")
            self.kernel.commit_state(tc_teach, [warm])

        ctx2 = self._make_ctx()
        prop = teach_skill_action(ctx2, t, s, "Medicine", success=True, teacher_quality=1.0)
        if prop != ():
            self.assertIsInstance(prop, TransitionProposal)
            md = dict(prop.metadata)
            self.assertEqual(md.get("action"), "teach_skill")
            self.assertIn("lesson_id", md)

    def test_advance_experience_action_returns_proposal(self) -> None:
        villagers = sorted(self.villager_entities.keys())
        v = villagers[0]
        ctx = self._make_ctx()
        prop = advance_experience_action(ctx, v, "Cooking", 25.0, source="production", context_label="cooked_bread")
        self.assertIsInstance(prop, TransitionProposal)
        md = dict(prop.metadata)
        self.assertEqual(md.get("delta"), 25.0)
        self.assertEqual(md.get("source"), "production")

    def test_proposal_never_mutates_current_state(self) -> None:
        villagers = sorted(self.villager_entities.keys())
        v = villagers[0]
        snap_before_keys = sorted(list(dict(self.kernel.current_state).keys()))

        ctx = self._make_ctx()
        prop = practice_skill_action(ctx, v, "Carpentry", context_label="build", success=True)
        self.assertIsInstance(prop, TransitionProposal)
        snap_after_keys = sorted(list(dict(self.kernel.current_state).keys()))
        self.assertEqual(snap_before_keys, snap_after_keys)

    def test_kernel_commit_applies_state(self) -> None:
        villagers = sorted(self.villager_entities.keys())
        v = villagers[0]
        v_str = str(v.value) if hasattr(v, "value") else str(v)
        ctx1 = self._make_ctx()
        p = practice_skill_action(ctx1, v, "Social", context_label="talk", success=True, practice_count=30)
        self.assertIsInstance(p, TransitionProposal)

        tc_soc = self._create_tick_context("social_practice_commit")
        res = self.kernel.commit_state(tc_soc, [p])
        self.assertIsNotNone(res)

        states_after = self.kernel.current_state.get("learning_states", {})
        matched = None
        matched_key = None
        for k in states_after.keys():
            if v_str in str(k) or str(k) == v_str:
                matched = states_after[k]
                matched_key = k
                break
        self.assertIsNotNone(matched, f"learning state for {v_str} not found in {list(states_after.keys())[:5]}")
        raw = matched.to_dict() if hasattr(matched, "to_dict") else (dict(matched) if isinstance(matched, MappingProxyType) else matched)
        ls = LearningState.from_dict(raw) if isinstance(raw, dict) else matched
        self.assertGreater(ls.get_experience("Social"), 0.0)

    def test_no_proposal_no_state_change(self) -> None:
        snap_keys = sorted(list(dict(self.kernel.current_state).keys()))
        ctx = self._make_ctx()
        empty = practice_skill_action(ctx, "", "Farming", context_label="invalid")
        self.assertEqual(empty, ())
        self.assertEqual(
            snap_keys, sorted(list(dict(self.kernel.current_state).keys()))
        )

    # ============================================================
    # Learning state persistence, summaries, delta
    # ============================================================

    def test_learning_survives_multiple_commits(self) -> None:
        villagers = sorted(self.villager_entities.keys())
        v = villagers[0]
        v_str = str(v.value) if hasattr(v, "value") else str(v)
        for i in range(5):
            ctx = self._make_ctx()
            p = practice_skill_action(ctx, v, "Crafting", context_label=f"craft_{i}", success=True, practice_count=3)
            if isinstance(p, TransitionProposal):
                tc_craft = self._create_tick_context(f"craft_{i}_commit")
                self.kernel.commit_state(tc_craft, [p])

        ctx_final = self._make_ctx()
        skill_info = get_entity_skills(ctx_final, v)
        self.assertIn("Crafting", skill_info)
        lv, exp = skill_info["Crafting"]
        self.assertGreater(exp, 0.0)
        self.assertGreaterEqual(lv, 0)

    def test_learning_summary_computable(self) -> None:
        states = {
            "Mira": build_default_learning_state("Mira"),
            "Joren": build_default_learning_state("Joren"),
        }
        states["Mira"], _ = record_practice(states["Mira"], "Farming", 1, "p", True, 10)
        summary = compute_learning_summary(states)
        self.assertEqual(summary["entities"], 2)
        self.assertEqual(summary["total_skills"], 2 * len(SKILL_TYPES))
        self.assertGreater(summary["total_levels"], 0)
        self.assertGreater(summary["total_experience"], 0.0)

    def test_summarize_delta_identifies_changes(self) -> None:
        before = build_default_learning_state("Mira")
        after, _ = record_practice(before, "Farming", 1, "p", True, 5)
        delta = summarize_learning_delta(before, after)
        self.assertIn("Farming", delta)
        lv_delta, exp_delta, exp_after = delta["Farming"]
        self.assertGreater(exp_delta, 0.0)
        self.assertGreaterEqual(lv_delta, 0)

    def test_ensure_learning_state_for_defaults(self) -> None:
        empty = {}
        ls = ensure_learning_state_for(empty, "NewEntity")
        self.assertEqual(ls.entity_id, "NewEntity")
        self.assertEqual(ls.skill_count, len(SKILL_TYPES))

    def test_get_learning_summary_action(self) -> None:
        ctx = self._make_ctx()
        summary = get_learning_summary(ctx)
        self.assertIsInstance(summary, dict)
        self.assertIn("entities", summary)
        self.assertIn("total_skills", summary)

    def test_get_learning_states_and_apprenticeships_and_lessons(self) -> None:
        ctx = self._make_ctx()
        states = get_learning_states(ctx)
        self.assertIsInstance(states, dict)
        self.assertGreaterEqual(len(states), 1)
        apps = get_apprenticeships(ctx)
        self.assertIsInstance(apps, dict)
        lessons = get_lessons(ctx)
        self.assertIsInstance(lessons, dict)

    # ============================================================
    # Conversation integration
    # ============================================================

    def test_teaching_conversation_generates_teaching_events(self) -> None:
        teacher = build_default_learning_state("Joren")
        teacher, _ = record_practice(teacher, "Farming", 1, "w", True, 10)
        student = build_default_learning_state("Pell")

        ls_map_before = {"Joren": teacher, "Pell": student}
        lesson, t1, s1, ev_s = start_lesson(teacher, student, "Farming", tick=5)
        completed, t2, s2, ev_c = complete_lesson(lesson, t1, s1, tick=7, success=True)

        lesson_started = [e for e in ev_s if isinstance(e, LessonStarted)]
        lesson_completed = [e for e in ev_c if isinstance(e, LessonCompleted)]
        knowledge = [e for e in ev_c if isinstance(e, KnowledgeTransferred)]
        self.assertGreaterEqual(len(lesson_started), 1)
        self.assertGreaterEqual(len(lesson_completed), 1)
        self.assertGreaterEqual(len(knowledge), 1)
        self.assertEqual(knowledge[0].from_entity_id, "Joren")
        self.assertEqual(knowledge[0].to_entity_id, "Pell")

    def test_finish_apprenticeship_action_via_kernel(self) -> None:
        villagers = sorted(self.villager_entities.keys())
        self.assertGreaterEqual(len(villagers), 2)
        master = villagers[0]
        apprentice = villagers[1]

        ctx1 = self._make_ctx()
        warm = practice_skill_action(ctx1, master, "Leadership", context_label="lead_warmup", success=True, practice_count=10)
        if isinstance(warm, TransitionProposal):
            tc_lead = self._create_tick_context("finish_app_warmup")
            self.kernel.commit_state(tc_lead, [warm])

        master_str = str(master.value) if hasattr(master, "value") else str(master)
        apprentice_str = str(apprentice.value) if hasattr(apprentice, "value") else str(apprentice)
        aid = make_apprenticeship_id(apprentice_str, master_str, "Leadership")

        ctx2 = self._make_ctx()
        ctx2.current_state = dict(self.kernel.current_state)
        ctx2.current_tick_number = int(self.kernel.current_tick_number) + 1
        finish_prop = finish_apprenticeship_action(ctx2, aid, force=True)
        if finish_prop != ():
            self.assertIsInstance(finish_prop, TransitionProposal)

    # ============================================================
    # Immutable events
    # ============================================================

    def test_all_learning_events_are_frozen(self) -> None:
        events = [
            SkillPracticeStarted(entity_id="M", skill_type="Farming", context="x", tick=1),
            SkillPracticeCompleted(entity_id="M", skill_type="Farming", context="x", success=True, tick=1),
            ExperienceGained(entity_id="M", skill_type="Farming", experience_before=0.0, experience_after=15.0, experience_delta=15.0, source="p", tick=1),
            LevelIncreased(entity_id="M", skill_type="Farming", level_before=0, level_after=1, experience_at_level=100.0, tick=1),
            LessonStarted(lesson_id="L1", teacher_id="T", student_id="S", skill_type="Farming", tick=1),
            LessonCompleted(lesson_id="L1", teacher_id="T", student_id="S", skill_type="Farming", success=True, experience_transferred=10.0, tick=2),
            TeacherAssigned(teacher_id="T", student_id="S", skill_type="Farming", start_tick=1, tick=1),
            ApprenticeshipStarted(apprenticeship_id="A1", apprentice_id="A", master_id="M", skill_type="B", experience_target=500.0, tick=1),
            ApprenticeshipCompleted(apprenticeship_id="A1", apprentice_id="A", master_id="M", skill_type="B", total_experience=500.0, final_level=3, tick=10),
            ObservationLearning(observer_id="O", practitioner_id="P", skill_type="F", context="obs", experience_gained=5.0, tick=1),
            SkillMastered(entity_id="M", skill_type="Farming", master_level=MAX_LEVEL, total_experience=9999.0, tick=100),
            KnowledgeTransferred(from_entity_id="T", to_entity_id="S", skill_type="Farming", experience_amount=25.0, context="l", tick=1),
        ]
        for e in events:
            d1 = e.to_dict()
            d2 = e.to_dict()
            self.assertEqual(d1, d2)
            event_type_attr = getattr(e, "event_type", None)
            if event_type_attr is not None:
                self.assertIsInstance(event_type_attr, str)
            self.assertIn("event_type", d1)
            try:
                e.tick = 999
                mutated = True
            except Exception:
                mutated = False
            self.assertFalse(mutated, f"{type(e).__name__} should be frozen and reject mutation")

    def test_events_to_dict_roundtrips_equality(self) -> None:
        eg = ExperienceGained(
            entity_id="Mira", skill_type="Cooking",
            experience_before=10.0, experience_after=25.0, experience_delta=15.0,
            source="practice", tick=7,
        )
        d = eg.to_dict()
        restored = ExperienceGained(**{k: v for k, v in d.items() if k != "event_type"})
        self.assertEqual(restored.entity_id, "Mira")
        self.assertEqual(restored.experience_delta, 15.0)

    # ============================================================
    # Replay determinism
    # ============================================================

    def test_record_practice_deterministic(self) -> None:
        def run(label: str) -> tuple[float, int, list[str]]:
            ls = build_default_learning_state(label)
            ev_types_all: list[str] = []
            for t in range(1, 11):
                ls, evs = record_practice(ls, "Cooking", tick=t, context=f"cook_{t}_{label}", success=True)
                ev_types_all.extend(getattr(e, "event_type", str(type(e).__name__)) for e in evs)
            return ls.get_experience("Cooking"), ls.get_level("Cooking"), ev_types_all

        exp1, lv1, ev1 = run("A")
        exp2, lv2, ev2 = run("A")
        self.assertEqual(exp1, exp2)
        self.assertEqual(lv1, lv2)
        self.assertEqual(ev1, ev2)

    def test_teaching_deterministic(self) -> None:
        def run(seed: str) -> tuple[float, float]:
            teacher = build_default_learning_state("T_" + seed)
            for t in range(1, 10):
                teacher, _ = record_practice(teacher, "Trading", tick=t, context="w", success=True, practice_count=2)
            student = build_default_learning_state("S_" + seed)
            lesson, t1, s1, _ = start_lesson(teacher, student, "Trading", tick=10)
            _, t2, s2, _ = complete_lesson(lesson, t1, s1, tick=12, success=True, teacher_quality=0.9)
            return t2.get_experience("Trading"), s2.get_experience("Trading")

        t1, s1 = run("X1")
        t2, s2 = run("X1")
        self.assertEqual(t1, t2)
        self.assertEqual(s1, s2)

    def test_observation_deterministic(self) -> None:
        def run() -> float:
            master = build_default_learning_state("M")
            for t in range(1, 10):
                master, _ = record_practice(master, "Hunting", tick=t, context="w", success=True)
            a = build_default_learning_state("A")
            for t in range(5, 10):
                a, _ = record_observation(a, master, "Hunting", tick=t, context="obs", proximity=1)
            return a.get_experience("Hunting")

        self.assertEqual(run(), run())

    def test_planner_replay_selects_same_worker(self) -> None:
        def build() -> list[tuple[str, int, float]]:
            mira = build_default_learning_state("Mira")
            joren = build_default_learning_state("Joren")
            lina = build_default_learning_state("Lina")
            for t in range(1, 10):
                mira, _ = record_practice(mira, "Trading", tick=t, context="trade", success=True, practice_count=2)
                joren, _ = record_practice(joren, "Trading", tick=t, context="trade", success=True, practice_count=1)
                lina, _ = record_practice(lina, "Trading", tick=t, context="trade", success=True, practice_count=3)
            return find_skilled_workers(
                {"Mira": mira, "Joren": joren, "Lina": lina}, "Trading", min_level=0, top_n=3
            )

        r1 = build()
        r2 = build()
        self.assertEqual([x[0] for x in r1], [x[0] for x in r2])

    # ============================================================
    # No direct world mutation
    # ============================================================

    def test_record_practice_preserves_original(self) -> None:
        before = build_default_learning_state("Mira")
        snap = before.to_dict()
        after, evts = record_practice(before, "Farming", tick=1, context="plant", success=True)
        self.assertEqual(before.to_dict(), snap)
        self.assertNotEqual(after.to_dict(), snap)

    def test_record_observation_preserves_originals(self) -> None:
        master = build_default_learning_state("Joren")
        master, _ = record_practice(master, "Blacksmithing", 1, "w", True, 5)
        apprentice = build_default_learning_state("Pell")
        master_snap = master.to_dict()
        app_snap = apprentice.to_dict()
        after, _ = record_observation(apprentice, master, "Blacksmithing", 5, "o", 1)
        self.assertEqual(master.to_dict(), master_snap)
        self.assertEqual(apprentice.to_dict(), app_snap)

    def test_complete_lesson_preserves_originals(self) -> None:
        teacher = build_default_learning_state("T")
        teacher, _ = record_practice(teacher, "Leadership", 1, "w", True, 5)
        student = build_default_learning_state("S")
        lesson, t1, s1, _ = start_lesson(teacher, student, "Leadership", tick=1)
        t1_snap = t1.to_dict()
        s1_snap = s1.to_dict()
        l_snap = lesson.to_dict()
        completed, t2, s2, _ = complete_lesson(lesson, t1, s1, tick=3, success=True)
        self.assertEqual(t1.to_dict(), t1_snap)
        self.assertEqual(s1.to_dict(), s1_snap)
        self.assertEqual(lesson.to_dict(), l_snap)

    # ============================================================
    # Apply / auto-progress integration
    # ============================================================

    def test_apply_on_empty_state_returns_empty(self) -> None:
        ctx = type("Ctx", (), {
            "current_state": {},
            "world_id": "w",
            "current_tick_number": 0,
            "tick_context": None,
            "committed_revision": None,
        })()
        self.assertEqual(apply(ctx), ())

    def test_apply_auto_progresses_active_apprenticeships(self) -> None:
        master = build_default_learning_state("M")
        apprentice = build_default_learning_state("A")
        app, a_new, m_new, _ = start_apprenticeship(
            apprentice, master, "Carpentry", start_tick=0, experience_target=100.0
        )
        for _ in range(3):
            a_new, _ = record_practice(a_new, "Carpentry", 1, "x", True, 20)
        skill_exp = a_new.get_experience("Carpentry")
        app_done = Apprenticeship(
            apprenticeship_id=app.apprenticeship_id,
            apprentice_id=app.apprentice_id,
            master_id=app.master_id,
            skill_type=app.skill_type,
            status="Active",
            start_tick=0,
            end_tick=0,
            experience_target=app.experience_target,
            experience_earned=skill_exp,
            lessons_completed=0,
            practices_completed=3,
        )
        state = {
            "learning_states": {
                "M": m_new.to_dict(),
                "A": a_new.to_dict(),
            },
            "learning_apprenticeships": {
                app_done.apprenticeship_id: app_done.to_dict(),
            },
            "learning_lessons": {},
        }
        ctx = type("Ctx", (), {
            "current_state": state,
            "world_id": "w",
            "current_tick_number": 5,
            "tick_context": None,
            "committed_revision": None,
        })()
        prop = apply(ctx)
        self.assertIsInstance(prop, TransitionProposal)
        md = dict(prop.metadata)
        self.assertTrue(md.get("auto_progress"))

    # ============================================================
    # Learning history (teachers/students/practice)
    # ============================================================

    def test_teacher_learning_and_students_taught_tracked(self) -> None:
        teacher = build_default_learning_state("Joren")
        teacher, _ = record_practice(teacher, "Medicine", 1, "w", True, 5)
        s1 = build_default_learning_state("Mira")
        s2 = build_default_learning_state("Lina")

        lesson1, t1, s1a, _ = start_lesson(teacher, s1, "Medicine", tick=5)
        _, t2, s1b, _ = complete_lesson(lesson1, t1, s1a, tick=7, success=True)

        lesson2, t3, s2a, _ = start_lesson(t2, s2, "Medicine", tick=8)
        _, t4, s2b, _ = complete_lesson(lesson2, t3, s2a, tick=10, success=True)

        self.assertIn("Mira", t4.students_taught)
        self.assertIn("Lina", t4.students_taught)
        self.assertIn("Joren", s1b.teachers_learned_from)
        self.assertIn("Joren", s2b.teachers_learned_from)

    def test_knowledge_shared_count_increments(self) -> None:
        teacher = build_default_learning_state("T")
        teacher, _ = record_practice(teacher, "Social", 1, "w", True, 3)
        student = build_default_learning_state("S")
        lesson, t1, s1, _ = start_lesson(teacher, student, "Social", tick=1)
        _, t2, _, _ = complete_lesson(lesson, t1, s1, tick=3, success=True)
        self.assertEqual(t2.knowledge_shared_count, 1)

    # ============================================================
    # Learning goals (planner observe-only)
    # ============================================================

    def test_generate_learning_goals_observe_only(self) -> None:
        result = generate_learning_goals(self.kernel)
        if result != ():
            self.assertIsInstance(result, TransitionProposal)
            md = dict(result.metadata)
            if "action" in md:
                self.assertEqual(md["action"], "generate_learning_goals")

    def test_skill_to_occupation_mapping(self) -> None:
        pairs = dict(SKILL_TO_OCCUPATION)
        for sk in SKILL_TYPES:
            self.assertIn(sk, pairs)


if __name__ == "__main__":
    unittest.main()
