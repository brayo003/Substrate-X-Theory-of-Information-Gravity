from __future__ import annotations

import copy
import unittest
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any

from sim_world import KernelConfig, WorldKernel
from sim_world.core.contracts import TickContext, TransitionProposal
from sim_world.core.ids import TickId
from sim_world.domains import register_all
from sim_world.domains.agriculture import initialize_valley_agriculture
from sim_world.domains.economy import initialize_valley_economy
from sim_world.domains.health import (
    DEATH_THRESHOLD,
    DEFAULT_BODY_TEMP,
    DEFAULT_FATIGUE,
    DEFAULT_HEALTH,
    DEFAULT_HYDRATION,
    DEFAULT_IMMUNITY,
    DEFAULT_INFECTION,
    DEFAULT_INJURY,
    DEFAULT_MOBILITY_PENALTY,
    DEFAULT_NUTRITION,
    DEFAULT_SICKNESS,
    DEFAULT_STRESS,
    DEATH_THRESHOLD as DT,
    HEALTH_EVENT_TYPES,
    HEALTH_MAX,
    HEALTH_MIN,
    ILLNESS_TYPES,
    INJURY_TYPES,
    RECOVERY_RATE_BASE,
    DeathOccurred,
    Dehydrated,
    FatigueIncreased,
    FatigueRecovered,
    HealthDeclined,
    HealthImproved,
    HealthState,
    HeatStressStarted,
    HypothermiaStarted,
    IllnessRecovered,
    IllnessStarted,
    InjuryOccurred,
    InjuryRecovered,
    Malnourished,
    RecoveryCompleted,
    RecoveryStarted,
    add_illness,
    add_injury,
    apply as health_apply,
    apply_food_eaten,
    apply_heavy_work,
    apply_light_work,
    apply_rest_recovery,
    apply_sleep_recovery,
    apply_water_drank,
    clamp,
    compute_overall_health_from_components,
    derive_body_temperature_from_weather,
    deterministic_hash,
    drink_water_action,
    eat_food_action,
    evaluate_villager_health_tick,
    generate_health_goals,
    get_health_state,
    get_health_summary,
    is_entity_alive,
    make_health_state_id,
    recover_action,
    remove_illness,
    remove_injury,
    rest_action,
    shelter_action,
    should_go_to_hospital_or_home,
    should_prioritize_rest,
    should_seek_shelter_for_health,
    sleep_action,
    treat_action,
    walk_wound_action,
    work_efficiency,
    work_efficiency_multiplier_for,
    work_while_sick_action,
)
from sim_world.domains.population import initialize_valley_population
from sim_world.domains.relationships import initialize_valley_relationships
from sim_world.domains.resources import initialize_valley_resources
from sim_world.domains.terrain import initialize_valley_terrain


class Loop11HealthTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = KernelConfig(
            world_name="valley_world_health",
            seed="health-seed-011",
            initial_state={"mode": "valley_health_simulation"},
        )
        self.kernel = WorldKernel(self.config)
        register_all(self.kernel.simulation_engine)
        self.terrain_entities = initialize_valley_terrain(self.kernel)
        self.villager_entities = initialize_valley_population(self.kernel)
        self.building_entities = initialize_valley_resources(self.kernel)
        self.crop_fields = initialize_valley_agriculture(self.kernel)
        self.economy_state = initialize_valley_economy(self.kernel)
        self.relationships_state = initialize_valley_relationships(self.kernel)

    def _create_tick_context(
        self,
        correlation_id: str = "test_health_correlation",
        tick_override: int | None = None,
    ) -> TickContext:
        tick_num = (
            int(tick_override)
            if tick_override is not None
            else int(self.kernel.current_tick_number)
        )
        tick_id = TickId.new(self.kernel.world_id, tick_num)
        rev = (
            self.kernel.current_revision.revision_id
            if self.kernel.current_revision is not None
            else None
        )
        return TickContext(
            world_id=self.kernel.world_id,
            tick_id=tick_id,
            state_revision=rev,
            parent_revision=rev,
            timestamp=datetime.now(timezone.utc),
            correlation_id=correlation_id,
        )

    def _make_ctx(self, tick_override: int | None = None) -> Any:
        tick_num = (
            int(tick_override)
            if tick_override is not None
            else int(self.kernel.current_tick_number)
        )
        tc = self._create_tick_context(tick_override=tick_num)
        return type("Ctx", (), {
            "world_state": dict(self.kernel.current_state),
            "current_state": dict(self.kernel.current_state),
            "world_id": self.kernel.world_id,
            "tick_number": tick_num,
            "current_tick_number": tick_num,
            "tick_context": tc,
            "committed_revision": (
                self.kernel.current_revision.revision_id
                if self.kernel.current_revision is not None
                else None
            ),
        })()

    def _first_human_entity_id(self) -> str:
        entities = dict(self.kernel.current_state.get("entities", {}))
        for eid, ed in sorted(entities.items()):
            if str(ed.get("type")) == "human":
                return str(eid)
        raise RuntimeError("No human entity found in kernel")

    # ================================================================
    # 1. MODELS / STATE INVARIANTS
    # ================================================================

    def test_illness_types_complete(self) -> None:
        expected = {
            "Cold",
            "Flu",
            "FoodPoisoning",
            "Exhaustion",
            "Dehydration",
            "Malnutrition",
            "Hypothermia",
            "HeatStress",
        }
        self.assertEqual(set(ILLNESS_TYPES), expected)

    def test_injury_types_complete(self) -> None:
        expected = {
            "MinorCut",
            "Sprain",
            "Fracture",
            "WorkStrain",
            "StormAccident",
            "FallingTree",
            "ConstructionFall",
        }
        self.assertEqual(set(INJURY_TYPES), expected)

    def test_health_event_types_count(self) -> None:
        self.assertGreaterEqual(len(HEALTH_EVENT_TYPES), 15)

    def test_health_state_clamping_ranges(self) -> None:
        bad = {
            "health_id": make_health_state_id("e_test_clamp"),
            "entity_id": "e_test_clamp",
            "overall_health": 5.0,
            "fatigue": -2.0,
            "nutrition": 3.0,
            "hydration": -1.0,
            "immunity": 9.0,
            "stress": 50.0,
            "sickness": -0.5,
            "injury": -1.0,
            "infection": 2.0,
            "body_temperature_c": 100.0,
            "mobility_penalty": 5.0,
            "alive": True,
        }
        hs = HealthState.from_dict(bad)
        self.assertLessEqual(hs.overall_health, HEALTH_MAX)
        self.assertGreaterEqual(hs.overall_health, HEALTH_MIN)
        self.assertLessEqual(hs.fatigue, HEALTH_MAX)
        self.assertGreaterEqual(hs.fatigue, 0.0)
        self.assertLessEqual(hs.nutrition, HEALTH_MAX)
        self.assertGreaterEqual(hs.nutrition, 0.0)
        self.assertLessEqual(hs.hydration, HEALTH_MAX)
        self.assertGreaterEqual(hs.hydration, 0.0)
        self.assertLessEqual(hs.immunity, HEALTH_MAX)
        self.assertGreaterEqual(hs.immunity, 0.0)
        self.assertLessEqual(hs.stress, HEALTH_MAX)
        self.assertGreaterEqual(hs.stress, 0.0)
        self.assertLessEqual(hs.sickness, HEALTH_MAX)
        self.assertGreaterEqual(hs.sickness, 0.0)
        self.assertLessEqual(hs.injury, HEALTH_MAX)
        self.assertGreaterEqual(hs.injury, 0.0)
        self.assertLessEqual(hs.infection, HEALTH_MAX)
        self.assertGreaterEqual(hs.infection, 0.0)
        self.assertLessEqual(hs.body_temperature_c, 44.0)
        self.assertGreaterEqual(hs.body_temperature_c, 30.0)
        self.assertLessEqual(hs.mobility_penalty, 1.0)
        self.assertGreaterEqual(hs.mobility_penalty, 0.0)

    def test_health_state_death_when_threshold(self) -> None:
        hs = HealthState(
            health_id=make_health_state_id("e_dying"),
            entity_id="e_dying",
            overall_health=0.0,
            alive=True,
        )
        self.assertFalse(hs.alive)

    def test_dead_entity_not_recovering(self) -> None:
        hs = HealthState(
            health_id=make_health_state_id("e_dead_recovery"),
            entity_id="e_dead_recovery",
            overall_health=0.0,
            alive=True,
            recovering=True,
        )
        self.assertFalse(hs.alive)
        self.assertFalse(hs.recovering)

    def test_health_state_roundtrip_dict(self) -> None:
        hs0 = HealthState.initial("e_roundtrip", birth_tick=10, seed="abc")
        d = hs0.to_dict()
        hs1 = HealthState.from_dict(d)
        attrs = (
            "health_id",
            "entity_id",
            "overall_health",
            "fatigue",
            "nutrition",
            "hydration",
            "immunity",
            "stress",
            "sickness",
            "injury",
            "infection",
            "body_temperature_c",
            "mobility_penalty",
            "alive",
            "recovering",
            "last_treatment_tick",
            "active_illnesses",
            "active_injuries",
            "last_updated_tick",
            "birth_tick",
        )
        for attr in attrs:
            self.assertEqual(getattr(hs0, attr), getattr(hs1, attr), f"attr {attr} mismatch")

    def test_initial_health_defaults(self) -> None:
        hs = HealthState.initial("e_init")
        self.assertAlmostEqual(hs.overall_health, DEFAULT_HEALTH, places=3)
        self.assertAlmostEqual(hs.fatigue, DEFAULT_FATIGUE, places=3)
        self.assertAlmostEqual(hs.nutrition, DEFAULT_NUTRITION, places=3)
        self.assertAlmostEqual(hs.hydration, DEFAULT_HYDRATION, places=3)
        self.assertAlmostEqual(hs.immunity, DEFAULT_IMMUNITY, places=3)
        self.assertAlmostEqual(hs.stress, DEFAULT_STRESS, places=3)
        self.assertAlmostEqual(hs.sickness, DEFAULT_SICKNESS, places=3)
        self.assertAlmostEqual(hs.injury, DEFAULT_INJURY, places=3)
        self.assertAlmostEqual(hs.infection, DEFAULT_INFECTION, places=3)
        self.assertAlmostEqual(hs.body_temperature_c, DEFAULT_BODY_TEMP, places=3)
        self.assertAlmostEqual(hs.mobility_penalty, DEFAULT_MOBILITY_PENALTY, places=3)
        self.assertTrue(hs.alive)
        self.assertFalse(hs.recovering)

    def test_deterministic_hash_stable(self) -> None:
        h1 = deterministic_hash("health:abc:123")
        h2 = deterministic_hash("health:abc:123")
        self.assertEqual(h1, h2)
        self.assertIsInstance(h1, int)
        self.assertGreaterEqual(h1, 0)
        self.assertLess(h1, 2**32)

    def test_make_health_state_id_deterministic(self) -> None:
        a = make_health_state_id("entity_A")
        b = make_health_state_id("entity_A")
        c = make_health_state_id("entity_B")
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_add_remove_illness_idempotent(self) -> None:
        base = ("Cold",)
        self.assertEqual(add_illness(base, "Cold"), base)
        self.assertIn("Flu", add_illness(base, "Flu"))
        self.assertNotIn("Cold", remove_illness(base, "Cold"))
        self.assertEqual(remove_illness(base, "NotThere"), base)

    def test_add_remove_injury_idempotent(self) -> None:
        base = ("Sprain",)
        self.assertEqual(add_injury(base, "Sprain"), base)
        self.assertIn("Fracture", add_injury(base, "Fracture"))
        self.assertNotIn("Sprain", remove_injury(base, "Sprain"))

    def test_clamp_function(self) -> None:
        self.assertEqual(clamp(1.5, 0.0, 1.0), 1.0)
        self.assertEqual(clamp(-0.5, 0.0, 1.0), 0.0)
        self.assertEqual(clamp(0.5, 0.0, 1.0), 0.5)

    # ================================================================
    # 2. WEATHER EFFECTS ON BODY TEMPERATURE
    # ================================================================

    def test_indoor_body_temp_regulates(self) -> None:
        cold_body = 34.0
        result = derive_body_temperature_from_weather(
            weather_temperature_c=0.0,
            is_outside=False,
            has_warm_clothing=False,
            current_body_temp=cold_body,
        )
        self.assertGreater(result, cold_body)

    def test_outdoor_freeze_cold_weather(self) -> None:
        t = derive_body_temperature_from_weather(
            weather_temperature_c=-20.0,
            is_outside=True,
            has_warm_clothing=False,
            current_body_temp=36.7,
            weather_state_short="clear",
        )
        self.assertLess(t, 36.5)

    def test_warm_clothing_mitigates_cold(self) -> None:
        no_clothing = derive_body_temperature_from_weather(
            weather_temperature_c=-15.0,
            is_outside=True,
            has_warm_clothing=False,
            current_body_temp=36.7,
        )
        with_clothing = derive_body_temperature_from_weather(
            weather_temperature_c=-15.0,
            is_outside=True,
            has_warm_clothing=True,
            current_body_temp=36.7,
        )
        self.assertGreater(with_clothing, no_clothing)

    def test_outdoor_heat_raises_temp(self) -> None:
        t = derive_body_temperature_from_weather(
            weather_temperature_c=50.0,
            is_outside=True,
            has_warm_clothing=False,
            current_body_temp=36.7,
        )
        self.assertGreater(t, 37.0)

    def test_rain_snow_worsens_warmth_loss(self) -> None:
        clear = derive_body_temperature_from_weather(
            weather_temperature_c=2.0,
            is_outside=True,
            has_warm_clothing=False,
            current_body_temp=36.0,
            weather_state_short="clear",
        )
        storm = derive_body_temperature_from_weather(
            weather_temperature_c=2.0,
            is_outside=True,
            has_warm_clothing=False,
            current_body_temp=36.0,
            weather_state_short="storm",
        )
        self.assertLess(storm, clear)

    # ================================================================
    # 3. FOOD / DRINK / SLEEP / WORK ACTIONS
    # ================================================================

    def test_apply_food_eaten_improves_nutrition(self) -> None:
        n, h, i = apply_food_eaten(0.3, 0.3, 0.4, 0.9, 0.9)
        self.assertGreater(n, 0.3)
        self.assertGreater(h, 0.3)
        self.assertGreater(i, 0.4)

    def test_food_quality_matters(self) -> None:
        bad, _, _ = apply_food_eaten(0.5, 0.5, 0.5, 0.2, 0.2)
        good, _, _ = apply_food_eaten(0.5, 0.5, 0.5, 0.95, 0.95)
        self.assertGreater(good, bad)

    def test_apply_water_drank_improves_hydration(self) -> None:
        self.assertGreater(apply_water_drank(0.2, 0.9), 0.2)

    def test_apply_sleep_recovery(self) -> None:
        f, s, bt = apply_sleep_recovery(0.9, 0.8, 35.5)
        self.assertLess(f, 0.9)
        self.assertLess(s, 0.8)
        self.assertGreater(bt, 35.5)

    def test_apply_heavy_work_increases_fatigue(self) -> None:
        f, n, h, _ = apply_heavy_work(0.1, 0.8, 0.8, 0.0)
        self.assertGreater(f, 0.1)
        self.assertLess(n, 0.8)
        self.assertLess(h, 0.8)

    def test_apply_light_work_less_fatigue_than_heavy(self) -> None:
        f_light, _, _ = apply_light_work(0.1, 0.8, 0.8)
        f_heavy, _, _, _ = apply_heavy_work(0.1, 0.8, 0.8, 0.0)
        self.assertLess(f_light, f_heavy)

    def test_apply_rest_recovery(self) -> None:
        f, s = apply_rest_recovery(0.6, 0.5)
        self.assertLess(f, 0.6)
        self.assertLess(s, 0.5)

    # ================================================================
    # 4. OVERALL HEALTH COMPUTATION
    # ================================================================

    def test_perfect_components_give_high_health(self) -> None:
        h = compute_overall_health_from_components(
            fatigue=0.0,
            nutrition=1.0,
            hydration=1.0,
            immunity=1.0,
            stress=0.0,
            sickness=0.0,
            injury=0.0,
            infection=0.0,
            body_temperature_c=36.7,
        )
        self.assertGreater(h, 0.85)

    def test_bad_components_give_low_health(self) -> None:
        h = compute_overall_health_from_components(
            fatigue=1.0,
            nutrition=0.0,
            hydration=0.0,
            immunity=0.0,
            stress=1.0,
            sickness=1.0,
            injury=1.0,
            infection=1.0,
            body_temperature_c=33.0,
        )
        self.assertLess(h, 0.4)

    def test_extreme_body_temp_penalizes_health(self) -> None:
        normal = compute_overall_health_from_components(
            0.1, 0.8, 0.8, 0.7, 0.2, 0.0, 0.0, 0.0, 36.7
        )
        cold = compute_overall_health_from_components(
            0.1, 0.8, 0.8, 0.7, 0.2, 0.0, 0.0, 0.0, 33.0
        )
        hot = compute_overall_health_from_components(
            0.1, 0.8, 0.8, 0.7, 0.2, 0.0, 0.0, 0.0, 41.0
        )
        self.assertLess(cold, normal)
        self.assertLess(hot, normal)

    # ================================================================
    # 5. NEEDS INTEGRATION VIA evaluate_villager_health_tick
    # ================================================================

    def _base_hs(self, eid: str = "e_test_base") -> HealthState:
        return HealthState.initial(eid)

    def test_unmet_hunger_need_lowers_nutrition(self) -> None:
        prev = self._base_hs("e_hunger")
        prev = HealthState.from_dict({**prev.to_dict(), "nutrition": 0.6})
        new, _ = evaluate_villager_health_tick(
            previous=prev,
            tick_number=1,
            needs={"hunger": 0.9},
        )
        self.assertLess(new.nutrition, 0.6)

    def test_unmet_thirst_need_lowers_hydration(self) -> None:
        prev = self._base_hs("e_thirst")
        prev = HealthState.from_dict({**prev.to_dict(), "hydration": 0.6})
        new, _ = evaluate_villager_health_tick(
            previous=prev,
            tick_number=1,
            needs={"thirst": 0.9},
        )
        self.assertLess(new.hydration, 0.6)

    def test_unmet_energy_need_increases_fatigue(self) -> None:
        prev = self._base_hs("e_energy")
        prev = HealthState.from_dict({**prev.to_dict(), "fatigue": 0.2})
        new, _ = evaluate_villager_health_tick(
            previous=prev,
            tick_number=1,
            needs={"energy": 0.0},
        )
        self.assertGreater(new.fatigue, 0.2)

    def test_low_warmth_need_lowers_body_temp(self) -> None:
        prev = self._base_hs("e_warmth")
        prev = HealthState.from_dict({**prev.to_dict(), "body_temperature_c": 36.5})
        new, _ = evaluate_villager_health_tick(
            previous=prev,
            tick_number=1,
            needs={"warmth": 0.1},
            weather_temperature_c=15.0,
        )
        self.assertLess(new.body_temperature_c, 36.5)

    def test_low_social_need_increases_stress(self) -> None:
        prev = self._base_hs("e_social")
        prev = HealthState.from_dict({**prev.to_dict(), "stress": 0.1})
        new, _ = evaluate_villager_health_tick(
            previous=prev,
            tick_number=1,
            needs={"social": 0.1},
        )
        self.assertGreater(new.stress, 0.1)

    # ================================================================
    # 6. ILLNESSES (deterministic emergence)
    # ================================================================

    def test_dehydration_illness_at_low_hydration(self) -> None:
        prev = HealthState(
            health_id=make_health_state_id("e_dehy"),
            entity_id="e_dehy",
            hydration=0.05,
            nutrition=0.8,
            immunity=0.8,
        )
        new, events = evaluate_villager_health_tick(previous=prev, tick_number=1)
        self.assertIn("Dehydration", new.active_illnesses)
        types = {type(e).__name__ for e in events}
        self.assertIn("Dehydrated", types)
        self.assertIn("IllnessStarted", types)

    def test_malnutrition_illness_at_low_nutrition(self) -> None:
        prev = HealthState(
            health_id=make_health_state_id("e_mal"),
            entity_id="e_mal",
            nutrition=0.05,
            hydration=0.8,
            immunity=0.8,
        )
        new, events = evaluate_villager_health_tick(previous=prev, tick_number=1)
        self.assertIn("Malnutrition", new.active_illnesses)
        types = {type(e).__name__ for e in events}
        self.assertIn("Malnourished", types)

    def test_hypothermia_at_low_body_temp(self) -> None:
        prev = HealthState(
            health_id=make_health_state_id("e_hypo"),
            entity_id="e_hypo",
            body_temperature_c=33.0,
        )
        new, events = evaluate_villager_health_tick(previous=prev, tick_number=1)
        self.assertIn("Hypothermia", new.active_illnesses)
        types = {type(e).__name__ for e in events}
        self.assertIn("HypothermiaStarted", types)

    def test_heat_stress_at_high_body_temp(self) -> None:
        prev = HealthState(
            health_id=make_health_state_id("e_heat"),
            entity_id="e_heat",
            body_temperature_c=39.5,
        )
        new, events = evaluate_villager_health_tick(previous=prev, tick_number=1)
        self.assertIn("HeatStress", new.active_illnesses)
        types = {type(e).__name__ for e in events}
        self.assertIn("HeatStressStarted", types)

    def test_exhaustion_illness_at_extreme_fatigue(self) -> None:
        prev = HealthState(
            health_id=make_health_state_id("e_exh"),
            entity_id="e_exh",
            fatigue=0.99,
        )
        new, events = evaluate_villager_health_tick(previous=prev, tick_number=1)
        self.assertIn("Exhaustion", new.active_illnesses)

    def test_food_poisoning_from_spoiled_food(self) -> None:
        prev = self._base_hs("e_fp")
        new, events = evaluate_villager_health_tick(
            previous=prev,
            tick_number=1,
            did_eat=True,
            food_spoiled=True,
            food_quality=0.1,
        )
        self.assertIn("FoodPoisoning", new.active_illnesses)
        types = {type(e).__name__ for e in events}
        self.assertIn("IllnessStarted", types)

    def test_dehydration_recovers_when_hydration_restored(self) -> None:
        start = HealthState(
            health_id=make_health_state_id("e_dehy_rec"),
            entity_id="e_dehy_rec",
            hydration=0.9,
            nutrition=0.9,
            immunity=0.8,
            active_illnesses=("Dehydration",),
            sickness=0.2,
        )
        new, events = evaluate_villager_health_tick(previous=start, tick_number=1)
        types = {type(e).__name__ for e in events}
        self.assertIn("IllnessRecovered", types)
        recovered_illnesses = [e.illness_type for e in events if isinstance(e, IllnessRecovered)]
        self.assertIn("Dehydration", recovered_illnesses)

    def test_cold_emerges_in_cold_weather_low_immunity(self) -> None:
        found = False
        for t in range(100):
            prev = HealthState(
                health_id=make_health_state_id(f"e_cold_{t}"),
                entity_id=f"e_cold_{t}",
                immunity=0.1,
                hydration=0.9,
                nutrition=0.9,
            )
            new, _ = evaluate_villager_health_tick(
                previous=prev,
                tick_number=t,
                weather_state_short="cold",
                seed_tag=f"cold_test_{t}",
            )
            if "Cold" in new.active_illnesses:
                found = True
                break
        self.assertTrue(found, "Cold illness should emerge eventually with low immunity in cold weather")

    # ================================================================
    # 7. INJURIES
    # ================================================================

    def test_work_strain_from_heavy_work(self) -> None:
        found = False
        for t in range(200):
            prev = HealthState(
                health_id=make_health_state_id(f"e_ws_{t}"),
                entity_id=f"e_ws_{t}",
                nutrition=0.9,
                hydration=0.9,
            )
            new, events = evaluate_villager_health_tick(
                previous=prev,
                tick_number=t,
                did_heavy_work=True,
                seed_tag=f"workstrain_{t}",
            )
            if "WorkStrain" in new.active_injuries:
                found = True
                injury_events = [e for e in events if isinstance(e, InjuryOccurred)]
                self.assertTrue(any("WorkStrain" in e.injury_type for e in injury_events))
                break
        self.assertTrue(found, "WorkStrain should occur with enough heavy work ticks")

    def test_construction_fall_possible(self) -> None:
        found = False
        for t in range(300):
            prev = HealthState(
                health_id=make_health_state_id(f"e_cf_{t}"),
                entity_id=f"e_cf_{t}",
                nutrition=0.9,
                hydration=0.9,
            )
            new, _ = evaluate_villager_health_tick(
                previous=prev,
                tick_number=t,
                did_construction=True,
                seed_tag=f"consfall_{t}",
            )
            if "ConstructionFall" in new.active_injuries or "Sprain" in new.active_injuries:
                found = True
                break
        self.assertTrue(found, "Construction injuries should occur eventually")

    def test_storm_accident_outside(self) -> None:
        found = False
        for t in range(200):
            prev = HealthState(
                health_id=make_health_state_id(f"e_sa_{t}"),
                entity_id=f"e_sa_{t}",
                nutrition=0.9,
                hydration=0.9,
            )
            new, _ = evaluate_villager_health_tick(
                previous=prev,
                tick_number=t,
                was_outside_storm=True,
                seed_tag=f"stormacc_{t}",
            )
            if "StormAccident" in new.active_injuries:
                found = True
                break
        self.assertTrue(found, "Storm accidents should occur outside during storms")

    # ================================================================
    # 8. RECOVERY
    # ================================================================

    def test_good_conditions_start_recovery(self) -> None:
        prev = HealthState(
            health_id=make_health_state_id("e_rec"),
            entity_id="e_rec",
            nutrition=0.9,
            hydration=0.9,
            fatigue=0.2,
            sickness=0.15,
            body_temperature_c=36.5,
        )
        new, events = evaluate_villager_health_tick(
            previous=prev,
            tick_number=1,
            has_shelter=True,
        )
        self.assertTrue(new.recovering)
        types = {type(e).__name__ for e in events}
        self.assertIn("RecoveryStarted", types)

    def test_treatment_boosts_recovery_and_immunity(self) -> None:
        prev = HealthState(
            health_id=make_health_state_id("e_treat"),
            entity_id="e_treat",
            immunity=0.3,
            sickness=0.6,
            nutrition=0.9,
            hydration=0.9,
            body_temperature_c=36.7,
        )
        new, events = evaluate_villager_health_tick(
            previous=prev,
            tick_number=5,
            had_treatment=True,
            has_shelter=True,
        )
        self.assertGreater(new.immunity, 0.3)
        self.assertLess(new.sickness, 0.6)
        self.assertEqual(new.last_treatment_tick, 5)
        self.assertTrue(new.recovering)

    def test_recovery_completes_when_clean(self) -> None:
        started = HealthState(
            health_id=make_health_state_id("e_rec_c"),
            entity_id="e_rec_c",
            nutrition=0.95,
            hydration=0.95,
            immunity=0.9,
            sickness=0.02,
            injury=0.02,
            body_temperature_c=36.7,
            recovering=True,
        )
        new, events = evaluate_villager_health_tick(
            previous=started,
            tick_number=10,
            has_shelter=True,
        )
        self.assertFalse(new.recovering)
        types = {type(e).__name__ for e in events}
        self.assertIn("RecoveryCompleted", types)

    # ================================================================
    # 9. DEATH
    # ================================================================

    def test_death_from_starvation(self) -> None:
        prev = HealthState(
            health_id=make_health_state_id("e_starve"),
            entity_id="e_starve",
            nutrition=0.0,
            hydration=0.0,
            immunity=0.0,
            fatigue=1.0,
            stress=1.0,
            sickness=1.0,
            injury=0.95,
            infection=0.95,
            body_temperature_c=30.0,
            overall_health=0.8,
        )
        for t in range(1, 600):
            prev, events = evaluate_villager_health_tick(
                previous=prev,
                tick_number=t,
                needs={"hunger": 1.0, "thirst": 1.0},
                weather_temperature_c=-25.0,
                weather_state_short="storm",
                is_outside=True,
                has_shelter=False,
                has_warm_clothing=False,
                did_heavy_work=True,
                was_outside_storm=True,
                did_construction=True,
                seed_tag=f"die_starve_{t}",
            )
            if not prev.alive:
                types = {type(e).__name__ for e in events}
                self.assertIn("DeathOccurred", types)
                deaths = [e for e in events if isinstance(e, DeathOccurred)]
                self.assertTrue(len(deaths) > 0)
                break
        self.assertFalse(prev.alive, "Should die of combined failures eventually")

    def test_dead_entity_stays_dead(self) -> None:
        dead = HealthState(
            health_id=make_health_state_id("e_dead"),
            entity_id="e_dead",
            overall_health=0.0,
            alive=False,
        )
        new, events = evaluate_villager_health_tick(
            previous=dead,
            tick_number=100,
            did_eat=True,
            did_sleep=True,
            has_shelter=True,
            had_treatment=True,
        )
        self.assertFalse(new.alive)
        self.assertEqual(len(events), 0)

    def test_death_lowers_alive_flag_only(self) -> None:
        """Dead entities cannot revive via good fortune."""
        prev = HealthState(
            health_id=make_health_state_id("e_norevive"),
            entity_id="e_norevive",
            overall_health=0.0,
            alive=False,
        )
        for _ in range(10):
            prev, _ = evaluate_villager_health_tick(
                previous=prev,
                tick_number=5,
                has_shelter=True,
                had_treatment=True,
                did_eat=True,
                did_drink=True,
                did_sleep=True,
                food_quality=1.0,
                water_quality=1.0,
            )
        self.assertFalse(prev.alive)

    # ================================================================
    # 10. FATIGUE / HEALTH EVENTS
    # ================================================================

    def test_fatigue_increased_event_fires(self) -> None:
        prev = self._base_hs("e_fi")
        new, events = evaluate_villager_health_tick(
            previous=prev,
            tick_number=1,
            did_heavy_work=True,
        )
        types = {type(e).__name__ for e in events}
        self.assertIn("FatigueIncreased", types)

    def test_fatigue_recovered_event_fires(self) -> None:
        prev = HealthState(
            health_id=make_health_state_id("e_fr"),
            entity_id="e_fr",
            fatigue=0.9,
        )
        new, events = evaluate_villager_health_tick(
            previous=prev,
            tick_number=1,
            did_sleep=True,
        )
        types = {type(e).__name__ for e in events}
        self.assertIn("FatigueRecovered", types)

    def test_health_improved_declined_events(self) -> None:
        prev_bad = HealthState(
            health_id=make_health_state_id("e_hdec"),
            entity_id="e_hdec",
            overall_health=0.5,
            nutrition=0.1,
            hydration=0.1,
            fatigue=0.9,
            immunity=0.3,
            stress=0.9,
            sickness=0.1,
            injury=0.1,
            infection=0.1,
            body_temperature_c=36.7,
        )
        _, ev1 = evaluate_villager_health_tick(
            previous=prev_bad,
            tick_number=1,
            needs={"hunger": 1.0, "thirst": 1.0, "energy": 0.0},
        )
        types1 = {type(e).__name__ for e in ev1}
        self.assertIn("HealthDeclined", types1)

        prev_good = HealthState(
            health_id=make_health_state_id("e_himp"),
            entity_id="e_himp",
            overall_health=0.3,
            nutrition=0.9,
            hydration=0.9,
            fatigue=0.05,
            immunity=0.9,
            stress=0.05,
            sickness=0.5,
            injury=0.0,
            infection=0.0,
            body_temperature_c=36.7,
        )
        _, ev2 = evaluate_villager_health_tick(
            previous=prev_good,
            tick_number=2,
            has_shelter=True,
            did_eat=True,
            did_sleep=True,
            had_treatment=True,
            food_quality=1.0,
            water_quality=1.0,
        )
        types2 = {type(e).__name__ for e in ev2}
        self.assertIn("HealthImproved", types2)

    # ================================================================
    # 11. PLANNER INTEGRATION (HEALTH GOALS)
    # ================================================================

    def test_generate_health_goals_returns_list(self) -> None:
        ctx = self._make_ctx(tick_override=1)
        goals = generate_health_goals(ctx)
        self.assertIsInstance(goals, list)

    def test_dehydration_triggers_drink_goal(self) -> None:
        eid = self._first_human_entity_id()
        ctx = self._make_ctx(tick_override=5)
        from sim_world.domains.health.health_domain import _read_health_state
        hs = _read_health_state(ctx.world_state, eid)
        thirsty = HealthState.from_dict({**hs.to_dict(), "hydration": 0.05, "alive": True})
        ctx.world_state.setdefault("health_states", {})[eid] = thirsty.to_dict()
        ctx.current_state.setdefault("health_states", {})[eid] = thirsty.to_dict()
        goals = generate_health_goals(ctx)
        kinds = [g["kind"] for g in goals if g.get("entity_id") == eid]
        self.assertIn("drink_water", kinds)

    def test_exhaustion_triggers_sleep_goal(self) -> None:
        eid = self._first_human_entity_id()
        ctx = self._make_ctx(tick_override=6)
        from sim_world.domains.health.health_domain import _read_health_state
        hs = _read_health_state(ctx.world_state, eid)
        tired = HealthState.from_dict({**hs.to_dict(), "fatigue": 0.95, "alive": True})
        ctx.world_state.setdefault("health_states", {})[eid] = tired.to_dict()
        ctx.current_state.setdefault("health_states", {})[eid] = tired.to_dict()
        goals = generate_health_goals(ctx)
        kinds = [g["kind"] for g in goals if g.get("entity_id") == eid]
        self.assertIn("sleep", kinds)

    def test_hypothermia_triggers_shelter_goal(self) -> None:
        eid = self._first_human_entity_id()
        ctx = self._make_ctx(tick_override=7)
        from sim_world.domains.health.health_domain import _read_health_state
        hs = _read_health_state(ctx.world_state, eid)
        cold = HealthState.from_dict({
            **hs.to_dict(),
            "body_temperature_c": 33.5,
            "immunity": 0.3,
            "alive": True,
        })
        ctx.world_state.setdefault("health_states", {})[eid] = cold.to_dict()
        ctx.current_state.setdefault("health_states", {})[eid] = cold.to_dict()
        goals = generate_health_goals(ctx)
        kinds = [g["kind"] for g in goals if g.get("entity_id") == eid]
        self.assertIn("shelter", kinds)

    def test_sickness_triggers_recover_goal(self) -> None:
        eid = self._first_human_entity_id()
        ctx = self._make_ctx(tick_override=8)
        from sim_world.domains.health.health_domain import _read_health_state
        hs = _read_health_state(ctx.world_state, eid)
        sick = HealthState.from_dict({
            **hs.to_dict(),
            "active_illnesses": ("Flu",),
            "sickness": 0.5,
            "alive": True,
        })
        ctx.world_state.setdefault("health_states", {})[eid] = sick.to_dict()
        ctx.current_state.setdefault("health_states", {})[eid] = sick.to_dict()
        goals = generate_health_goals(ctx)
        kinds = [g["kind"] for g in goals if g.get("entity_id") == eid]
        self.assertIn("recover", kinds)

    def test_should_prioritize_rest_dead_false(self) -> None:
        dead = HealthState(health_id=make_health_state_id("x"), entity_id="x", overall_health=0.0, alive=False)
        self.assertFalse(should_prioritize_rest(dead))
        healthy = HealthState.initial("y")
        self.assertFalse(should_prioritize_rest(healthy))
        sick = HealthState.from_dict({**healthy.to_dict(), "sickness": 0.6})
        self.assertTrue(should_prioritize_rest(sick))

    def test_should_seek_shelter_for_health_dead_false(self) -> None:
        dead = HealthState(health_id=make_health_state_id("x"), entity_id="x", overall_health=0.0, alive=False)
        self.assertFalse(should_seek_shelter_for_health(dead))
        healthy = HealthState.initial("y")
        self.assertFalse(should_seek_shelter_for_health(healthy))
        cold = HealthState.from_dict({**healthy.to_dict(), "body_temperature_c": 34.0})
        self.assertTrue(should_seek_shelter_for_health(cold))

    def test_should_go_to_hospital_or_home(self) -> None:
        dead = HealthState(health_id=make_health_state_id("x"), entity_id="x", overall_health=0.0, alive=False)
        self.assertFalse(should_go_to_hospital_or_home(dead))
        healthy = HealthState.initial("y")
        self.assertFalse(should_go_to_hospital_or_home(healthy))
        injured = HealthState.from_dict({**healthy.to_dict(), "injury": 0.6})
        self.assertTrue(should_go_to_hospital_or_home(injured))

    def test_work_efficiency_multiplier_for(self) -> None:
        dead = HealthState(health_id=make_health_state_id("x"), entity_id="x", overall_health=0.0, alive=False)
        self.assertEqual(work_efficiency_multiplier_for(dead), 0.0)
        healthy = HealthState.initial("y")
        wem = work_efficiency_multiplier_for(healthy)
        self.assertGreater(wem, 0.6)
        self.assertLessEqual(wem, 1.2)
        tired = HealthState.from_dict({**healthy.to_dict(), "fatigue": 0.99})
        self.assertLess(work_efficiency_multiplier_for(tired), wem)

    # ================================================================
    # 12. SIMULATION PROPOSAL (apply)
    # ================================================================

    def test_apply_returns_transition_proposal(self) -> None:
        ctx = self._make_ctx(tick_override=1)
        prop = health_apply(ctx)
        self.assertIsInstance(prop, TransitionProposal)
        self.assertIn("health_states", prop.patch)
        self.assertEqual(prop.subject, "domain.health")
        self.assertEqual(prop.metadata.get("domain"), "health")

    def test_apply_patch_contains_entity_health_components(self) -> None:
        ctx = self._make_ctx(tick_override=3)
        prop = health_apply(ctx)
        entities_patch = dict(prop.patch.get("entities", {}))
        for eid, ep in entities_patch.items():
            ed = dict(self.kernel.current_state.get("entities", {}).get(eid, {}))
            if str(ed.get("type")) != "human":
                continue
            ep_dict = dict(ep) if hasattr(ep, "items") else {}
            components = dict(ep_dict.get("components", {}))
            self.assertIn("HealthComponent", components)
            hc = dict(components["HealthComponent"])
            for k in ("health_state", "alive", "recovering", "active_illnesses",
                      "active_injuries", "overall_health", "fatigue", "nutrition",
                      "hydration", "stress", "immunity", "sickness", "injury",
                      "infection", "body_temperature_c", "mobility_penalty"):
                self.assertIn(k, hc, f"HealthComponent missing key: {k}")

    def test_apply_metadata_contains_entities_evaluated(self) -> None:
        ctx = self._make_ctx(tick_override=5)
        prop = health_apply(ctx)
        meta = dict(prop.metadata)
        self.assertIn("entities_evaluated", meta)
        self.assertIn("improved_count", meta)
        self.assertIn("declined_count", meta)
        self.assertIn("fatigued_entities", meta)
        self.assertIn("events", meta)
        self.assertIn("entities_dead_this_tick", meta)

    def test_apply_never_mutates_world_state_directly(self) -> None:
        ctx = self._make_ctx(tick_override=5)

        def snap(state: Any) -> dict[str, Any]:
            out: dict[str, Any] = {}
            hs = state.get("health_states", {})
            hs = dict(hs) if hasattr(hs, "items") else {}
            for k, v in hs.items():
                if isinstance(v, MappingProxyType):
                    out[k] = dict(v)
                else:
                    out[k] = v
            return {"health_states": out}

        orig = snap(dict(ctx.world_state))
        _ = health_apply(ctx)
        post = snap(dict(ctx.world_state))
        self.assertEqual(orig, post)

    # ================================================================
    # 13. ACTION PROPOSALS
    # ================================================================

    def test_drink_water_action_returns_proposal(self) -> None:
        ctx = self._make_ctx(tick_override=10)
        eid = self._first_human_entity_id()
        prop = drink_water_action(ctx, eid, water_quality=0.9)
        self.assertIsInstance(prop, TransitionProposal)
        self.assertEqual(prop.metadata.get("action"), "drink_water")

    def test_eat_food_action_flags(self) -> None:
        ctx = self._make_ctx(tick_override=11)
        eid = self._first_human_entity_id()
        prop = eat_food_action(ctx, eid, food_quality=0.9, food_spoiled=False)
        self.assertIsInstance(prop, TransitionProposal)
        self.assertTrue(prop.metadata.get("did_eat"))

    def test_sleep_rest_shelter_recover_treat_actions(self) -> None:
        ctx = self._make_ctx(tick_override=12)
        eid = self._first_human_entity_id()
        for fn, name, key in [
            (sleep_action, "sleep", "did_sleep"),
            (rest_action, "rest", "did_rest"),
            (shelter_action, "shelter", "has_shelter"),
            (recover_action, "recover", "did_rest"),
        ]:
            prop = fn(ctx, eid)
            with self.subTest(action=name):
                self.assertIsInstance(prop, TransitionProposal)
                self.assertEqual(prop.metadata.get("action"), name)
                self.assertTrue(prop.metadata.get(key))

    def test_treat_action_records_tick(self) -> None:
        ctx = self._make_ctx(tick_override=15)
        eid = self._first_human_entity_id()
        prop = treat_action(ctx, eid, doctor_id="e_doctor")
        self.assertIsInstance(prop, TransitionProposal)
        self.assertTrue(prop.metadata.get("had_treatment"))
        self.assertEqual(prop.metadata.get("doctor_id"), "e_doctor")

    def test_walk_wound_and_work_sick_actions(self) -> None:
        ctx = self._make_ctx(tick_override=18)
        eid = self._first_human_entity_id()
        prop1 = walk_wound_action(ctx, eid)
        self.assertIsInstance(prop1, TransitionProposal)
        self.assertTrue(prop1.metadata.get("mobility_penalty_active"))
        prop2 = work_while_sick_action(ctx, eid)
        self.assertIsInstance(prop2, TransitionProposal)
        self.assertTrue(prop2.metadata.get("did_light_work"))

    # ================================================================
    # 14. KERNEL QUERIES (get_health_summary etc)
    # ================================================================

    def test_get_health_state_and_summary(self) -> None:
        ctx = self._make_ctx(tick_override=20)
        eid = self._first_human_entity_id()
        hs = get_health_state(ctx, eid)
        self.assertIsInstance(hs, HealthState)
        summ = get_health_summary(ctx, eid)
        self.assertIsInstance(summ, dict)
        for k in ("entity_id", "overall_health", "alive", "recovering",
                  "fatigue", "nutrition", "hydration", "immunity", "stress",
                  "sickness", "injury", "infection", "body_temperature_c",
                  "mobility_penalty", "active_illnesses", "active_injuries",
                  "should_rest", "should_seek_shelter", "should_treat",
                  "work_efficiency"):
            self.assertIn(k, summ)

    def test_is_entity_alive(self) -> None:
        ctx = self._make_ctx(tick_override=21)
        eid = self._first_human_entity_id()
        self.assertTrue(is_entity_alive(ctx, eid))

    def test_work_efficiency_query(self) -> None:
        ctx = self._make_ctx(tick_override=22)
        eid = self._first_human_entity_id()
        we = work_efficiency(ctx, eid)
        self.assertIsInstance(we, float)
        self.assertGreaterEqual(we, 0.0)
        self.assertLessEqual(we, 1.2)

    # ================================================================
    # 15. IMMUTABLE EVENTS
    # ================================================================

    def test_events_are_frozen(self) -> None:
        events_samples = [
            HealthImproved(tick_number=1, entity_id="e1", delta_health=0.05),
            HealthDeclined(tick_number=2, entity_id="e2", delta_health=0.04),
            FatigueIncreased(tick_number=3, entity_id="e3", delta_fatigue=0.1),
            FatigueRecovered(tick_number=4, entity_id="e4", delta_fatigue=0.2),
            IllnessStarted(tick_number=5, entity_id="e5", illness_type="Cold"),
            IllnessRecovered(tick_number=6, entity_id="e6", illness_type="Cold"),
            InjuryOccurred(tick_number=7, entity_id="e7", injury_type="Sprain"),
            InjuryRecovered(tick_number=8, entity_id="e8", injury_type="Sprain"),
            Dehydrated(tick_number=9, entity_id="e9", hydration_level=0.1),
            Malnourished(tick_number=10, entity_id="e10", nutrition_level=0.1),
            HypothermiaStarted(tick_number=11, entity_id="e11", body_temperature_c=33.0),
            HeatStressStarted(tick_number=12, entity_id="e12", body_temperature_c=39.5),
            DeathOccurred(tick_number=13, entity_id="e13", cause="starvation"),
            RecoveryStarted(tick_number=14, entity_id="e14", reason="good_conditions"),
            RecoveryCompleted(tick_number=15, entity_id="e15", reason="restored"),
        ]
        for ev in events_samples:
            with self.subTest(event=type(ev).__name__):
                raised = False
                try:
                    setattr(ev, "tick_number", 9_999_999)
                except (FrozenInstanceError, AttributeError):
                    raised = True
                self.assertTrue(raised, f"{type(ev).__name__} should be frozen")

    def test_events_to_dict_contains_event_type(self) -> None:
        ev_list = [
            (HealthImproved(tick_number=1, entity_id="e", delta_health=0.01), "HealthImproved"),
            (IllnessStarted(tick_number=2, entity_id="e", illness_type="Flu"), "IllnessStarted"),
            (InjuryOccurred(tick_number=3, entity_id="e", injury_type="Fracture"), "InjuryOccurred"),
            (DeathOccurred(tick_number=4, entity_id="e", cause="infection_sickness"), "DeathOccurred"),
        ]
        for ev, expected_name in ev_list:
            with self.subTest(ev=expected_name):
                self.assertEqual(ev.to_dict()["event_type"], expected_name)

    # ================================================================
    # 16. REPLAY DETERMINISM
    # ================================================================

    def test_evaluate_villager_health_tick_deterministic(self) -> None:
        base = HealthState.initial("e_det", birth_tick=0)
        params = dict(
            tick_number=5,
            needs={"hunger": 0.3, "thirst": 0.2, "energy": 0.7, "comfort": 0.6, "warmth": 0.8, "social": 0.5},
            weather_temperature_c=18.0,
            weather_state_short="clear",
            is_outside=False,
            has_shelter=True,
            has_warm_clothing=False,
            did_sleep=False,
            did_rest=True,
            did_eat=True,
            did_drink=True,
            did_heavy_work=False,
            did_light_work=True,
            did_construction=False,
            was_outside_storm=False,
            food_quality=0.85,
            water_quality=0.85,
            food_spoiled=False,
            had_treatment=False,
            seed_tag="farmer:Alice",
        )

        new_a, events_a = evaluate_villager_health_tick(previous=base, **params)
        new_b, events_b = evaluate_villager_health_tick(previous=base, **params)
        for attr in ("overall_health", "fatigue", "nutrition", "hydration", "immunity",
                     "stress", "sickness", "injury", "infection", "body_temperature_c",
                     "mobility_penalty", "alive", "recovering", "active_illnesses",
                     "active_injuries"):
            self.assertEqual(getattr(new_a, attr), getattr(new_b, attr), f"attr {attr} not deterministic")
        self.assertEqual(len(events_a), len(events_b))
        for ea, eb in zip(events_a, events_b):
            self.assertEqual(ea.to_dict(), eb.to_dict())

    def test_multiple_runs_health_trace_identical(self) -> None:
        def run_trace(num_ticks: int) -> list[tuple[float, float, tuple[str, ...], tuple[str, ...]]]:
            cur = HealthState.initial("e_trace", birth_tick=0)
            trace: list[tuple[float, float, tuple[str, ...], tuple[str, ...]]] = []
            for t in range(num_ticks):
                cur, _ = evaluate_villager_health_tick(
                    previous=cur,
                    tick_number=t,
                    needs={"hunger": 0.5 + (t % 5) * 0.05, "thirst": 0.4, "energy": 0.6, "comfort": 0.7, "warmth": 0.7, "social": 0.6},
                    weather_temperature_c=10.0 + (t % 20),
                    weather_state_short=("clear", "cloudy", "cold", "storm")[t % 4],
                    is_outside=(t % 3 == 0),
                    has_shelter=(t % 3 != 0),
                    did_sleep=(t % 8 == 0),
                    did_rest=(t % 4 == 2),
                    did_eat=(t % 2 == 0),
                    did_drink=(t % 2 == 1 or t % 2 == 0),
                    did_heavy_work=(t % 6 == 1),
                    did_light_work=(t % 3 == 2),
                    did_construction=(t % 25 == 7),
                    was_outside_storm=((t % 3 == 0) and (t % 4 == 3)),
                    seed_tag="blacksmith:Bob",
                )
                trace.append((round(cur.overall_health, 6), round(cur.fatigue, 6),
                              tuple(cur.active_illnesses), tuple(cur.active_injuries)))
            return trace

        t1 = run_trace(120)
        t2 = run_trace(120)
        t3 = run_trace(120)
        self.assertEqual(t1, t2)
        self.assertEqual(t2, t3)

    def test_apply_proposal_deterministic(self) -> None:
        ctx_a = self._make_ctx(tick_override=3)
        ctx_b = self._make_ctx(tick_override=3)
        prop_a = health_apply(ctx_a)
        prop_b = health_apply(ctx_b)
        self.assertEqual(dict(prop_a.metadata).get("entities_evaluated"),
                         dict(prop_b.metadata).get("entities_evaluated"))

    # ================================================================
    # 17. NO DIRECT WORLD MUTATION (KERNEL AUTHORITY)
    # ================================================================

    def test_proposal_must_be_committed_to_affect_state(self) -> None:
        ctx = self._make_ctx(tick_override=int(self.kernel.current_tick_number))

        def snap_health() -> dict[str, Any]:
            raw = self.kernel.current_state.get("health_states", {})
            rd = dict(raw) if hasattr(raw, "items") else {}
            return rd

        pre = snap_health()
        _ = health_apply(ctx)
        post_no_commit = snap_health()
        self.assertEqual(pre, post_no_commit, "State must not change until kernel commits proposal")

    def test_registered_domain_in_engine(self) -> None:
        domains = getattr(self.kernel.simulation_engine, "_domains", None)
        if domains is None:
            return
        self.assertIn("health", domains)

    def test_register_all_includes_health(self) -> None:
        from sim_world import register_all as r_all
        engine2 = WorldKernel(KernelConfig(world_name="h2", seed="hs2", initial_state={})).simulation_engine
        r_all(engine2)
        domains = getattr(engine2, "_domains", None)
        if domains is None:
            return
        self.assertIn("health", domains)


if __name__ == "__main__":
    unittest.main()
