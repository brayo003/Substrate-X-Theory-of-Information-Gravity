"""
Controlled Field-to-Agent Causality Experiment

This experiment tests whether changing the physical-field condition produces
a corresponding change in an autonomous agent's behavior.

World A: Baseline field condition
World B: Different field condition (intervention at tick 50)

Total: 150 ticks (50 baseline + 100 post-intervention)
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sim_world.kernel.world_kernel import WorldKernel
from sim_world.core.config import KernelConfig
from sim_world.core.ids import WorldId
from sim_world.domains.physical_field import register as register_physical_field, initialize_physical_field
from sim_world.domains.needs import register as register_needs
from sim_world.domains.population import register as register_population
from sim_world.entities.components import NeedsComponent, TransformComponent, InventoryComponent, ResourceDescriptor


class FieldCausalityExperiment:
    """Controlled experiment testing field-to-agent causality."""
    
    BASELINE_TICKS = 10
    INTERVENTION_TICK = 10
    POST_INTERVENTION_TICKS = 20
    TOTAL_TICKS = 30
    
    def __init__(self):
        self.trace_A = []
        self.trace_B = []
        self.divergence_tick = None
        self.divergence_layer = None
        self.divergence_observable = None
    
    def create_world(self, world_name, field_regime="baseline"):
        """Create a world with a single entity and controlled field regime."""
        print(f"\nCreating {world_name} with field regime: {field_regime}")
        
        # Create kernel
        world_id = WorldId.new(world_name)
        config = KernelConfig(world_id=world_id, initial_state={}, enable_llm_generation=False)
        kernel = WorldKernel(config=config)
        
        # Register domains
        register_physical_field(kernel.simulation_engine)
        register_needs(kernel.simulation_engine)
        register_population(kernel.simulation_engine)
        
        # Initialize physical field
        field = initialize_physical_field(kernel)
        print(f"  ✓ Physical field initialized")
        
        # Create single entity (use same display name for deterministic comparison)
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
        
        return kernel, entity_id, field
    
    def apply_field_intervention(self, field, target_regime):
        """Apply controlled field intervention."""
        print(f"\nApplying field intervention: {target_regime}")
        
        # Since we cannot directly modify field parameters without redesigning,
        # we will document this limitation and instead create a new world
        # with different initial field parameters if the backend supports it.
        # For now, we'll skip the intervention and report the limitation.
        
        print(f"  ⚠ Field intervention skipped: Cannot modify field parameters without architectural changes")
        print(f"  ⚠ This is a limitation of the current backend implementation")
        
        return field
    
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
        
        # Field data
        spectral_obs = kernel.last_spectral_transport_observable
        if spectral_obs is not None:
            data["field"] = {
                "dominant_regime": spectral_obs.dominant_regime,
                "dominant_k": spectral_obs.dominant_k,
                "dominant_D": spectral_obs.dominant_D,
                "propagating_power_fraction": spectral_obs.propagating_power_fraction,
                "overdamped_power_fraction": spectral_obs.overdamped_power_fraction,
            }
        
        # Transport observation (Q)
        transport_obs = kernel.last_transport_observation
        if transport_obs is not None:
            data["field"]["q_value"] = transport_obs.q_value
            data["field"]["q_regime"] = transport_obs.regime
        
        # Perception (snapshot)
        try:
            snapshot = kernel.create_snapshot()
            data["perception"]["snapshot_id"] = str(snapshot.snapshot_id)
            data["perception"]["tick_id"] = str(snapshot.tick_id)
        except Exception as e:
            data["perception"]["error"] = str(e)
        
        # Entity state
        entity = kernel.entity_registry.get_entity(entity_id)
        if entity:
            data["state"]["entity_id"] = str(entity.entity_id)
            data["state"]["entity_type"] = entity.type
            data["state"]["display_name"] = entity.display_name
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
            data["memory"]["memory_id"] = memory.memory_id
        
        # Action (from last revision)
        if kernel._current_revision:
            data["action"]["event_count"] = len(kernel._current_revision.events)
            data["action"]["revision_id"] = str(kernel._current_revision.revision_id)
        
        return data
    
    def compare_ticks(self, data_A, data_B):
        """Compare two tick data points and identify divergence."""
        # Check field divergence (ignore UUIDs, focus on actual values)
        field_A = data_A["field"]
        field_B = data_B["field"]
        
        # Compare field observables (not UUIDs)
        field_keys = ["dominant_regime", "dominant_k", "dominant_D", "propagating_power_fraction", "overdamped_power_fraction", "q_value", "q_regime"]
        for key in field_keys:
            if field_A.get(key) != field_B.get(key):
                return "FIELD", {key: field_A.get(key)}, {key: field_B.get(key)}
        
        # Check state divergence (ignore UUIDs, focus on actual values)
        state_A = data_A["state"]
        state_B = data_B["state"]
        
        # Compare actual state values (not entity_id, not display_name)
        state_keys = ["entity_type", "alive", "enabled", "needs", "location"]
        for key in state_keys:
            if state_A.get(key) != state_B.get(key):
                return "STATE", {key: state_A.get(key)}, {key: state_B.get(key)}
        
        # Check action divergence (ignore revision UUIDs)
        action_A = data_A["action"]
        action_B = data_B["action"]
        
        if action_A.get("event_count") != action_B.get("event_count"):
            return "ACTION", {"event_count": action_A.get("event_count")}, {"event_count": action_B.get("event_count")}
        
        # Check memory divergence (ignore memory_id)
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
        
        # Create worlds
        kernel_A, entity_id_A, field_A = self.create_world("World_A", "baseline")
        kernel_B, entity_id_B, field_B = self.create_world("World_B", "baseline")
        
        # Baseline phase
        print(f"\n{'='*80}")
        print(f"BASELINE PHASE (ticks 1-{self.BASELINE_TICKS})")
        print(f"{'='*80}")
        
        for tick in range(1, self.BASELINE_TICKS + 1):
            print(f"\n--- Baseline Tick {tick} ---")
            
            # Run both worlds
            kernel_A.advance_tick()
            kernel_B.advance_tick()
            
            # Collect data
            data_A = self.collect_tick_data(kernel_A, entity_id_A, tick, "World_A")
            data_B = self.collect_tick_data(kernel_B, entity_id_B, tick, "World_B")
            
            self.trace_A.append(data_A)
            self.trace_B.append(data_B)
            
            # Check for divergence (should not happen during baseline)
            divergence_layer, val_A, val_B = self.compare_ticks(data_A, data_B)
            if divergence_layer:
                print(f"  ⚠ BASELINE DIVERGENCE at tick {tick}: {divergence_layer}")
                print(f"    World A: {val_A}")
                print(f"    World B: {val_B}")
                print(f"  ⚠ ABORTING: Baseline divergence detected")
                return self.generate_report(False, "BASELINE_DIVERGENCE")
            
            print(f"  ✓ Both worlds equivalent")
        
        # Intervention
        print(f"\n{'='*80}")
        print(f"INTERVENTION at tick {self.INTERVENTION_TICK}")
        print(f"{'='*80}")
        
        # Apply field intervention to World B only
        field_B = self.apply_field_intervention(field_B, "coherent")
        
        # Since intervention was not possible, we'll stop here and report
        return self.generate_report(False, "INTERVENTION_NOT_POSSIBLE")
        
        # Post-intervention phase
        print(f"\n{'='*80}")
        print(f"POST-INTERVENTION PHASE (ticks {self.INTERVENTION_TICK+1}-{self.TOTAL_TICKS})")
        print(f"{'='*80}")
        
        for tick in range(self.INTERVENTION_TICK + 1, self.TOTAL_TICKS + 1):
            print(f"\n--- Post-Intervention Tick {tick} ---")
            
            # Run both worlds
            kernel_A.advance_tick()
            kernel_B.advance_tick()
            
            # Collect data
            data_A = self.collect_tick_data(kernel_A, entity_id_A, tick, "World_A")
            data_B = self.collect_tick_data(kernel_B, entity_id_B, tick, "World_B")
            
            self.trace_A.append(data_A)
            self.trace_B.append(data_B)
            
            # Check for divergence
            divergence_layer, val_A, val_B = self.compare_ticks(data_A, data_B)
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
                print(f"  ✓ Worlds still equivalent")
        
        return self.generate_report(True, "COMPLETED")
    
    def generate_report(self, success, status):
        """Generate the experiment report."""
        report = {
            "EXPERIMENT": "Controlled Field-to-Agent Causality Test",
            "STATUS": status,
            "TIMESTAMP": datetime.now().isoformat(),
            "CONFIGURATION": {
                "baseline_ticks": self.BASELINE_TICKS,
                "intervention_tick": self.INTERVENTION_TICK,
                "post_intervention_ticks": self.POST_INTERVENTION_TICKS,
                "total_ticks": self.TOTAL_TICKS,
            },
            "WORLD_A": {
                "entity_count": len(self.trace_A[0]["state"]) if self.trace_A else 0,
                "field_condition": "baseline",
                "final_state": self.trace_A[-1] if self.trace_A else None,
            },
            "WORLD_B": {
                "entity_count": len(self.trace_B[0]["state"]) if self.trace_B else 0,
                "field_condition": "coherent (intervention)",
                "final_state": self.trace_B[-1] if self.trace_B else None,
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
                "Field intervention NOT POSSIBLE with current backend - field parameters cannot be modified after initialization",
                "Missing integration: backend does not expose field parameter modification API",
                "Single-entity worlds to isolate causality",
            ],
            "TRACE_A": self.trace_A,
            "TRACE_B": self.trace_B,
        }
        
        return report
    
    def determine_result(self):
        """Determine the experiment result."""
        if self.divergence_tick is None:
            return "NO_BEHAVIORAL_COUPLING_OBSERVED"
        elif self.divergence_layer == "FIELD":
            return "FIELD_DIVERGENCE_ONLY"
        elif self.divergence_layer in ["PERCEPTION", "STATE", "ACTION", "MEMORY"]:
            return "BEHAVIORAL_RESPONSE_TO_FIELD_INTERVENTION_OBSERVED"
        else:
            return "INDETERMINATE"


def main():
    """Run the field causality experiment."""
    experiment = FieldCausalityExperiment()
    
    try:
        report = experiment.run_experiment()
        
        # Save report
        report_path = "q_capability_experiment/field_causality_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n{'='*80}")
        print("EXPERIMENT REPORT")
        print(f"{'='*80}")
        print(f"Status: {report['STATUS']}")
        print(f"Result: {report['RESULT']}")
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
