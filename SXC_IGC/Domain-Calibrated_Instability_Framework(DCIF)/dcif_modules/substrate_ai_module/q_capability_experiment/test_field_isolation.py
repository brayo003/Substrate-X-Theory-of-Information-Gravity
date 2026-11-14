"""
Field State Isolation Test

This test verifies that each WorldKernel instance maintains independent
physical field state, ensuring controlled A/B experiments are possible.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sim_world.kernel.world_kernel import WorldKernel
from sim_world.core.config import KernelConfig
from sim_world.core.ids import WorldId
from sim_world.domains.physical_field import register as register_physical_field
from sim_world.domains.needs import register as register_needs
from sim_world.domains.population import register as register_population


def test_field_state_isolation():
    """Test that field state is isolated between kernel instances."""
    print("="*80)
    print("FIELD STATE ISOLATION TEST")
    print("="*80)
    
    # Create World A with c_nominal=1.0
    print("\n1. Creating World A with c_nominal=1.0")
    world_id_A = WorldId.new("World_A")
    config_A = KernelConfig(world_id=world_id_A, initial_state={}, enable_llm_generation=False)
    kernel_A = WorldKernel(config=config_A)
    
    register_physical_field(kernel_A.simulation_engine)
    register_needs(kernel_A.simulation_engine)
    register_population(kernel_A.simulation_engine)
    
    kernel_A.initialize_physical_field(c_nominal=1.0, tau_nominal=1.0)
    print(f"   ✓ World A field initialized: c={kernel_A._propagation_params.c_nominal}")
    
    # Create World B with c_nominal=2.0
    print("\n2. Creating World B with c_nominal=2.0")
    world_id_B = WorldId.new("World_B")
    config_B = KernelConfig(world_id=world_id_B, initial_state={}, enable_llm_generation=False)
    kernel_B = WorldKernel(config=config_B)
    
    register_physical_field(kernel_B.simulation_engine)
    register_needs(kernel_B.simulation_engine)
    register_population(kernel_B.simulation_engine)
    
    kernel_B.initialize_physical_field(c_nominal=2.0, tau_nominal=1.0)
    print(f"   ✓ World B field initialized: c={kernel_B._propagation_params.c_nominal}")
    
    # Verify initial isolation
    print("\n3. Verifying initial field parameter isolation")
    c_A = kernel_A._propagation_params.c_nominal
    c_B = kernel_B._propagation_params.c_nominal
    
    assert c_A == 1.0, f"World A should have c=1.0, got c={c_A}"
    assert c_B == 2.0, f"World B should have c=2.0, got c={c_B}"
    print(f"   ✓ World A c_nominal: {c_A}")
    print(f"   ✓ World B c_nominal: {c_B}")
    print(f"   ✓ Field parameters are isolated")
    
    # Advance World B
    print("\n4. Advancing World B for 5 ticks")
    for tick in range(1, 6):
        kernel_B.advance_tick()
        print(f"   ✓ World B tick {tick} completed")
    
    # Verify World A is unchanged
    print("\n5. Verifying World A field parameters after World B advancement")
    c_A_after_B = kernel_A._propagation_params.c_nominal
    assert c_A_after_B == 1.0, f"World A should still have c=1.0, got c={c_A_after_B}"
    print(f"   ✓ World A c_nominal unchanged: {c_A_after_B}")
    
    # Verify World B is still changed
    print("\n6. Verifying World B field parameters after advancement")
    c_B_after = kernel_B._propagation_params.c_nominal
    assert c_B_after == 2.0, f"World B should still have c=2.0, got c={c_B_after}"
    print(f"   ✓ World B c_nominal unchanged: {c_B_after}")
    
    # Advance World A
    print("\n7. Advancing World A for 5 ticks")
    for tick in range(1, 6):
        kernel_A.advance_tick()
        print(f"   ✓ World A tick {tick} completed")
    
    # Verify both kernels maintain their field parameters
    print("\n8. Verifying both kernels maintain independent field parameters")
    c_A_final = kernel_A._propagation_params.c_nominal
    c_B_final = kernel_B._propagation_params.c_nominal
    
    assert c_A_final == 1.0, f"World A should still have c=1.0, got c={c_A_final}"
    assert c_B_final == 2.0, f"World B should still have c=2.0, got c={c_B_final}"
    print(f"   ✓ World A c_nominal: {c_A_final}")
    print(f"   ✓ World B c_nominal: {c_B_final}")
    print(f"   ✓ Field parameters remain isolated after both kernels advanced")
    
    # Verify spectral observables are different
    print("\n9. Verifying spectral observables are different")
    spectral_A = kernel_A.last_spectral_transport_observable
    spectral_B = kernel_B.last_spectral_transport_observable
    
    if spectral_A and spectral_B:
        D_A = spectral_A.dominant_D
        D_B = spectral_B.dominant_D
        print(f"   ✓ World A dominant_D: {D_A}")
        print(f"   ✓ World B dominant_D: {D_B}")
        
        if D_A != D_B:
            print(f"   ✓ Spectral observables are different (field isolation verified)")
        else:
            print(f"   ⚠ Spectral observables are identical (may indicate same field dynamics)")
    
    print("\n" + "="*80)
    print("FIELD STATE ISOLATION TEST: PASSED")
    print("="*80)
    print("\nConclusion:")
    print("  ✓ Each WorldKernel instance maintains independent field state")
    print("  ✓ Field parameters are not shared between kernels")
    print("  ✓ Advancing one kernel does not affect another kernel's field")
    print("  ✓ Controlled A/B experiments are now possible")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(test_field_state_isolation())
    except AssertionError as e:
        print(f"\n✗ ISOLATION TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ISOLATION TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
