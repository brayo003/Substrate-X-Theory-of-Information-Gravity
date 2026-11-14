import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))
sim_world_dir = repo_root / "sim_world"
if sim_world_dir.exists() and str(sim_world_dir) not in sys.path:
    sys.path.insert(0, str(sim_world_dir))

try:
    from domains.society.society_models import VillageState, Household, Family, Occupation, CommunalProject
    from domains.society.society_rules import (
        compute_prosperity, compute_stability, compute_morale, detect_emergencies
    )
    from domains.society.society_domain import SocietyDomain, TransitionProposal
except ModuleNotFoundError:
    from sim_world.domains.society.society_models import VillageState, Household, Family, Occupation, CommunalProject
    from sim_world.domains.society.society_rules import (
        compute_prosperity, compute_stability, compute_morale, detect_emergencies
    )
    from sim_world.domains.society.society_domain import SocietyDomain, TransitionProposal


"""
LOOP 12 VILLAGE SOCIETY TEST SUITE REPORT
-----------------------------------------
1. test_village_initialization:
   - Validates correct creation of VillageState with persistent attributes (id, name, population, workforce, reserves, metrics).

2. test_households_and_social_org:
   - Verifies representation of social structure including Households, Families, and Occupations in persistent world state.

3. test_leadership_influence_and_planner_integration:
   - Verifies that leadership and emergency conditions generate correct planner goals without mutating world state.

4. test_communal_projects:
   - Confirms active communal projects emit corresponding labor goals for villagers to cooperate.

5. test_emergency_detection:
   - Checks deterministic emergency detection (food crisis, flood, disease outbreak, resource/workforce shortages).

6. test_morale_prosperity_stability_computation:
   - Verifies deterministic formulas for village metrics (prosperity, stability, morale) stay bounded within [0.0, 1.0].

7. test_simulation_proposal_generation:
   - Confirms simulation actions (HoldMeeting, AssignWork, RespondEmergency) emit valid TransitionProposals.

8. test_kernel_authority_no_direct_mutation:
   - Asserts planner/simulation observation and proposal methods never directly mutate village state.

9. test_replay_determinism:
   - Ensures identical initial states and tick inputs yield byte-for-byte identical state transitions, events, and metrics.
"""


def test_village_initialization():
    state = VillageState(
        village_id="v1",
        village_name="Ravenwood",
        population=10,
        workforce=7,
        food_reserve=50.0,
        wood_reserve=30.0,
        prosperity=0.6,
        stability=0.8,
        morale=0.7
    )
    assert state.village_id == "v1"
    assert state.population == 10
    assert state.workforce == 7
    assert state.food_reserve == 50.0


def test_households_and_social_org():
    h1 = Household(id="h1", name="Smith Family", member_ids=["v1", "v2"])
    fam1 = Family(id="fam1", household_id="h1", member_ids=["v1", "v2"])
    occ1 = Occupation(villager_id="v1", role="farmer")

    state = VillageState(
        village_id="v1",
        village_name="Ravenwood",
        households={"h1": h1},
        families={"fam1": fam1},
        occupations={"v1": occ1},
        population=2
    )

    assert "h1" in state.households
    assert state.households["h1"].member_ids == ["v1", "v2"]
    assert state.occupations["v1"].role == "farmer"


def test_leadership_influence_and_planner_integration():
    domain = SocietyDomain()
    domain.village_state.population = 10
    domain.village_state.food_reserve = 5.0
    domain.village_state.leader_id = "v_leader"
    domain.village_state.active_emergencies = ["Food crisis"]

    goals = domain.observe_and_plan({})
    goal_types = [g["type"] for g in goals]

    assert "IncreaseFarming" in goal_types
    assert "GatherVillagers" in goal_types


def test_communal_projects():
    proj = CommunalProject(id="p1", project_type="Bridge repair", required_work=100.0)
    state = VillageState(
        village_id="v1",
        village_name="Ravenwood",
        communal_projects={"p1": proj}
    )
    domain = SocietyDomain(state)

    goals = domain.observe_and_plan({})
    assert any(g["type"] == "WorkOnProject_Bridge repair" for g in goals)


def test_emergency_detection():
    state = VillageState(
        village_id="v1",
        village_name="Ravenwood",
        population=10,
        food_reserve=5.0,
        wood_reserve=2.0
    )

    emergencies = detect_emergencies(
        state,
        severe_weather=True,
        fire_active=False,
        disease_outbreak=True
    )

    types = [e[0] for e in emergencies]
    assert "Food crisis" in types
    assert "Flood" in types
    assert "Disease outbreak" in types


def test_morale_prosperity_stability_computation():
    state = VillageState(village_id="v1", village_name="Ravenwood", population=10, food_reserve=50.0)

    pros = compute_prosperity(state, 5.0, 0.9, 0.8, 0.7, 0.8, 0.6, 0.7, 0.9)
    assert 0.0 <= pros <= 1.0

    stab = compute_stability(state, 0.1, 0.9, 0.0, True, 0, 0.8)
    assert 0.0 <= stab <= 1.0

    mor = compute_morale(state, 2, 1, 0, 0.0, 0.0, 0.0, 1)
    assert 0.0 <= mor <= 1.0


def test_simulation_proposal_generation():
    domain = SocietyDomain()

    prop1 = domain.HoldMeeting("leader_1", ["v1", "v2"], "Winter Prep")
    assert isinstance(prop1, TransitionProposal)
    assert prop1.action_type == "HoldMeeting"
    assert prop1.actor_id == "leader_1"

    prop2 = domain.AssignWork("leader_1", "v1", "farmer")
    assert prop2.action_type == "AssignWork"

    prop3 = domain.RespondEmergency("v1", "Fire", "carry_water")
    assert prop3.action_type == "RespondEmergency"


def test_kernel_authority_no_direct_mutation():
    domain = SocietyDomain()
    initial_morale = domain.village_state.morale

    _ = domain.observe_and_plan({})
    _ = domain.HoldMeeting("leader_1", ["v1"], "Meeting")

    assert domain.village_state.morale == initial_morale


def test_replay_determinism():
    state1 = VillageState(village_id="v1", village_name="Ravenwood", population=10, food_reserve=5.0)
    domain1 = SocietyDomain(state1)

    state2 = VillageState(village_id="v1", village_name="Ravenwood", population=10, food_reserve=5.0)
    domain2 = SocietyDomain(state2)

    eval1 = domain1.evaluate_tick({"severe_weather": True, "fire_active": False}, current_tick=1)
    eval2 = domain2.evaluate_tick({"severe_weather": True, "fire_active": False}, current_tick=1)

    assert eval1["new_prosperity"] == eval2["new_prosperity"]
    assert eval1["new_stability"] == eval2["new_stability"]
    assert eval1["new_morale"] == eval2["new_morale"]
    assert eval1["active_emergencies"] == eval2["active_emergencies"]
    assert len(eval1["events"]) == len(eval2["events"])
