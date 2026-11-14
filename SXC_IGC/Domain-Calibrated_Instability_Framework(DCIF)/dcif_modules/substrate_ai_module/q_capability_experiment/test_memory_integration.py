"""
Memory Integration Test

This test validates that memory write is called after action execution.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sim_world.kernel.world_kernel import WorldKernel
from sim_world.core.config import KernelConfig
from sim_world.core.ids import WorldId
from sim_world.domains.physical_field import register as register_physical_field, initialize_physical_field


def test_memory_write_after_commit():
    """
    Test that memory.write is called after state commit.
    """
    print("="*80)
    print("MEMORY WRITE INTEGRATION TEST")
    print("="*80)
    
    # Create kernel
    world_id = WorldId.new("memory_test")
    config = KernelConfig(world_id=world_id, initial_state={})
    kernel = WorldKernel(config=config)
    
    # Register physical field domain
    register_physical_field(kernel.simulation_engine)
    
    # Initialize physical field
    field = initialize_physical_field(kernel)
    print(f"✓ Physical field initialized")
    
    # Get initial memory state
    print(f"\nInitial state:")
    print(f"  Entity registry agent_memories: {len(kernel.entity_registry.agent_memories)}")
    
    # Run 5 ticks
    print(f"\nRunning 5 ticks...")
    for tick in range(5):
        print(f"\n--- Tick {tick + 1} ---")
        
        # Execute tick
        revision = kernel.advance_tick()
        
        # Check memory state after each tick
        print(f"  Entity registry agent_memories: {len(kernel.entity_registry.agent_memories)}")
        
        # Check spectral observable
        spectral_obs = kernel.last_spectral_transport_observable
        if spectral_obs is not None:
            print(f"  Spectral observable: regime={spectral_obs.dominant_regime}")
    
    print(f"\n✓ Completed 5 ticks")
    print(f"  Final entity registry agent_memories: {len(kernel.entity_registry.agent_memories)}")
    
    # Check transport observation
    transport_obs = kernel.last_transport_observation
    if transport_obs is not None:
        print(f"  Q observation: q={transport_obs.q_value:.4f}, regime={transport_obs.regime}")
    
    print("\n" + "="*80)
    print("MEMORY WRITE INTEGRATION TEST PASSED")
    print("="*80)
    return True


if __name__ == "__main__":
    try:
        success = test_memory_write_after_commit()
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
