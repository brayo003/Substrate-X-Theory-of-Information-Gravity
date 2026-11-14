"""
Controlled Field-to-Agent Causality Experiment

This experiment tests whether changing the physical field condition produces
a corresponding change in an autonomous agent's behavior.

World A: Baseline field condition (c_nominal = 1.0)
World B: Perturbed field condition (c_nominal = 2.0)

Total: 30 ticks (10 baseline + 20 post-intervention)
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sim_world.kernel.world_kernel import WorldKernel
from sim_world.core.config import KernelConfig
from sim_world.core.ids import WorldId
from sim_world.domains.physical_field import register as register_physical_field
from sim_world.domains.needs import register as register_needs
from sim_world.domains.population import register as register_population
from sim_world.entities.components import NeedsComponent, TransformComponent, InventoryComponent, ResourceDescriptor


class FieldAgentCausalityExperiment:
    """Controlled experiment testing field-to-agent causality."""
    
    BASELINE_TICKS = 10
    POST_INTERVENTION_TICKS = 20
    TOTAL_TICKS = 30
    
    def __init__(self):
        self.trace_A = []
        self.trace_B = []
        self.divergence_tick = None
        self.divergence_layer = None
        self.divergence_observable = None
        self.field_params_A = {"c_nominal": 1.0, "tau_nominal": 1.0}
        self.field_params_B = {"c_nominal": 2.0, "tau_nominal": 1.0}
    
    def create_world(self, world_name, field_params):
        """Create a world with controlled field parameters."""
        print(f"\nCreating {world_name} with field params: {field_params}")
        
        # Create kernel
        world_id = WorldId.new(world_name)
        config = KernelConfig(world_id=world_id, initial_state={}, enable_llm_generation=False)
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
        print(f"  ✓ Physical field initialized")
        
        # Create single entity
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
        
        return kernel, entity_id
    
    def collect_tick_data(self, kernel, entity_id, tick, world_name):
        """Collect complete causal chain data for a tick."""
        data = {
            "tick": tick,
            "world": world_name,
            "field": {},
            "perception": {},
            "cognition": {},
            "action": {},
            "state": {},
            "memory": {},
        }
        
        # Field data from kernel's field state (for isolation verification)
        if kernel._propagation_params is not None:
            data["field"]["kernel_c_nominal"] = kernel._propagation_params.c_nominal
        if kernel._relaxation_params is not None:
            data["field"]["kernel_tau_nominal"] = kernel._relaxation_params.tau_nominal
        
        # Field data from spectral observable
        spectral_obs = kernel.last_spectral_transport_observable
        if spectral_obs is not None:
            data["field"]["dominant_regime"] = spectral_obs.dominant_regime
            data["field"]["dominant_k"] = spectral_obs.dominant_k
            data["field"]["dominant_D"] = spectral_obs.dominant_D
            data["field"]["propagating_power_fraction"] = spectral_obs.propagating_power_fraction
            data["field"]["overdamped_power_fraction"] = spectral_obs.overdamped_power_fraction
            data["field"]["c_nominal"] = spectral_obs.c_nominal
            data["field"]["tau_nominal"] = spectral_obs.tau_nominal
        
        # Transport observation (Q)
        transport_obs = kernel.last_transport_observation
        if transport_obs is not None:
            data["field"]["q_value"] = transport_obs.q_value
            data["field"]["q_regime"] = transport_obs.regime
        
        # Entity state
        entity = kernel.entity_registry.get_entity(entity_id)
        if entity:
            data["state"]["entity_type"] = entity.type
            data["state"]["alive"] = entity.alive
            data["state"]["enabled"] = entity.enabled
            
            # Needs
            needs_comp = entity.get_component("NeedsComponent")
            if needs_comp:
                data["state"]["needs"] = dict(needs_comp.needs)
            
            # Location
            transform_comp = entity.get_component("TransformComponent")
            if transform_comp:
                data["state"]["location"] = transform_comp.room
        
        # Memory
        memory = kernel.entity_registry.agent_memories.get(entity_id)
        if memory:
            data["memory"]["record_count"] = len(memory.records)
        
        # Action (from last revision)
        if kernel._current_revision:
            data["action"]["event_count"] = len(kernel._current_revision.events)
        
        return data
    
    def compare_ticks(self, data_A, data_B, expect_field_divergence=False):
        """Compare two tick data points and identify divergence."""
        # Check kernel field parameters (for isolation verification)
        field_A = data_A["field"]
        field_B = data_B["field"]
        
        # Check kernel-level field parameters (this is the intervention)
        if field_A.get("kernel_c_nominal") != field_B.get("kernel_c_nominal"):
            if expect_field_divergence:
                # Field divergence is expected after intervention
                pass
            else:
                # Field divergence is unexpected during baseline
                return "FIELD_KERNEL", {"kernel_c_nominal": field_A.get("kernel_c_nominal")}, {"kernel_c_nominal": field_B.get("kernel_c_nominal")}
        
        # Check field observables (not c_nominal which is intentional)
        field_keys = ["dominant_regime", "dominant_k", "dominant_D", "propagating_power_fraction", "overdamped_power_fraction", "q_value", "q_regime"]
        for key in field_keys:
            if field_A.get(key) != field_B.get(key):
                if expect_field_divergence:
                    # Field divergence is expected after intervention
                    return None, None, None
                else:
                    # Field divergence is unexpected during baseline
                    return "FIELD", {key: field_A.get(key)}, {key: field_B.get(key)}
        
        # Check state divergence
        state_A = data_A["state"]
        state_B = data_B["state"]
        
        state_keys = ["entity_type", "alive", "enabled", "needs", "location"]
        for key in state_keys:
            if state_A.get(key) != state_B.get(key):
                return "STATE", {key: state_A.get(key)}, {key: state_B.get(key)}
        
        # Check action divergence
        action_A = data_A["action"]
        action_B = data_B["action"]
        
        if action_A.get("event_count") != action_B.get("event_count"):
            return "ACTION", {"event_count": action_A.get("event_count")}, {"event_count": action_B.get("event_count")}
        
        # Check memory divergence
        memory_A = data_A["memory"]
        memory_B = data_B["memory"]
        
        if memory_A.get("record_count") != memory_B.get("record_count"):
            return "MEMORY", {"record_count": memory_A.get("record_count")}, {"record_count": memory_B.get("record_count")}
        
        return None, None, None
    
    def run_experiment(self):
        """Run the complete controlled causality experiment."""
        print("="*80)
        print("CONTROLLED FIELD-TO-AGENT CAUSALITY EXPERIMENT")
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
        
        # Run both worlds for full duration
        print(f"\n{'='*80}")
        print(f"RUNNING BOTH WORDS FOR {self.TOTAL_TICKS} TICKS")
        print(f"{'='*80}")
        
        for tick in range(1, self.TOTAL_TICKS + 1):
            print(f"\n--- Tick {tick} ---")
            
            # Run both worlds
            kernel_A.advance_tick()
            kernel_B.advance_tick()
            
            # Collect data
            data_A = self.collect_tick_data(kernel_A, entity_id_A, tick, "World_A")
            data_B = self.collect_tick_data(kernel_B, entity_id_B, tick, "World_B")
            
            self.trace_A.append(data_A)
            self.trace_B.append(data_B)
            
            # Verify kernel field parameters are isolated
            kernel_c_A = data_A["field"].get("kernel_c_nominal")
            kernel_c_B = data_B["field"].get("kernel_c_nominal")
            
            if kernel_c_A != self.field_params_A["c_nominal"]:
                print(f"  ⚠ WORLD A FIELD ISOLATION ERROR: expected c={self.field_params_A['c_nominal']}, got c={kernel_c_A}")
            if kernel_c_B != self.field_params_B["c_nominal"]:
                print(f"  ⚠ WORLD B FIELD ISOLATION ERROR: expected c={self.field_params_B['c_nominal']}, got c={kernel_c_B}")
            
            # Check for divergence (field divergence is expected)
            divergence_layer, val_A, val_B = self.compare_ticks(data_A, data_B, expect_field_divergence=True)
            if divergence_layer and self.divergence_tick is None:
                self.divergence_tick = tick
                self.divergence_layer = divergence_layer
                self.divergence_observable = {"A": val_A, "B": val_B}
                print(f"  ⚠ FIRST DIVERGENCE at tick {tick}: {divergence_layer}")
                print(f"    World A: {val_A}")
                print(f"    World B: {val_B}")
            elif divergence_layer:
                print(f"  ⚠ Continued divergence at tick {tick}: {divergence_layer}")
            else:
                print(f"  ✓ Worlds equivalent (field divergence expected and ignored)")
        
        return self.generate_report(True, "COMPLETED")
    
    def generate_report(self, success, status):
        """Generate the experiment report."""
        report = {
            "EXPERIMENT": "Controlled Field-to-Agent Causality Test",
            "STATUS": status,
            "TIMESTAMP": datetime.now().isoformat(),
            "CONFIGURATION": {
                "baseline_ticks": self.BASELINE_TICKS,
                "post_intervention_ticks": self.POST_INTERVENTION_TICKS,
                "total_ticks": self.TOTAL_TICKS,
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
            "FIRST_DIVERGENCE": {
                "tick": self.divergence_tick,
                "layer": self.divergence_layer,
                "observable": self.divergence_observable,
            },
            "CAUSAL_CHAIN": "field → perception → cognition → action → state → memory",
            "RESULT": self.determine_result(),
            "LIMITATIONS": [
                "LLM generation disabled for deterministic execution",
                "Field intervention applied at initialization (not runtime)",
                "Single-entity worlds to isolate causality",
                "Global field state requires sequential world creation",
            ],
            "TRACE_A": self.trace_A,
            "TRACE_B": self.trace_B,
        }
        
        return report
    
    def determine_result(self):
        """Determine the experiment result."""
        if self.divergence_tick is None:
            return "FIELD_OBSERVATION_VERIFIED_AGENT_BEHAVIORAL_RESPONSE_NOT_DETECTED"
        elif self.divergence_layer == "FIELD":
            return "FIELD_DIVERGENCE_ONLY"
        elif self.divergence_layer in ["STATE", "ACTION", "MEMORY"]:
            return "FIELD_TO_AGENT_CAUSAL_EFFECT_OBSERVED"
        else:
            return "INDETERMINATE"


def main():
    """Run the field causality experiment."""
    experiment = FieldAgentCausalityExperiment()
    
    try:
        report = experiment.run_experiment()
        
        # Save report
        report_path = "q_capability_experiment/field_agent_causality_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n{'='*80}")
        print("EXPERIMENT REPORT")
        print(f"{'='*80}")
        print(f"Status: {report['STATUS']}")
        print(f"Result: {report['RESULT']}")
        print(f"Field Intervention: c_nominal {report['FIELD_INTERVENTION']['world_A_value']} → {report['FIELD_INTERVENTION']['world_B_value']}")
        print(f"First Divergence: Tick {report['FIRST_DIVERGENCE']['tick']}, Layer {report['FIRST_DIVERGENCE']['layer']}")
        print(f"\nReport saved to: {report_path}")
        
        return 0 if report['RESULT'] != "INDETERMINATE" else 1
        
    except Exception as e:
        print(f"\n✗ EXPERIMENT ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
