from __future__ import annotations

import copy
from dataclasses import FrozenInstanceError
from typing import Any, Mapping

import pytest

from sim_world.domains.society import (
    SOCIETY_METRIC_MIN,
    SOCIETY_METRIC_MAX,
    DEFAULT_PROSPERITY,
    DEFAULT_STABILITY,
    DEFAULT_MORALE,
    EMERGENCY_THRESHOLD,
    FOOD_CRISIS_RESERVE_PER_PERSON,
    WOOD_RESERVE_MIN_PER_HOUSEHOLD,
    EMERGENCY_TYPES,
    PROJECT_TYPES,
    CELEBRATION_TYPES,
    LEADERSHIP_ROLES,
    SOCIETY_EVENT_TYPES,
    VillageState,
    Household,
    CommunalProject,
    ActiveCelebration,
    ActiveEmergency,
    Leadership,
    LaborAllocation,
    clamp,
    deterministic_hash,
    make_village_id,
    make_household_id,
    make_project_id,
    make_celebration_id,
    make_emergency_id,
    VillageMeetingHeld,
    LeaderAssigned,
    HarvestFestivalStarted,
    HarvestFestivalEnded,
    EmergencyDeclared,
    EmergencyResolved,
    VillageProspered,
    VillageDeclined,
    FoodCrisisStarted,
    FoodCrisisResolved,
    PublicProjectStarted,
    PublicProjectCompleted,
    MoraleChanged,
    ProsperityChanged,
    StabilityChanged,
    PopulationChanged,
    CelebrationStarted,
    CelebrationEnded,
    evaluate_village_tick,
    evaluate_emergencies,
    evaluate_communal_projects,
    evaluate_celebrations,
    evaluate_leadership,
    compute_prosperity_components,
    compute_stability_components,
    compute_morale_components,
    derive_resource_shortage,
    derive_emergency_level,
    derive_population_from_entities,
    derive_workforce_from_entities,
    derive_society_goals,
    should_hold_meeting_for,
    labor_priority_for,
    apply,
    generate_society_goals,
    hold_meeting_action,
    assign_work_action,
    deliver_supplies_action,
    repair_structure_action,
    organize_harvest_action,
    celebrate_action,
    respond_emergency_action,
    inspect_storage_action,
    support_neighbor_action,
    get_village_state,
    get_village_summary,
    society_active_projects,
    society_active_emergencies,
)

from sim_world.domains import register_all


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _village_initial(world_id="w_loop12", name="Greenfield"):
    return VillageState.initial(world_id=world_id, village_name=name, founded_tick=0)


def _human_entities(n, *, health=0.8, trust=0.6, rel=0.5, hunger=0.7, thirst=0.75, conflict=0.05, sickness=0.05, stress=0.1, energy=0.8, skill=0.5, occupations=None):
    ents = []
    occs = list(occupations or ())
    for i in range(n):
        occ = occs[i % len(occs)] if occs else "Farmer"
        ents.append({
            "entity_id": f"h{i:03d}",
            "name": f"Person{i}",
            "is_human": True,
            "alive": True,
            "occupation": occ,
            "overall_health": health,
            "trust": trust,
            "relationship_quality": rel,
            "hunger": hunger,
            "thirst": thirst,
            "conflict": conflict,
            "sickness": sickness,
            "stress": stress,
            "energy": energy,
            "skill_level": skill,
        })
    return ents


# ---------------------------------------------------------------------------
# 1. Village Initialization & Models
# ---------------------------------------------------------------------------

class TestModelsAndInitialization:
    def test_defaults_match_spec(self):
        assert DEFAULT_PROSPERITY == pytest.approx(0.6)
        assert DEFAULT_STABILITY == pytest.approx(0.7)
        assert DEFAULT_MORALE == pytest.approx(0.65)
        assert EMERGENCY_THRESHOLD == pytest.approx(0.5)

    def test_emergency_types_required(self):
        required = {"FoodCrisis", "Flood", "Fire", "DiseaseOutbreak", "ResourceShortage", "WorkforceShortage"}
        assert required <= set(EMERGENCY_TYPES)

    def test_project_types_required(self):
        required = {"Harvest", "RoadRepair", "BridgeRepair", "StorageOrganization", "FireResponse", "ConstructionSupport"}
        assert required <= set(PROJECT_TYPES)

    def test_society_event_types_required(self):
        required = {
            "VillageMeetingHeld", "LeaderAssigned", "HarvestFestivalStarted", "HarvestFestivalEnded",
            "EmergencyDeclared", "EmergencyResolved", "VillageProspered", "VillageDeclined",
            "FoodCrisisStarted", "FoodCrisisResolved", "PublicProjectStarted", "PublicProjectCompleted",
            "MoraleChanged", "ProsperityChanged", "StabilityChanged", "PopulationChanged",
        }
        assert required <= set(SOCIETY_EVENT_TYPES), set(SOCIETY_EVENT_TYPES) & required

    def test_leadership_roles_nonempty(self):
        assert len(LEADERSHIP_ROLES) >= 4

    def test_clamp_idempotent(self):
        assert clamp(1.5) == 1.0
        assert clamp(-0.1) == 0.0
        assert clamp(0.5) == 0.5
        assert clamp(0.5, lo=0.2, hi=0.3) == 0.3

    def test_deterministic_hash_stable(self):
        h1 = deterministic_hash("abc:1")
        h2 = deterministic_hash("abc:1")
        assert h1 == h2
        assert deterministic_hash("abc:1") != deterministic_hash("abc:2")

    def test_village_ids_deterministic(self):
        a = make_village_id("w1", "Willow")
        b = make_village_id("w1", "Willow")
        c = make_village_id("w2", "Willow")
        assert a == b
        assert a != c

    def test_initial_village_state_fields(self):
        vs = _village_initial()
        assert vs.village_name == "Greenfield"
        assert vs.population == 0
        assert vs.workforce_size == 0
        assert vs.prosperity == pytest.approx(DEFAULT_PROSPERITY)
        assert vs.stability == pytest.approx(DEFAULT_STABILITY)
        assert vs.morale == pytest.approx(DEFAULT_MORALE)
        assert vs.emergency_level == pytest.approx(0.0)
        assert vs.active_projects == tuple()
        assert vs.active_celebrations == tuple()
        assert vs.active_emergencies == tuple()

    def test_village_state_roundtrip(self):
        vs = _village_initial()
        d = vs.to_dict()
        d["population"] = 8
        d["food_reserve"] = 250.0
        d["active_projects"] = ["p1"]
        vs2 = VillageState.from_dict(d)
        assert vs2.population == 8
        assert vs2.food_reserve == pytest.approx(250.0)
        assert vs2.active_projects == ("p1",)
        # Clamping enforced by __post_init__
        bad = vs.to_dict()
        bad["prosperity"] = 10.0
        bad["morale"] = -3.0
        vs3 = VillageState.from_dict(bad)
        assert vs3.prosperity == pytest.approx(1.0)
        assert vs3.morale == pytest.approx(0.0)

    def test_household_model(self):
        vid = make_village_id("w", "V")
        hid = make_household_id(vid, "Smith")
        h = Household(household_id=hid, name="Smith Household", village_id=vid, members=("h000", "h001"), head_of_household="h000", founded_tick=5, food_store=22.0, wood_store=40.0)
        d = h.to_dict()
        assert d["members"] == ["h000", "h001"]
        h2 = Household.from_dict(d)
        assert h2.household_id == hid
        assert h2.food_store == pytest.approx(22.0)

    def test_communal_project_active_to_completed_roundtrip(self):
        vid = make_village_id("w", "V")
        pid = make_project_id(vid, "Harvest", 3)
        p = CommunalProject(project_id=pid, project_type="Harvest", village_id=vid, name="Communal Harvest", assigned_workers=("h0","h1","h2"), required_workers=3, required_ticks=5, start_tick=3, progress=1.0, completed_tick=10, active=False)
        d = p.to_dict()
        p2 = CommunalProject.from_dict(d)
        assert p2.progress == pytest.approx(1.0)
        assert p2.active is False
        assert p2.completed_tick == 10

    def test_active_emergency_resolved(self):
        vid = make_village_id("w", "V")
        eid = make_emergency_id(vid, "FoodCrisis")
        em = ActiveEmergency(emergency_id=eid, emergency_type="FoodCrisis", village_id=vid, severity=0.7, declared_tick=3, resolved=True, resolved_tick=20)
        d = em.to_dict()
        em2 = ActiveEmergency.from_dict(d)
        assert em2.resolved is True
        assert em2.resolved_tick == 20

    def test_leadership_initial_effectiveness_clamped(self):
        vid = make_village_id("w", "V")
        l = Leadership(village_id=vid, leader_entity_id="e1", leadership_effectiveness=3.0)
        assert 0.0 <= l.leadership_effectiveness <= 1.0


# ---------------------------------------------------------------------------
# 2. Population / Workforce / Needs -> aggregates
# ---------------------------------------------------------------------------

class TestAggregates:
    def test_population_counts_alive_only(self):
        ents = _human_entities(6)
        ents[0]["alive"] = False
        ents[2]["alive"] = False
        alive, dead = derive_population_from_entities(ents)
        assert alive == 4
        assert dead == 2

    def test_workforce_and_occupations(self):
        ents = _human_entities(6, occupations=("Farmer", "Woodcutter", "Baker"))
        wf, occ = derive_workforce_from_entities(ents)
        assert wf == 6
        occ_dict = dict(occ)
        assert occ_dict.get("Farmer") == 2
        assert occ_dict.get("Woodcutter") == 2
        assert occ_dict.get("Baker") == 2


# ---------------------------------------------------------------------------
# 3. Prosperity / Stability / Morale computation
# ---------------------------------------------------------------------------

class TestMetricsComputation:
    def test_prosperity_high_when_healthy_and_rich(self):
        p, factors = compute_prosperity_components(
            population=6,
            food_reserve=400.0,
            wood_reserve=300.0,
            avg_health=0.9,
            avg_relationship=0.8,
            production_value=80,
            harvest_value=200,
            leadership_effectiveness=0.9,
            festival_days_count=20,
            completed_projects_count=6,
            learning_skill_avg=0.75,
            stability=0.85,
            morale=0.8,
        )
        assert p >= 0.55
        assert "healthy_population" in factors or "good_harvest" in factors or "strong_production" in factors

    def test_prosperity_zero_when_everything_fails(self):
        p, factors = compute_prosperity_components(
            population=10,
            food_reserve=0.0,
            wood_reserve=0.0,
            avg_health=0.05,
            avg_relationship=0.05,
            production_value=0,
            harvest_value=0,
            leadership_effectiveness=0.1,
            emergency_level=0.95,
            stability=0.1,
            morale=0.05,
        )
        assert p <= 0.2

    def test_prosperity_in_range(self):
        for _ in range(20):
            p, _ = compute_prosperity_components(
                population=5, food_reserve=50, wood_reserve=30, avg_health=0.5, avg_relationship=0.4,
                production_value=10, harvest_value=20, stability=0.5, morale=0.5,
            )
            assert SOCIETY_METRIC_MIN <= p <= SOCIETY_METRIC_MAX

    def test_stability_low_when_conflict_and_shortages(self):
        s, causes = compute_stability_components(
            avg_trust=0.2, avg_conflict=0.8, resource_shortage_severity=0.85, recent_deaths=4, active_emergencies_count=3, population=8,
        )
        assert s <= 0.35
        assert "high_conflict" in causes

    def test_stability_high_when_peaceful_and_recovering(self):
        s, causes = compute_stability_components(
            avg_trust=0.9, avg_relationship=0.8, avg_conflict=0.0, resource_shortage_severity=0.1, leadership_effectiveness=0.95,
            resolved_emergencies_count=4, festival_days_count=12, completed_projects_count=6, population=8,
        )
        assert s >= 0.6
        assert any(c in causes for c in ("successful_recovery", "festival_cohesion", "effective_leadership"))

    def test_morale_rises_on_harvest_and_festival(self):
        m, causes = compute_morale_components(
            recent_harvest_success=0.95, festival_days_count=15, shared_achievement_value=0.8,
            leadership_effectiveness=0.85, avg_relationship=0.75, prosperity=0.82, stability=0.8, population=6,
        )
        assert m >= 0.55
        assert any(c in causes for c in ("good_harvest", "celebration", "shared_achievement"))

    def test_morale_crashes_under_starvation_and_deaths(self):
        m, causes = compute_morale_components(
            recent_deaths_count=3, avg_conflict=0.8, avg_hunger_pressure=0.95, avg_illness_pressure=0.8,
            emergency_level=0.95, prosperity=0.1, stability=0.2, population=6,
        )
        assert m <= 0.25
        assert any(c in causes for c in ("grief", "hunger_pressure", "illness_strain"))


# ---------------------------------------------------------------------------
# 4. Emergencies deterministic detection
# ---------------------------------------------------------------------------

class TestEmergencies:
    def test_food_crisis_start_and_resolve(self):
        vid = make_village_id("w", "V")
        _, new_map, events = evaluate_emergencies(
            village_id=vid, tick_number=10, previous_active={},
            resource_shortage_severity=0.7, avg_health=0.7, food_reserve=2.0, population=20,
        )
        fc = [e for e in events if isinstance(e, FoodCrisisStarted)]
        assert len(fc) >= 1
        fc_eid = [e for e in events if isinstance(e, EmergencyDeclared) and e.emergency_type == "FoodCrisis"]
        assert len(fc_eid) >= 1
        # Resolve
        _, _, events2 = evaluate_emergencies(
            village_id=vid, tick_number=30, previous_active=new_map,
            resource_shortage_severity=0.0, avg_health=0.8, food_reserve=500.0, population=20,
        )
        assert any(isinstance(e, FoodCrisisResolved) for e in events2)
        assert any(isinstance(e, EmergencyResolved) and e.emergency_type == "FoodCrisis" for e in events2)

    def test_disease_outbreak_emerges_when_health_low(self):
        vid = make_village_id("w", "V")
        _, _, events = evaluate_emergencies(
            village_id=vid, tick_number=10, previous_active={},
            resource_shortage_severity=0.0, avg_health=0.35, food_reserve=500.0, population=6,
        )
        types = {e.emergency_type for e in events if isinstance(e, EmergencyDeclared)}
        assert "DiseaseOutbreak" in types

    def test_flood_from_heavy_rain(self):
        vid = make_village_id("w", "V")
        weather = {"rainfall": 40.0, "weather_type": "storm", "severity": 0.8}
        _, _, events = evaluate_emergencies(
            village_id=vid, tick_number=10, previous_active={},
            resource_shortage_severity=0.0, avg_health=0.8, food_reserve=500.0, population=6, weather_state=weather,
        )
        types = {e.emergency_type for e in events if isinstance(e, EmergencyDeclared)}
        assert "Flood" in types

    def test_workforce_shortage_emerges(self):
        vid = make_village_id("w", "V")
        _, _, events = evaluate_emergencies(
            village_id=vid, tick_number=10, previous_active={},
            resource_shortage_severity=0.0, avg_health=0.8, food_reserve=500.0, population=10, workforce=2,
        )
        types = {e.emergency_type for e in events if isinstance(e, EmergencyDeclared)}
        assert "WorkforceShortage" in types

    def test_civil_unrest_from_conflict_and_low_trust(self):
        vid = make_village_id("w", "V")
        _, _, events = evaluate_emergencies(
            village_id=vid, tick_number=10, previous_active={},
            resource_shortage_severity=0.0, avg_health=0.8, food_reserve=500.0, population=6,
            conflict_severity=0.85, avg_trust=0.2,
        )
        types = {e.emergency_type for e in events if isinstance(e, EmergencyDeclared)}
        assert "CivilUnrest" in types

    def test_emergency_level_in_range(self):
        em = derive_emergency_level(
            resource_shortage_severity=0.9, active_emergencies_count=4, avg_health=0.3, weather_severity=0.8, workforce_shortage=0.5, conflict_severity=0.4,
        )
        assert 0.0 <= em <= 1.0
        em2 = derive_emergency_level(resource_shortage_severity=0.0, active_emergencies_count=0, avg_health=0.9)
        assert em2 <= 0.5


# ---------------------------------------------------------------------------
# 5. Leadership
# ---------------------------------------------------------------------------

class TestLeadership:
    def test_leader_assigned_when_absent(self):
        vs = _village_initial()
        prev = Leadership(village_id=vs.village_id)
        new_l, events = evaluate_leadership(
            village_id=vs.village_id, tick_number=5, previous_leadership=prev, population=6,
            prosperity=0.6, stability=0.6, morale=0.6, emergency_level=0.0,
            available_leader_ids=("h0", "h1", "h2", "h3"), leader_entity_seniority={"h0": 20, "h1": 15},
        )
        assert new_l.leader_entity_id == "h0"
        assert any(isinstance(e, LeaderAssigned) and e.leader_entity_id == "h0" for e in events)

    def test_meeting_held_on_schedule(self):
        vs = _village_initial()
        prev = Leadership(village_id=vs.village_id, leader_entity_id="h0", last_meeting_tick=0, meeting_count=0, leadership_effectiveness=0.6)
        new_l, events = evaluate_leadership(
            village_id=vs.village_id, tick_number=31, previous_leadership=prev, population=6,
            prosperity=0.6, stability=0.6, morale=0.6, emergency_level=0.0, meeting_frequency_ticks=30,
        )
        assert new_l.meeting_count == 1
        assert new_l.last_meeting_tick == 31
        assert any(isinstance(e, VillageMeetingHeld) for e in events)

    def test_meeting_held_due_to_emergency(self):
        vs = _village_initial()
        prev = Leadership(village_id=vs.village_id, leader_entity_id="h0", last_meeting_tick=29, meeting_count=0, leadership_effectiveness=0.6)
        new_l, events = evaluate_leadership(
            village_id=vs.village_id, tick_number=30, previous_leadership=prev, population=6,
            prosperity=0.6, stability=0.6, morale=0.6, emergency_level=0.9, meeting_frequency_ticks=30,
        )
        assert any(isinstance(e, VillageMeetingHeld) for e in events)

    def test_should_hold_meeting_for(self):
        vs = _village_initial()
        l_ok = Leadership(village_id=vs.village_id, leader_entity_id="h0", last_meeting_tick=0)
        assert should_hold_meeting_for(village=vs, leadership=l_ok, tick_number=31, meeting_frequency_ticks=30)


# ---------------------------------------------------------------------------
# 6. Communal projects
# ---------------------------------------------------------------------------

class TestCommunalProjects:
    def test_harvest_project_starts_when_ready(self):
        vs = _village_initial()
        _, projects, events, s, c = evaluate_communal_projects(
            village_id=vs.village_id, tick_number=5, previous_projects={},
            leadership=None, emergency_level=0.0,
            avg_harvest_readiness=0.99, available_workers=("h0", "h1", "h2", "h3"),
        )
        assert s >= 1
        assert any(isinstance(e, PublicProjectStarted) and e.project_type == "Harvest" for e in events)

    def test_road_and_bridge_repair_on_damage(self):
        vs = _village_initial()
        _, projects, events, s, c = evaluate_communal_projects(
            village_id=vs.village_id, tick_number=5, previous_projects={},
            leadership=None, emergency_level=0.0,
            roads_damaged=True, bridges_damaged=True,
            available_workers=("h0","h1","h2","h3","h4"),
        )
        started_types = {e.project_type for e in events if isinstance(e, PublicProjectStarted)}
        assert "RoadRepair" in started_types
        assert "BridgeRepair" in started_types

    def test_projects_progress_then_complete(self):
        vs = _village_initial()
        pid = make_project_id(vs.village_id, "Harvest", 0)
        # required_ticks=1 so at tick 1 we should see completion
        seed = {pid: CommunalProject(project_id=pid, project_type="Harvest", village_id=vs.village_id, name="H", assigned_workers=("h0","h1","h2"), required_workers=3, required_ticks=1, start_tick=0, progress=0.0, active=True)}
        _, _, ev1, _s, _c = evaluate_communal_projects(village_id=vs.village_id, tick_number=1, previous_projects=seed, leadership=None, emergency_level=0.0, available_workers=("h0","h1","h2"))
        completed_events = [e for e in ev1 if isinstance(e, PublicProjectCompleted)]
        assert len(completed_events) >= 1

    def test_fire_response_on_fire_risk(self):
        vs = _village_initial()
        _, _, ev, s, _ = evaluate_communal_projects(village_id=vs.village_id, tick_number=5, previous_projects={}, leadership=None, emergency_level=0.2, fire_risk_active=True, available_workers=("h0","h1","h2"))
        assert any(isinstance(e, PublicProjectStarted) and e.project_type == "FireResponse" for e in ev)


# ---------------------------------------------------------------------------
# 7. Celebrations
# ---------------------------------------------------------------------------

class TestCelebrations:
    def test_harvest_festival_from_surplus(self):
        vs = _village_initial()
        _, _, ev, days = evaluate_celebrations(
            village_id=vs.village_id, tick_number=20, previous_celebrations={},
            emergency_level=0.0, prosperity=0.7, morale=0.6, harvest_surplus=120.0, population=8,
        )
        assert any(isinstance(e, HarvestFestivalStarted) for e in ev)
        assert any(isinstance(e, CelebrationStarted) and e.celebration_type == "HarvestFestival" for e in ev)

    def test_celebration_ends_after_duration(self):
        vs = _village_initial()
        cid = make_celebration_id(vs.village_id, "HarvestFestival", 0)
        seed = {cid: ActiveCelebration(celebration_id=cid, celebration_type="HarvestFestival", village_id=vs.village_id, name="HF", start_tick=0, duration_ticks=2)}
        _, _, ev, days = evaluate_celebrations(
            village_id=vs.village_id, tick_number=3, previous_celebrations=seed,
            emergency_level=0.0, prosperity=0.7, morale=0.6, harvest_surplus=120.0, population=8,
        )
        assert any(isinstance(e, HarvestFestivalEnded) for e in ev)
        assert any(isinstance(e, CelebrationEnded) and e.celebration_type == "HarvestFestival" for e in ev)

    def test_wedding_feast_on_marriages(self):
        vs = _village_initial()
        _, _, ev, _ = evaluate_celebrations(
            village_id=vs.village_id, tick_number=10, previous_celebrations={},
            emergency_level=0.0, prosperity=0.7, morale=0.6, marriages_count_recent=1,
        )
        assert any(isinstance(e, CelebrationStarted) and e.celebration_type == "WeddingFeast" for e in ev)


# ---------------------------------------------------------------------------
# 8. evaluate_village_tick composes all
# ---------------------------------------------------------------------------

class TestEvaluateVillageTick:
    def test_empty_village_no_crash(self):
        vs = _village_initial()
        out = evaluate_village_tick(
            previous=vs,
            leadership=None,
            tick_number=1,
            population_new=0,
            workforce_new=0,
            food_reserve_new=0.0,
            wood_reserve_new=0.0,
        )
        new_v, new_l, hhs, projs, cels, ems, evs = out
        assert new_v.last_updated_tick == 1
        assert new_v.population == 0

    def test_population_and_metrics_change(self):
        vs = _village_initial()
        leadership = Leadership(village_id=vs.village_id, leader_entity_id="h000", leadership_effectiveness=0.7)
        new_v, *_ = evaluate_village_tick(
            previous=vs, leadership=leadership, tick_number=15, population_new=6, workforce_new=6,
            occupations_new=(("Farmer",3),("Woodcutter",3)), food_reserve_new=300.0, wood_reserve_new=250.0,
            avg_health=0.8, avg_relationship=0.6, avg_trust=0.7,
            available_leader_ids=("h000","h001","h002"), available_workers=tuple(f"h{i:03d}" for i in range(6)),
            harvest_value=60.0,
        )
        assert new_v.population == 6
        assert new_v.prosperity != DEFAULT_PROSPERITY or new_v.stability != DEFAULT_STABILITY or new_v.morale != DEFAULT_MORALE

    def test_population_change_event_on_delta(self):
        vs = _village_initial()
        vs.__class__.__name__  # ensure it's a real VillageState; population already 0
        leadership = Leadership(village_id=vs.village_id)
        *_, evs = evaluate_village_tick(
            previous=vs, leadership=leadership, tick_number=5, population_new=8, workforce_new=8,
            food_reserve_new=100.0, wood_reserve_new=80.0,
            available_leader_ids=(f"h{i}" for i in range(5)), available_workers=tuple(f"h{i}" for i in range(8)),
        )
        pops = [e for e in evs if isinstance(e, PopulationChanged)]
        assert len(pops) >= 1
        assert pops[0].delta == 8

    def test_metric_delta_events_emitted(self):
        vs = _village_initial()
        leadership = Leadership(village_id=vs.village_id)
        *_, evs = evaluate_village_tick(
            previous=vs, leadership=leadership, tick_number=5, population_new=8, workforce_new=8,
            food_reserve_new=500.0, wood_reserve_new=200.0,
            avg_health=0.9, avg_relationship=0.85, avg_trust=0.9,
            available_leader_ids=tuple(f"h{i}" for i in range(5)),
            available_workers=tuple(f"h{i}" for i in range(8)),
            harvest_value=200.0, production_value=60.0,
        )
        types = {e.to_dict().get("event_type") for e in evs}
        # At minimum, leadership + population + metric deltas or change events expected
        assert "PopulationChanged" in types
        assert "LeaderAssigned" in types
        assert "ProsperityChanged" in types or "VillageProspered" in types or "VillageDeclined" in types


# ---------------------------------------------------------------------------
# 9. Planner integration: derive_society_goals
# ---------------------------------------------------------------------------

class TestPlannerIntegration:
    def test_goals_on_food_shortage(self):
        vs = _village_initial()
        vs_updated = VillageState.from_dict({**vs.to_dict(), "population": 20, "food_reserve": 10.0})
        goals = derive_society_goals(village=vs_updated, leadership=None, active_emergencies={}, tick_number=5)
        goal_names = [g["goal"] for g in goals]
        assert "expand_farming_and_rationing" in goal_names

    def test_goals_when_disease_active(self):
        vs = _village_initial()
        vid = vs.village_id
        eid = make_emergency_id(vid, "DiseaseOutbreak")
        emer_map = {eid: ActiveEmergency(emergency_id=eid, emergency_type="DiseaseOutbreak", village_id=vid, severity=0.7, declared_tick=0)}
        vs2 = VillageState.from_dict({**vs.to_dict(), "population": 8, "active_emergencies": [eid]})
        goals = derive_society_goals(village=vs2, leadership=None, active_emergencies=emer_map, tick_number=5)
        goal_names = [g["goal"] for g in goals]
        assert "reduce_gatherings_and_recover" in goal_names

    def test_goals_on_fire_emergency(self):
        vs = _village_initial()
        vid = vs.village_id
        eid = make_emergency_id(vid, "Fire")
        emer_map = {eid: ActiveEmergency(emergency_id=eid, emergency_type="Fire", village_id=vid, severity=0.8, declared_tick=0)}
        vs2 = VillageState.from_dict({**vs.to_dict(), "population": 8, "active_emergencies": [eid]})
        goals = derive_society_goals(village=vs2, leadership=None, active_emergencies=emer_map, tick_number=5)
        assert goals and goals[0]["goal"] == "organize_fire_response"
        assert goals[0]["priority"] > 0.9

    def test_morale_goal_when_low(self):
        vs = VillageState.from_dict({**_village_initial().to_dict(), "morale": 0.2, "emergency_level": 0.0, "population": 8, "food_reserve": 500.0})
        goals = derive_society_goals(village=vs, leadership=None, active_emergencies={}, tick_number=5)
        names = [g["goal"] for g in goals]
        assert "community_celebration" in names

    def test_invest_public_projects_when_thriving(self):
        vs_dict = _village_initial().to_dict()
        vs_dict.update({"prosperity": 0.9, "stability": 0.9, "morale": 0.9, "emergency_level": 0.0, "population": 8, "food_reserve": 500.0, "wood_reserve": 400.0})
        vs = VillageState.from_dict(vs_dict)
        goals = derive_society_goals(village=vs, leadership=None, active_emergencies={}, tick_number=5)
        names = [g["goal"] for g in goals]
        assert "invest_in_public_projects" in names


# ---------------------------------------------------------------------------
# 10. Simulation actions (TransitionProposals)
# ---------------------------------------------------------------------------

def _proposal_keys_ok(p: Mapping[str, Any]) -> bool:
    return all(k in p for k in ("subject", "patch", "metadata", "correlation_id", "state_revision"))


class TestSimulationProposals:
    def test_hold_meeting_action(self):
        vs = _village_initial()
        p = hold_meeting_action(village_id=vs.village_id, tick_number=5, state_revision=1, agenda="planning", attendees=("h0","h1"), leader_entity_id="h0")
        assert _proposal_keys_ok(p)
        assert p["subject"].startswith("domain.society.action.hold_meeting")
        assert p["metadata"]["meeting_held"] is True
        assert "meeting" in str(p["patch"]["society.events.requested"][0].get("event_type")).lower()

    def test_assign_work_action(self):
        vs = _village_initial()
        p = assign_work_action(village_id=vs.village_id, tick_number=6, state_revision=1, assignments={"h0": "Farmer", "h1": "Woodcutter"}, source="village_council")
        assert _proposal_keys_ok(p)
        assert p["metadata"]["assignments_count"] == 2
        assert "Farmer" in p["patch"]["society.labor_assignments_requested"].values()

    def test_deliver_supplies_action(self):
        vs = _village_initial()
        p = deliver_supplies_action(village_id=vs.village_id, tick_number=7, state_revision=2, from_location="granary", to_location="e_household", supplies={"food": 10.0, "water": 5.0}, transporter_entity_id="h2")
        assert _proposal_keys_ok(p)
        req = p["patch"]["society.supply_delivery_requested"]
        assert req["from_location"] == "granary"
        assert req["supplies"]["water"] == pytest.approx(5.0)

    def test_repair_structure_action(self):
        vs = _village_initial()
        p = repair_structure_action(village_id=vs.village_id, tick_number=8, state_revision=1, structure_id="bridge_main", structure_type="Bridge", workers=("h0","h1","h2"), project_type="BridgeRepair")
        assert _proposal_keys_ok(p)
        assert p["metadata"]["structure_type"] == "Bridge"

    def test_organize_harvest_action(self):
        vs = _village_initial()
        p = organize_harvest_action(village_id=vs.village_id, tick_number=9, state_revision=3, harvesters=("h0","h1","h2"), target_field_ids=("fA","fB"))
        assert _proposal_keys_ok(p)
        assert p["metadata"]["harvesters_count"] == 3
        assert p["metadata"]["fields_count"] == 2

    def test_celebrate_action(self):
        vs = _village_initial()
        p = celebrate_action(village_id=vs.village_id, tick_number=10, celebration_type="HarvestFestival", name="Harvest Home", organizer="h0", participants=("h0","h1","h2","h3"))
        assert _proposal_keys_ok(p)
        assert p["metadata"]["celebration_type"] == "HarvestFestival"
        assert p["patch"]["society.celebration_requested"]["duration_ticks"] == 3

    def test_respond_emergency_action(self):
        vs = _village_initial()
        eid = make_emergency_id(vs.village_id, "Fire")
        p = respond_emergency_action(village_id=vs.village_id, tick_number=11, state_revision=1, emergency_id=eid, emergency_type="Fire", responders=("h0","h1","h2"), instructions="carry water and clear perimeter")
        assert _proposal_keys_ok(p)
        assert p["metadata"]["emergency_type"] == "Fire"

    def test_inspect_storage_action(self):
        vs = _village_initial()
        p = inspect_storage_action(village_id=vs.village_id, tick_number=12, state_revision=1, inspector_entity_id="h5", locations=("granary_east", "cellar_main"))
        assert _proposal_keys_ok(p)
        assert p["metadata"]["inspection_requested"] is True

    def test_support_neighbor_action(self):
        vs = _village_initial()
        p = support_neighbor_action(village_id=vs.village_id, tick_number=13, supporter_entity_id="h0", neighbor_entity_id="h7", aid_goods={"food": 8.0, "wood": 6.0})
        assert _proposal_keys_ok(p)
        assert p["metadata"]["support_requested"] is True
        assert p["metadata"]["aid_goods_count"] == 2


# ---------------------------------------------------------------------------
# 11. apply(simulation context) -> TransitionProposal / Kernel authority
# ---------------------------------------------------------------------------

class TestApplyAndKernelAuthority:
    def test_apply_returns_proposal(self):
        vs = _village_initial()
        world_state = {
            "world_id": "w_loop12",
            "name": "Greenfield",
            "village_name": "Greenfield",
            "entities": _human_entities(6, health=0.85),
            "resource_stocks": {"food": {"current_quantity": 300.0}, "wood": {"current_quantity": 200.0}, "water": {"current_quantity": 150.0}},
            "weather": {"temperature_c": 22.0, "rainfall": 0.0, "wind_speed": 2.0, "weather_type": "Clear", "severity": 0.0},
            "society": {
                "village_state": vs.to_dict(),
            },
        }
        ctx = {"world_state": world_state, "tick_number": 5, "state_revision": 2}
        prop = apply(ctx)
        assert _proposal_keys_ok(prop)
        patch = prop["patch"]
        assert "society" in patch
        assert "village_state" in patch["society"]
        soc = patch["society"]["village_state"]
        for field in ("village_id", "prosperity", "stability", "morale", "population", "workforce_size", "emergency_level", "active_projects", "active_celebrations", "active_emergencies", "occupations"):
            assert field in soc, field
        meta = prop["metadata"]
        for field in ("entities_evaluated", "prosperity", "stability", "morale", "emergency_level", "events_count", "households_count", "projects_count", "celebrations_count", "emergencies_count"):
            assert field in meta, field

    def test_apply_no_direct_mutation(self):
        vs = _village_initial()
        entities = _human_entities(6, health=0.85)
        ws = {
            "world_id": "w_loop12", "village_name": "Greenfield",
            "entities": entities,
            "resource_stocks": {"food": {"current_quantity": 300.0}, "wood": {"current_quantity": 200.0}},
            "weather": {"temperature_c": 22.0},
            "society": {"village_state": vs.to_dict()},
        }
        snap_before = (copy.deepcopy(ws), copy.deepcopy(vs.to_dict()))
        ctx = {"world_state": ws, "tick_number": 5, "state_revision": 2}
        _ignored = apply(ctx)
        # world_state or village_state shouldn't be mutated by apply() directly
        snap_after = (copy.deepcopy(ws), copy.deepcopy(vs.to_dict()))
        assert snap_before == snap_after

    def test_register_all_includes_society(self):
        class FakeEngine:
            def __init__(self):
                self._domains = {}
            def register_domain(self, name, fn):
                self._domains[name] = fn
        engine = FakeEngine()
        register_all(engine)
        assert "society" in engine._domains
        assert "health" in engine._domains

    def test_society_active_projections(self):
        vs = _village_initial()
        vid = vs.village_id
        pid = make_project_id(vid, "Harvest", 0)
        p = CommunalProject(project_id=pid, project_type="Harvest", village_id=vid, name="H", assigned_workers=("h0",), start_tick=0, active=True)
        eid = make_emergency_id(vid, "FoodCrisis")
        em = ActiveEmergency(emergency_id=eid, emergency_type="FoodCrisis", village_id=vid, severity=0.6, declared_tick=0)
        ws = {"society": {"village_state": vs.to_dict(), "communal_projects": {pid: p.to_dict()}, "emergencies": {eid: em.to_dict()}}}
        projects = society_active_projects(ws)
        emergencies = society_active_emergencies(ws)
        assert len(projects) == 1
        assert projects[0].project_id == pid
        assert len(emergencies) == 1
        assert emergencies[0].emergency_type == "FoodCrisis"

    def test_village_summary(self):
        vs = _village_initial()
        vs = VillageState.from_dict({**vs.to_dict(), "population": 10, "food_reserve": 500.0, "wood_reserve": 200.0, "prosperity": 0.8, "morale": 0.75, "stability": 0.82})
        leader = Leadership(village_id=vs.village_id, leader_entity_id="h0", leadership_effectiveness=0.8)
        ws = {"society": {"village_state": vs.to_dict(), "leadership": leader.to_dict()}}
        summary = get_village_summary(ws)
        for key in ("village_id", "village_name", "population", "workforce_size", "food_reserve", "wood_reserve", "prosperity", "stability", "morale", "leader_entity_id", "leadership_effectiveness", "occupations"):
            assert key in summary, key
        assert summary["population"] == 10
        assert summary["prosperity"] == pytest.approx(0.8)


# ---------------------------------------------------------------------------
# 12. Events frozen
# ---------------------------------------------------------------------------

EVENT_CLASSES = (
    VillageMeetingHeld,
    LeaderAssigned,
    HarvestFestivalStarted,
    HarvestFestivalEnded,
    EmergencyDeclared,
    EmergencyResolved,
    VillageProspered,
    VillageDeclined,
    FoodCrisisStarted,
    FoodCrisisResolved,
    PublicProjectStarted,
    PublicProjectCompleted,
    MoraleChanged,
    ProsperityChanged,
    StabilityChanged,
    PopulationChanged,
    CelebrationStarted,
    CelebrationEnded,
)


def _sample_event(cls):
    vid = make_village_id("w", "V")
    kwargs = {"village_id": vid, "tick_number": 1}
    if cls is LeaderAssigned:
        kwargs.update(leader_entity_id="e1", leader_role="Elder")
    if cls is EmergencyDeclared:
        kwargs.update(emergency_id=make_emergency_id(vid, "X"), emergency_type="Fire", severity=0.5)
    if cls is EmergencyResolved:
        kwargs.update(emergency_id=make_emergency_id(vid, "X"), emergency_type="Fire")
    if cls in (VillageProspered, VillageDeclined):
        kwargs.update(prosperity_delta=0.1, new_prosperity=0.7)
    if cls is FoodCrisisStarted:
        kwargs.update(reserve_shortfall=5.0)
    if cls is FoodCrisisResolved:
        kwargs.update(recovery_food_reserve=100.0)
    if cls in (HarvestFestivalStarted, PublicProjectStarted):
        kwargs.update(celebration_id=make_celebration_id(vid, "H", 1)) if "estival" in cls.__name__ else kwargs.update(project_id=make_project_id(vid, "P", 1), project_type="X")
    if cls in (PublicProjectStarted, PublicProjectCompleted):
        kwargs.update(project_id=make_project_id(vid, "P", 1), project_type="X")
    if cls is HarvestFestivalStarted:
        kwargs["celebration_id"] = make_celebration_id(vid, "H", 1)
    if cls is HarvestFestivalEnded:
        kwargs["celebration_id"] = make_celebration_id(vid, "H", 1)
    if cls in (MoraleChanged, ProsperityChanged, StabilityChanged):
        if "oral" in cls.__name__:
            kwargs.update(old_morale=0.5, new_morale=0.6)
        elif "rosperity" in cls.__name__:
            kwargs.update(old_prosperity=0.5, new_prosperity=0.6)
        else:
            kwargs.update(old_stability=0.5, new_stability=0.6)
    if cls is PopulationChanged:
        kwargs.update(old_population=4, new_population=5, delta=1)
    if cls in (CelebrationStarted, CelebrationEnded):
        kwargs["celebration_id"] = make_celebration_id(vid, "X", 1)
        kwargs["celebration_type"] = "HarvestFestival"
    return cls.create(**kwargs)


class TestEventsFrozen:
    @pytest.mark.parametrize("cls", EVENT_CLASSES)
    def test_events_are_frozen(self, cls):
        e = _sample_event(cls)
        with pytest.raises((FrozenInstanceError, AttributeError)):
            e.tick_number = 9999  # type: ignore[misc]

    @pytest.mark.parametrize("cls", EVENT_CLASSES)
    def test_events_to_dict_has_event_type(self, cls):
        e = _sample_event(cls)
        d = e.to_dict()
        assert "event_type" in d
        assert "event_id" in d


# ---------------------------------------------------------------------------
# 13. Labor priorities helper
# ---------------------------------------------------------------------------

class TestLaborPriority:
    def test_fire_and_food_first(self):
        vs = _village_initial()
        vid = vs.village_id
        fe = make_emergency_id(vid, "Fire")
        fc = make_emergency_id(vid, "FoodCrisis")
        amap = {
            fe: ActiveEmergency(emergency_id=fe, emergency_type="Fire", village_id=vid, severity=0.7, declared_tick=0),
            fc: ActiveEmergency(emergency_id=fc, emergency_type="FoodCrisis", village_id=vid, severity=0.7, declared_tick=0),
        }
        vs2 = VillageState.from_dict({**vs.to_dict(), "population": 8, "active_emergencies": [fe, fc]})
        priorities = labor_priority_for(village=vs2, active_emergencies=amap)
        sectors = [p[0] for p in priorities]
        assert sectors[0] == "FireResponse"
        assert "RoadRepair" in sectors or "Agriculture" in sectors


# ---------------------------------------------------------------------------
# 14. Replay determinism
# ---------------------------------------------------------------------------

class TestReplayDeterminism:
    def test_evaluate_village_tick_replay_id(self):
        vs = _village_initial()
        leadership = Leadership(village_id=vs.village_id)
        ents = _human_entities(8)
        kwargs = dict(
            leadership=leadership,
            tick_number=22,
            population_new=8,
            workforce_new=8,
            occupations_new=(("Farmer",3),("Woodcutter",2),("Baker",2),("Builder",1)),
            entities=ents,
            avg_health=0.78,
            avg_energy=0.7,
            avg_relationship=0.6,
            avg_trust=0.7,
            avg_conflict=0.1,
            avg_hunger_pressure=0.3,
            avg_thirst_pressure=0.2,
            avg_illness_pressure=0.05,
            avg_skill=0.55,
            production_value=40.0,
            harvest_value=100.0,
            trade_volume=15.0,
            weather_state={"temperature_c": 20.0, "rainfall": 0.0, "wind_speed": 2.0, "weather_type": "Clear", "severity": 0.0},
            food_reserve_new=300.0,
            wood_reserve_new=200.0,
            water_reserve=180.0,
            recent_deaths_count=0,
            shared_achievement_value=0.3,
            available_workers=tuple(f"h{i:03d}" for i in range(8)),
            available_leader_ids=tuple(f"h{i:03d}" for i in range(4)),
            roads_damaged=False,
            bridges_damaged=False,
            storage_disorganized=True,
            marriages_count_recent=0,
            midseason_tick=True,
        )
        out_a = evaluate_village_tick(previous=vs, **kwargs)
        out_b = evaluate_village_tick(previous=vs, **kwargs)
        s_a, *_rest_a, ev_a = out_a
        s_b, *_rest_b, ev_b = out_b
        assert s_a.to_dict() == s_b.to_dict()
        assert [e.to_dict() for e in ev_a] == [e.to_dict() for e in ev_b]

    def test_apply_replay_multirun(self):
        vs = _village_initial()
        entities = _human_entities(8)
        base_ws = {
            "world_id": "w_loop12", "village_name": "Greenfield",
            "entities": entities,
            "resource_stocks": {"food": {"current_quantity": 300.0}, "wood": {"current_quantity": 200.0}, "water": {"current_quantity": 150.0}},
            "weather": {"temperature_c": 20.0, "rainfall": 2.0, "wind_speed": 3.0, "weather_type": "Overcast", "severity": 0.1},
            "economy": {"harvest_value_tick": 50.0, "production_value_tick": 20.0, "trade_volume_tick": 10.0},
            "society": {"village_state": vs.to_dict()},
        }
        results = []
        for run in range(3):
            ctx = {"world_state": copy.deepcopy(base_ws), "tick_number": 15, "state_revision": 1}
            results.append(apply(ctx))
        assert results[0]["metadata"] == results[1]["metadata"] == results[2]["metadata"]
        vs_dict_a = results[0]["patch"]["society"]["village_state"]
        vs_dict_b = results[1]["patch"]["society"]["village_state"]
        assert vs_dict_a == vs_dict_b

    def test_long_trace_replay(self):
        vs = _village_initial()
        leadership = Leadership(village_id=vs.village_id)
        def run_trace():
            v = vs
            l = leadership
            projs, cels, emers = {}, {}, {}
            events_trace = []
            for t in range(1, 60):
                midseason = (t % 45 == 0)
                founding = (t % 180 == 0)
                marriage = (t % 19 == 0)
                v, l, _hhs, projs, cels, emers, evs = evaluate_village_tick(
                    previous=v, leadership=l, tick_number=t, households={},
                    active_projects_map=projs, active_celebrations_map=cels, active_emergencies_map=emers,
                    population_new=6, workforce_new=6, food_reserve_new=200 + t, wood_reserve_new=150 + t//2,
                    avg_health=0.75 + 0.001*t,
                    available_leader_ids=tuple(f"h{i}" for i in range(4)),
                    available_workers=tuple(f"h{i}" for i in range(6)),
                    marriages_count_recent=1 if marriage else 0,
                    midseason_tick=midseason,
                    founding_day_tick=founding,
                )
                events_trace.append((v.prosperity, v.stability, v.morale, v.emergency_level, tuple(e.to_dict()["event_type"] for e in evs)))
            return events_trace
        t1 = run_trace()
        t2 = run_trace()
        assert t1 == t2


# ---------------------------------------------------------------------------
# 15. generate_society_goals end-to-end from world-like context
# ---------------------------------------------------------------------------

class TestGenerateGoals:
    def test_generate_society_goals_from_ctx(self):
        vs = _village_initial()
        vs = VillageState.from_dict({**vs.to_dict(), "population": 8, "food_reserve": 15.0})
        ctx = {"world_state": {"society": {"village_state": vs.to_dict(), "emergencies": {}}}, "tick_number": 5}
        goals = generate_society_goals(ctx)
        assert isinstance(goals, list)
        assert any(g["goal"] == "expand_farming_and_rationing" for g in goals)


# ---------------------------------------------------------------------------
# 16. Resource shortage / emergency level invariants
# ---------------------------------------------------------------------------

class TestInvariants:
    def test_resource_shortage_in_range(self):
        for population in (1, 5, 20):
            for hh in (0, 1, 5, 10):
                s = derive_resource_shortage(food_reserve=0.0, wood_reserve=0.0, population=population, households_count=hh)
                assert 0.0 <= s <= 1.0
                s2 = derive_resource_shortage(food_reserve=10_000.0, wood_reserve=10_000.0, population=population, households_count=hh)
                assert 0.0 <= s2 <= 1.0

    def test_no_negative_metrics_in_village_state(self):
        vs = _village_initial()
        bad = vs.to_dict()
        bad["prosperity"] = -1.0
        bad["stability"] = -5.0
        bad["morale"] = -10.0
        bad["emergency_level"] = -0.1
        vs2 = VillageState.from_dict(bad)
        assert vs2.prosperity >= 0.0
        assert vs2.stability >= 0.0
        assert vs2.morale >= 0.0
        assert vs2.emergency_level >= 0.0

    def test_metrics_never_exceed_one(self):
        vs = _village_initial()
        bad = vs.to_dict()
        bad["prosperity"] = 10.0
        bad["stability"] = 10.0
        bad["morale"] = 10.0
        bad["emergency_level"] = 10.0
        vs2 = VillageState.from_dict(bad)
        assert vs2.prosperity <= 1.0
        assert vs2.stability <= 1.0
        assert vs2.morale <= 1.0
        assert vs2.emergency_level <= 1.0


# ---------------------------------------------------------------------------
# 17. Death integration (dead villagers don't participate in workforce)
# ---------------------------------------------------------------------------

class TestDeathIntegration:
    def test_dead_excluded_from_population_and_workforce(self):
        ents = _human_entities(6)
        ents[0]["alive"] = False
        ents[1]["alive"] = False
        alive, dead = derive_population_from_entities(ents)
        wf, occs = derive_workforce_from_entities(ents)
        assert alive == 4
        assert dead == 2
        assert wf == 4
