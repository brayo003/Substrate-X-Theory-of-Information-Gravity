from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from .society_models import VillageState
from .society_events import (
    EmergencyDeclared, EmergencyResolved, VillageProspered, VillageDeclined,
    FoodCrisisStarted, FoodCrisisResolved, MoraleChanged,
    ProsperityChanged, StabilityChanged
)
from .society_rules import (
    compute_prosperity, compute_stability, compute_morale, detect_emergencies
)


@dataclass
class TransitionProposal:
    action_type: str
    actor_id: str
    target_id: Optional[str]
    payload: Dict[str, Any]
    valid: bool = True
    reason: str = ""


class SocietyDomain:
    def __init__(self, village_state: Optional[VillageState] = None):
        if village_state is None:
            self.village_state = VillageState(
                village_id="village_1",
                village_name="Oakvale",
                population=0,
                workforce=0,
                food_reserve=10.0,
                wood_reserve=10.0,
                prosperity=0.5,
                stability=0.5,
                morale=0.5
            )
        else:
            self.village_state = village_state

    def observe_and_plan(self, world_ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
        goals = []
        state = self.village_state

        if "Food crisis" in state.active_emergencies or state.food_reserve < state.population * 2.0:
            goals.append({
                "type": "IncreaseFarming",
                "priority": 10,
                "reason": "Food shortage detected",
                "target_role": "farmer"
            })

        if "Flood" in state.active_emergencies:
            goals.append({
                "type": "RepairBridge",
                "priority": 9,
                "reason": "Flood mitigation",
                "target_role": "builder"
            })

        if "Fire" in state.active_emergencies:
            goals.append({
                "type": "CarryWater",
                "priority": 10,
                "reason": "Fire response",
                "target_role": "all"
            })

        if "Disease outbreak" in state.active_emergencies:
            goals.append({
                "type": "ReduceGatherings",
                "priority": 8,
                "reason": "Disease recovery",
                "target_role": "all"
            })

        if state.leader_id:
            goals.append({
                "type": "GatherVillagers",
                "priority": 5,
                "reason": "Leader called village meeting",
                "leader_id": state.leader_id
            })

        for proj_id, proj in state.communal_projects.items():
            if proj.status == "active":
                goals.append({
                    "type": f"WorkOnProject_{proj.project_type}",
                    "priority": 6,
                    "project_id": proj_id,
                    "reason": f"Communal project {proj.project_type} in progress"
                })

        if state.food_reserve > state.population * 10.0 and state.morale > 0.7:
            goals.append({
                "type": "Celebration",
                "priority": 3,
                "reason": "Large surplus celebration"
            })

        return goals

    def HoldMeeting(self, leader_id: str, attendees: List[str], topic: str) -> TransitionProposal:
        return TransitionProposal(
            action_type="HoldMeeting",
            actor_id=leader_id,
            target_id=self.village_state.village_id,
            payload={"topic": topic, "attendees": attendees}
        )

    def AssignWork(self, leader_id: str, worker_id: str, occupation: str) -> TransitionProposal:
        return TransitionProposal(
            action_type="AssignWork",
            actor_id=leader_id,
            target_id=worker_id,
            payload={"occupation": occupation}
        )

    def DeliverSupplies(self, worker_id: str, resource_type: str, amount: float, target_storage: str) -> TransitionProposal:
        return TransitionProposal(
            action_type="DeliverSupplies",
            actor_id=worker_id,
            target_id=target_storage,
            payload={"resource_type": resource_type, "amount": amount}
        )

    def RepairStructure(self, worker_id: str, structure_id: str, work_amount: float) -> TransitionProposal:
        return TransitionProposal(
            action_type="RepairStructure",
            actor_id=worker_id,
            target_id=structure_id,
            payload={"work_amount": work_amount}
        )

    def OrganizeHarvest(self, leader_id: str, project_id: str, target_field: str) -> TransitionProposal:
        return TransitionProposal(
            action_type="OrganizeHarvest",
            actor_id=leader_id,
            target_id=target_field,
            payload={"project_id": project_id}
        )

    def Celebrate(self, leader_id: str, festival_name: str) -> TransitionProposal:
        return TransitionProposal(
            action_type="Celebrate",
            actor_id=leader_id,
            target_id=self.village_state.village_id,
            payload={"festival_name": festival_name}
        )

    def RespondEmergency(self, actor_id: str, emergency_type: str, response_action: str) -> TransitionProposal:
        return TransitionProposal(
            action_type="RespondEmergency",
            actor_id=actor_id,
            target_id=self.village_state.village_id,
            payload={"emergency_type": emergency_type, "response_action": response_action}
        )

    def InspectStorage(self, inspector_id: str, storage_id: str) -> TransitionProposal:
        return TransitionProposal(
            action_type="InspectStorage",
            actor_id=inspector_id,
            target_id=storage_id,
            payload={}
        )

    def SupportNeighbor(self, helper_id: str, neighbor_id: str, assistance_type: str) -> TransitionProposal:
        return TransitionProposal(
            action_type="SupportNeighbor",
            actor_id=helper_id,
            target_id=neighbor_id,
            payload={"assistance_type": assistance_type}
        )

    def evaluate_tick(self, world_ctx: Dict[str, Any], current_tick: int) -> Dict[str, Any]:
        events = []
        st = self.village_state

        food_per_cap = st.food_reserve / max(1, st.population)
        new_pros = compute_prosperity(
            st,
            food_per_capita=food_per_cap,
            health_score=world_ctx.get("health_score", 0.8),
            economy_score=world_ctx.get("economy_score", 0.5),
            production_score=world_ctx.get("production_score", 0.5),
            relationship_score=world_ctx.get("relationship_score", 0.7),
            learning_score=world_ctx.get("learning_score", 0.5),
            agri_score=world_ctx.get("agri_score", 0.6),
            weather_resilience=world_ctx.get("weather_resilience", 0.8)
        )

        new_stab = compute_stability(
            st,
            conflict_level=world_ctx.get("conflict_level", 0.0),
            trust_level=world_ctx.get("trust_level", 0.8),
            resource_shortage_severity=0.5 if "Resource shortage" in st.active_emergencies else 0.0,
            has_leader=st.leader_id is not None,
            recent_deaths=world_ctx.get("recent_deaths", 0),
            cooperation_level=world_ctx.get("cooperation_level", 0.7)
        )

        new_mor = compute_morale(
            st,
            successful_harvests=world_ctx.get("successful_harvests", 1),
            active_festivals=len(st.active_celebrations),
            recent_deaths=world_ctx.get("recent_deaths", 0),
            conflict_level=world_ctx.get("conflict_level", 0.0),
            starvation_risk=1.0 if "Food crisis" in st.active_emergencies else 0.0,
            illness_rate=world_ctx.get("illness_rate", 0.0),
            achievements_count=world_ctx.get("achievements_count", 0)
        )

        if new_pros != st.prosperity:
            events.append(ProsperityChanged(st.village_id, st.prosperity, new_pros, tick=current_tick))
            if new_pros > st.prosperity:
                events.append(VillageProspered(st.village_id, new_pros, tick=current_tick))
            else:
                events.append(VillageDeclined(st.village_id, "Prosperity decreased", tick=current_tick))

        if new_stab != st.stability:
            events.append(StabilityChanged(st.village_id, st.stability, new_stab, tick=current_tick))

        if new_mor != st.morale:
            events.append(MoraleChanged(st.village_id, st.morale, new_mor, tick=current_tick))

        detected = detect_emergencies(
            st,
            severe_weather=world_ctx.get("severe_weather", False),
            fire_active=world_ctx.get("fire_active", False),
            disease_outbreak=world_ctx.get("disease_outbreak", False)
        )

        new_emergencies = [e[0] for e in detected]
        for em_type, sev in detected:
            if em_type not in st.active_emergencies:
                events.append(EmergencyDeclared(st.village_id, em_type, sev, tick=current_tick))
                if em_type == "Food crisis":
                    events.append(FoodCrisisStarted(st.village_id, tick=current_tick))

        for em_type in st.active_emergencies:
            if em_type not in new_emergencies:
                events.append(EmergencyResolved(st.village_id, em_type, tick=current_tick))
                if em_type == "Food crisis":
                    events.append(FoodCrisisResolved(st.village_id, tick=current_tick))

        return {
            "new_prosperity": new_pros,
            "new_stability": new_stab,
            "new_morale": new_mor,
            "active_emergencies": new_emergencies,
            "events": events
        }
