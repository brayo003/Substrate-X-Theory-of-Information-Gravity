"""
50-Tick Controlled Field-to-Agent Behavioral Causality Experiment

This experiment tests whether an actively reasoning autonomous agent behaves
differently when exposed to different physical-field regimes over 50 ticks.

World A: Baseline field condition (c_nominal = 1.0)
World B: Perturbed field condition (c_nominal = 2.0)
Total: 50 ticks per world with LLM generation enabled
"""

import sys
import os
import json
from datetime import datetime
from typing import Any, Dict, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sim_world.kernel.world_kernel import WorldKernel
from sim_world.core.config import KernelConfig
from sim_world.core.ids import WorldId
from sim_world.domains.physical_field import register as register_physical_field
from sim_world.domains.needs import register as register_needs
from sim_world.domains.population import register as register_population
from sim_world.entities.components import NeedsComponent, TransformComponent, InventoryComponent, ResourceDescriptor


class FieldAgentBehavioralCausalityExperiment:
    """50-tick controlled field-to-agent behavioral causality experiment."""
    
    TOTAL_TICKS = 50  # Increased for more cognitive cycles
    SEED = "controlled_experiment_fixed_seed"
    
    def __init__(self):
        self.trace_A = []
        self.trace_B = []
        self.divergence_tracker = {
            "field_parameters": None,
            "spectral_observable": None,
            "agent_perception": None,
            "llm_input": None,
            "llm_output": None,
            "intent": None,
            "goal": None,
            "plan": None,
            "action": None,
            "state": None,
            "memory": None,
        }
        self.field_params_A = {"c_nominal": 1.0, "tau_nominal": 1.0}
        self.field_params_B = {"c_nominal": 2.0, "tau_nominal": 1.0}
    
    def create_world(self, world_name, field_params):
        """Create a world with controlled field parameters and LLM enabled."""
        print(f"\nCreating {world_name} with field params: {field_params}")
        
        # Create kernel with LLM generation enabled and fixed seed
        world_id = WorldId.new(world_name)
        config = KernelConfig(
            world_id=world_id,
            initial_state={},
            enable_llm_generation=True,  # CRITICAL: LLM enabled
            seed=self.SEED  # CRITICAL: Same seed for both worlds
        )
        kernel = WorldKernel(config=config)
        
        # Register domains
        register_physical_field(kernel.simulation_engine)
        register_needs(kernel.simulation_engine)
        register_population(kernel.simulation_engine)
        
        # Initialize physical field with kernel's method (per-world isolation)
        kernel.initialize_physical_field(
            c_nominal=field_params["c_nominal"],
            tau_nominal=field_params["tau_nominal"]
        )
        print(f"  ✓ Field parameters set: c={field_params['c_nominal']}, tau={field_params['tau_nominal']}")
        print(f"  ✓ LLM generation enabled: {config.enable_llm_generation}")
        print(f"  ✓ Seed: {config.seed}")
        
        # Create single entity with identical initial state
        entity = kernel.entity_registry.create_entity(
            entity_type="human",
            display_name="TestAgent",  # Same name for both worlds
            created_tick=0,
            created_revision=None,
            components=[
                TransformComponent(room="village_center"),
                NeedsComponent(needs={"hunger": 0.7, "thirst": 0.5, "energy": 0.8}),
                InventoryComponent(items=(
                    ResourceDescriptor(identifier="food", quantity=2.0),
                    ResourceDescriptor(identifier="water", quantity=3.0),
                )),
            ],
        )
        entity_id = entity.entity_id
        print(f"  ✓ Created entity: {entity_id}")
        
        # Assert single entity
        entity_count = len(kernel.entity_registry.entities)
        assert entity_count == 1, f"Expected 1 entity, got {entity_count}"
        print(f"  ✓ Entity count: {entity_count}")
        
        # Configure reasoning coordinator for consistent behavior
        kernel.reasoning_coordinator.set_importance_threshold(0.0)  # Always reason
        kernel.reasoning_coordinator.reasoning_cooldown_ticks = 0  # No cooldown
        kernel.reasoning_coordinator.reasoning_cooldown_seconds = 0.0  # No cooldown
        kernel.reasoning_coordinator.max_entities_per_tick = 10  # Allow many entities
        
        return kernel, entity_id
    
    def collect_tick_data(self, kernel, entity_id, tick, world_name):
        """Collect complete causal chain data for a tick."""
        data = {
            "tick": tick,
            "world": world_name,
            "field": {},
            "perception": {},
            "llm": {},
            "cognition": {},
            "action": {},
            "state": {},
            "memory": {},
        }
        
        # Layer 1: Physical field
        if kernel._propagation_params is not None:
            data["field"]["kernel_c_nominal"] = kernel._propagation_params.c_nominal
        if kernel._relaxation_params is not None:
            data["field"]["kernel_tau_nominal"] = kernel._relaxation_params.tau_nominal
        
        spectral_obs = kernel.last_spectral_transport_observable
        if spectral_obs is not None:
            data["field"]["dominant_regime"] = spectral_obs.dominant_regime
            data["field"]["dominant_k"] = spectral_obs.dominant_k
            data["field"]["dominant_D"] = spectral_obs.dominant_D
            data["field"]["weighted_D"] = spectral_obs.weighted_D
            data["field"]["propagating_power_fraction"] = spectral_obs.propagating_power_fraction
            data["field"]["overdamped_power_fraction"] = spectral_obs.overdamped_power_fraction
            data["field"]["critical_power_fraction"] = spectral_obs.critical_power_fraction
            data["field"]["spectral_entropy"] = spectral_obs.spectral_entropy
            data["field"]["c_nominal"] = spectral_obs.c_nominal
            data["field"]["tau_nominal"] = spectral_obs.tau_nominal
        
        # Layer 2: Agent perception (Q observation)
        transport_obs = kernel.last_transport_observation
        if transport_obs is not None:
            data["perception"]["q_value"] = transport_obs.q_value
            data["perception"]["q_regime"] = transport_obs.regime
        
        # Layer 3 & 4: LLM input/output (from reasoning coordinator)
        entity_cycles = kernel.reasoning_coordinator.cycle_tracker.get_cycles_for_entity(str(entity_id))
        if entity_cycles:
            last_cycle = entity_cycles[-1]  # Get most recent cycle
            data["llm"]["reasoning_tick"] = last_cycle.tick_id
            data["llm"]["reasoning_time"] = last_cycle.timestamp.isoformat()
            data["llm"]["reasoning_success"] = last_cycle.succeeded
            data["llm"]["intent_text"] = last_cycle.intent_text
            data["llm"]["reasoning_text"] = last_cycle.reasoning_text
            data["llm"]["confidence"] = last_cycle.confidence
            data["llm"]["goal_kind"] = last_cycle.goal_kind
        
        # Layer 5 & 6: Planning and Action
        if kernel._current_revision:
            data["action"]["event_count"] = len(kernel._current_revision.events)
            # Extract action details from events
            actions = []
            for event in kernel._current_revision.events:
                if hasattr(event, 'action') or 'action' in str(event):
                    actions.append(str(event))
            data["action"]["events"] = actions[:5]  # Limit to first 5 actions
        
        # Layer 7: State mutation
        entity = kernel.entity_registry.get_entity(entity_id)
        if entity:
            data["state"]["entity_type"] = entity.type
            data["state"]["alive"] = entity.alive
            data["state"]["enabled"] = entity.enabled
            
            needs_comp = entity.get_component("NeedsComponent")
            if needs_comp:
                data["state"]["needs"] = dict(needs_comp.needs)
            
            transform_comp = entity.get_component("TransformComponent")
            if transform_comp:
                data["state"]["location"] = transform_comp.room
        
        # Layer 8: Memory
        memory = kernel.entity_registry.agent_memories.get(entity_id)
        if memory:
            data["memory"]["record_count"] = len(memory.records)
            # Get recent memory records
            recent_records = []
            for record in list(memory.records)[-3:]:  # Last 3 records
                # Handle both string records and object records
                if hasattr(record, 'kind'):
                    recent_records.append({
                        "kind": record.kind,
                        "tick_id": str(record.tick_id) if record.tick_id else None,
                    })
                else:
                    recent_records.append({
                        "content": str(record)[:100],  # Truncate for readability
                    })
            data["memory"]["recent_records"] = recent_records
        
        return data
    
    def compare_layers(self, data_A, data_B):
        """Compare two tick data points layer by layer."""
        divergences = {}
        
        # Layer 1: Field parameters
        if data_A["field"].get("kernel_c_nominal") != data_B["field"].get("kernel_c_nominal"):
            divergences["field_parameters"] = {
                "tick": data_A["tick"],
                "A": data_A["field"]["kernel_c_nominal"],
                "B": data_B["field"]["kernel_c_nominal"]
            }
        
        # Layer 1: Spectral observable
        if data_A["field"].get("dominant_D") != data_B["field"].get("dominant_D"):
            divergences["spectral_observable"] = {
                "tick": data_A["tick"],
                "A": data_A["field"]["dominant_D"],
                "B": data_B["field"]["dominant_D"]
            }
        
        # Layer 2: Agent perception
        if data_A["perception"].get("q_value") != data_B["perception"].get("q_value"):
            divergences["agent_perception"] = {
                "tick": data_A["tick"],
                "A": data_A["perception"]["q_value"],
                "B": data_B["perception"]["q_value"]
            }
        
        # Layer 3: LLM input (reasoning occurrence)
        llm_reasoned_A = data_A["llm"].get("reasoning_tick") is not None
        llm_reasoned_B = data_B["llm"].get("reasoning_tick") is not None
        if llm_reasoned_A != llm_reasoned_B:
            divergences["llm_input"] = {
                "tick": data_A["tick"],
                "A": llm_reasoned_A,
                "B": llm_reasoned_B
            }
        
        # Layer 4: LLM output (intent)
        intent_A = data_A["llm"].get("intent_text")
        intent_B = data_B["llm"].get("intent_text")
        if intent_A != intent_B and (intent_A or intent_B):
            divergences["llm_output"] = {
                "tick": data_A["tick"],
                "A": intent_A[:100] if intent_A else None,  # Truncate for readability
                "B": intent_B[:100] if intent_B else None
            }
        
        # Layer 5: Intent (from goal_kind)
        goal_A = data_A["llm"].get("goal_kind")
        goal_B = data_B["llm"].get("goal_kind")
        if goal_A != goal_B and (goal_A or goal_B):
            divergences["intent"] = {
                "tick": data_A["tick"],
                "A": goal_A,
                "B": goal_B
            }
        
        # Layer 6: Action (compare event subjects, not UUIDs)
        events_A = data_A["action"].get("events", [])
        events_B = data_B["action"].get("events", [])
        
        # Extract event subjects for comparison (ignore UUIDs)
        subjects_A = []
        for event_str in events_A:
            if "subject=" in event_str:
                subject = event_str.split("subject=")[1].split(",")[0].strip("'")
                subjects_A.append(subject)
        
        subjects_B = []
        for event_str in events_B:
            if "subject=" in event_str:
                subject = event_str.split("subject=")[1].split(",")[0].strip("'")
                subjects_B.append(subject)
        
        if subjects_A != subjects_B:
            divergences["action"] = {
                "tick": data_A["tick"],
                "A": subjects_A,
                "B": subjects_B
            }
        
        # Layer 7: State
        needs_A = data_A["state"].get("needs", {})
        needs_B = data_B["state"].get("needs", {})
        if needs_A != needs_B:
            divergences["state"] = {
                "tick": data_A["tick"],
                "A": needs_A,
                "B": needs_B
            }
        
        location_A = data_A["state"].get("location")
        location_B = data_B["state"].get("location")
        if location_A != location_B:
            if "state" not in divergences:
                divergences["state"] = {
                    "tick": data_A["tick"],
                    "A": {},
                    "B": {}
                }
            divergences["state"]["A"]["location"] = location_A
            divergences["state"]["B"]["location"] = location_B
        
        # Layer 8: Memory
        memory_count_A = data_A["memory"].get("record_count")
        memory_count_B = data_B["memory"].get("record_count")
        if memory_count_A != memory_count_B:
            divergences["memory"] = {
                "tick": data_A["tick"],
                "A": memory_count_A,
                "B": memory_count_B
            }
        
        return divergences
    
    def validate_controls(self, kernel_A, kernel_B, entity_id_A, entity_id_B):
        """Validate experimental controls before 500-tick run."""
        print("\n" + "="*80)
        print("EXPERIMENTAL CONTROL VALIDATION")
        print("="*80)
        
        controls = []
        
        # Control 1: Entity count
        entity_count_A = len(kernel_A.entity_registry.entities)
        entity_count_B = len(kernel_B.entity_registry.entities)
        control_1 = entity_count_A == 1 and entity_count_B == 1
        controls.append(("Entity count = 1 in both worlds", control_1))
        print(f"{'✓' if control_1 else '✗'} Entity count: World A={entity_count_A}, World B={entity_count_B}")
        
        # Control 2: Field parameters
        c_A = kernel_A._propagation_params.c_nominal if kernel_A._propagation_params else None
        c_B = kernel_B._propagation_params.c_nominal if kernel_B._propagation_params else None
        control_2 = c_A == 1.0 and c_B == 2.0
        controls.append(("World A c_nominal=1.0, World B c_nominal=2.0", control_2))
        print(f"{'✓' if control_2 else '✗'} Field parameters: World A c={c_A}, World B c={c_B}")
        
        # Control 3: LLM enabled
        llm_A = kernel_A.config.enable_llm_generation
        llm_B = kernel_B.config.enable_llm_generation
        control_3 = llm_A and llm_B
        controls.append(("LLM generation enabled in both worlds", control_3))
        print(f"{'✓' if control_3 else '✗'} LLM enabled: World A={llm_A}, World B={llm_B}")
        
        # Control 4: Same seed
        seed_A = kernel_A.config.seed
        seed_B = kernel_B.config.seed
        control_4 = seed_A == seed_B == self.SEED
        controls.append(("Same seed used in both worlds", control_4))
        print(f"{'✓' if control_4 else '✗'} Seed: World A={seed_A}, World B={seed_B}")
        
        # Control 5: Entity state equivalence
        entity_A = kernel_A.entity_registry.get_entity(entity_id_A)
        entity_B = kernel_B.entity_registry.get_entity(entity_id_B)
        if entity_A and entity_B:
            needs_A = entity_A.get_component("NeedsComponent").needs if entity_A.get_component("NeedsComponent") else {}
            needs_B = entity_B.get_component("NeedsComponent").needs if entity_B.get_component("NeedsComponent") else {}
            control_5 = needs_A == needs_B
            controls.append(("Entity needs equivalent", control_5))
            print(f"{'✓' if control_5 else '✗'} Entity needs: World A={needs_A}, World B={needs_B}")
        else:
            control_5 = False
            controls.append(("Entity needs equivalent", control_5))
            print(f"✗ Entity state comparison failed")
        
        # Validate all controls
        all_valid = all(control for _, control in controls)
        
        if not all_valid:
            print("\n✗ CONTROL VALIDATION FAILED - ABORTING")
            return False
        
        print("\n✓ ALL CONTROLS VALIDATED - PROCEEDING WITH 500-TICK RUN")
        return True
    
    def run_experiment(self):
        """Run the complete 500-tick controlled causality experiment."""
        print("="*80)
        print("500-TICK CONTROLLED FIELD-TO-AGENT BEHAVIORAL CAUSALITY EXPERIMENT")
        print("="*80)
        
        # Create World A with baseline field
        print(f"\n{'='*80}")
        print(f"CREATING WORLD A (BASELINE FIELD)")
        print(f"{'='*80}")
        kernel_A, entity_id_A = self.create_world("World_A", self.field_params_A)
        
        # Create World B with perturbed field
        print(f"\n{'='*80}")
        print(f"CREATING WORLD B (PERTURBED FIELD)")
        print(f"{'='*80}")
        kernel_B, entity_id_B = self.create_world("World_B", self.field_params_B)
        
        # Validate controls
        if not self.validate_controls(kernel_A, kernel_B, entity_id_A, entity_id_B):
            return self.generate_report(False, "EXPERIMENT_INVALID")
        
        # Run 10 ticks
        print(f"\n{'='*80}")
        print(f"RUNNING BOTH WORLDS FOR {self.TOTAL_TICKS} TICKS")
        print(f"{'='*80}")
        
        for tick in range(1, self.TOTAL_TICKS + 1):
            print(f"\n--- Tick {tick} ---")
            
            # Run both worlds
            kernel_A.advance_tick()
            kernel_B.advance_tick()
            
            # Force LLM reasoning for the entity
            entity_data_A = kernel_A.entity_registry.serialize().get(str(entity_id_A), {})
            entity_data_B = kernel_B.entity_registry.serialize().get(str(entity_id_B), {})
            
            # Force LLM calls by directly calling reasoning coordinator
            kernel_A.reasoning_coordinator.generate_intents_for_tick(
                entities={entity_id_A: entity_data_A},
                world_state=kernel_A.current_state,
                agent_memories={entity_id_A: kernel_A.entity_registry.agent_memories.get(entity_id_A)},
                transport_observation=kernel_A.last_transport_observation,
                spectral_observable=kernel_A.last_spectral_transport_observable,
                current_tick=tick,
                current_revision=kernel_A._current_revision.revision_id if kernel_A._current_revision else None,
            )
            
            kernel_B.reasoning_coordinator.generate_intents_for_tick(
                entities={entity_id_B: entity_data_B},
                world_state=kernel_B.current_state,
                agent_memories={entity_id_B: kernel_B.entity_registry.agent_memories.get(entity_id_B)},
                transport_observation=kernel_B.last_transport_observation,
                spectral_observable=kernel_B.last_spectral_transport_observable,
                current_tick=tick,
                current_revision=kernel_B._current_revision.revision_id if kernel_B._current_revision else None,
            )
            
            # Collect data
            data_A = self.collect_tick_data(kernel_A, entity_id_A, tick, "World_A")
            data_B = self.collect_tick_data(kernel_B, entity_id_B, tick, "World_B")
            
            self.trace_A.append(data_A)
            self.trace_B.append(data_B)
            
            # Track divergences
            divergences = self.compare_layers(data_A, data_B)
            for layer, divergence in divergences.items():
                if self.divergence_tracker[layer] is None:
                    self.divergence_tracker[layer] = divergence
                    if layer in ["action", "state", "memory"]:
                        print(f"  ⚠ FIRST DIVERGENCE at tick {tick}: {layer}")
                        print(f"    World A: {divergence['A']}")
                        print(f"    World B: {divergence['B']}")
            
            llm_calls_A = sum(1 for t in self.trace_A if t["llm"].get("reasoning_tick"))
            llm_calls_B = sum(1 for t in self.trace_B if t["llm"].get("reasoning_tick"))
            print(f"  ✓ LLM calls: World A={llm_calls_A}, World B={llm_calls_B}")
        
        return self.generate_report(True, "COMPLETED")
    
    def generate_report(self, success, status):
        """Generate the experiment report."""
        report = {
            "EXPERIMENT": "10-Tick Controlled Field-to-Agent Behavioral Causality Test",
            "STATUS": status,
            "TIMESTAMP": datetime.now().isoformat(),
            "CONFIGURATION": {
                "total_ticks": self.TOTAL_TICKS,
                "seed": self.SEED,
                "llm_enabled": True,
                "reasoning_cooldown_ticks": 0,  # No cooldown
            "reasoning_cooldown_seconds": 0.0,  # No cooldown
            },
            "WORLD_A": {
                "entity_count": 1,
                "field_parameters": self.field_params_A,
                "final_state": self.trace_A[-1] if self.trace_A else None,
            },
            "WORLD_B": {
                "entity_count": 1,
                "field_parameters": self.field_params_B,
                "final_state": self.trace_B[-1] if self.trace_B else None,
            },
            "FIELD_INTERVENTION": {
                "parameter_changed": "c_nominal",
                "world_A_value": self.field_params_A["c_nominal"],
                "world_B_value": self.field_params_B["c_nominal"],
                "change_ratio": self.field_params_B["c_nominal"] / self.field_params_A["c_nominal"],
            },
            "FIRST_DIVERGENCE_TRACKER": self.divergence_tracker,
            "TRACE_A": self.trace_A,
            "TRACE_B": self.trace_B,
            "RESULT": self.determine_result(),
        }
        
        return report
    
    def determine_result(self):
        """Determine the experiment result based on divergence patterns."""
        # Check for behavioral divergence (action, state, or memory)
        behavioral_divergence = (
            self.divergence_tracker["action"] is not None or
            self.divergence_tracker["state"] is not None or
            self.divergence_tracker["memory"] is not None
        )
        
        # Check for cognitive divergence (LLM output, intent, goal)
        cognitive_divergence = (
            self.divergence_tracker["llm_output"] is not None or
            self.divergence_tracker["intent"] is not None
        )
        
        # Check for perception divergence
        perception_divergence = (
            self.divergence_tracker["agent_perception"] is not None
        )
        
        # Check for field divergence
        field_divergence = (
            self.divergence_tracker["spectral_observable"] is not None
        )
        
        if behavioral_divergence:
            return "BEHAVIORAL_FIELD_COUPLING_DETECTED"
        elif cognitive_divergence:
            return "FIELD_REACHES_COGNITION_BUT_NO_BEHAVIORAL_EFFECT_DETECTED"
        elif perception_divergence:
            return "FIELD_REACHES_PERCEPTION_BUT_NOT_COGNITION"
        elif field_divergence:
            return "FIELD_DIFFERENCE_ONLY"
        else:
            return "EXPERIMENT_INVALID"


def main():
    """Run the 500-tick field causality experiment."""
    experiment = FieldAgentBehavioralCausalityExperiment()
    
    try:
        report = experiment.run_experiment()
        
        # Save report
        report_path = "q_capability_experiment/field_agent_causality_500tick_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n{'='*80}")
        print("EXPERIMENT REPORT")
        print(f"{'='*80}")
        print(f"Status: {report['STATUS']}")
        print(f"Result: {report['RESULT']}")
        print(f"Field Intervention: c_nominal {report['FIELD_INTERVENTION']['world_A_value']} → {report['FIELD_INTERVENTION']['world_B_value']}")
        print(f"\nFirst Divergence Tracker:")
        for layer, divergence in report['FIRST_DIVERGENCE_TRACKER'].items():
            if divergence:
                print(f"  {layer}: Tick {divergence['tick']}")
            else:
                print(f"  {layer}: NONE THROUGH 500 TICKS")
        print(f"\nReport saved to: {report_path}")
        
        return 0 if report['RESULT'] != "EXPERIMENT_INVALID" else 1
        
    except Exception as e:
        print(f"\n✗ EXPERIMENT ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
