"""
Main Kernel Spectral Transport Integration Test

This test validates that the SpectralTransportObservable actually reaches
the main kernel execution path through the physical field domain.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sim_world.kernel.world_kernel import WorldKernel
from sim_world.core.config import KernelConfig
from sim_world.core.ids import WorldId


def test_kernel_spectral_observable_integration():
    """Test that spectral transport observable reaches the kernel."""
    print("="*80)
    print("KERNEL SPECTRAL TRANSPORT INTEGRATION TEST")
    print("="*80)
    
    # Create kernel with physical field domain
    world_id = WorldId.new("test_world")
    config = KernelConfig(world_id=world_id, initial_state={})
    kernel = WorldKernel(config=config)
    
    # Register physical field domain with simulation engine
    from sim_world.domains.physical_field import register as register_physical_field
    register_physical_field(kernel.simulation_engine)
    print("✓ Physical field domain registered with simulation engine")
    
    # Initialize physical field using kernel's method (per-world isolation)
    kernel.initialize_physical_field(c_nominal=1.0, tau_nominal=1.0)
    print(f"✓ Physical field initialized: {kernel._physical_field}")
    
    # Run a few ticks to generate spectral observables
    print("\nRunning 10 ticks to generate spectral observables...")
    for i in range(10):
        revision = kernel.advance_tick()
        print(f"  Tick {i+1}: revision={revision.revision_id.value}")
    
    # Check if spectral observable is available
    spectral_obs = kernel.last_spectral_transport_observable
    print(f"\n✓ Last spectral transport observable: {spectral_obs}")
    
    # Debug: check the kernel state
    print("\nDebug: Checking kernel state structure...")
    state = kernel.current_state
    print(f"State keys: {list(state.keys())}")
    
    if "physical_field" in state:
        print(f"Physical field keys: {list(state['physical_field'].keys())}")
        if "spectral_transport_observable" in state["physical_field"]:
            print(f"Spectral observable data: {state['physical_field']['spectral_transport_observable']}")
    
    if spectral_obs is None:
        print("✗ FAILED: Spectral transport observable not available at kernel")
        return False
    
    # Validate spectral observable structure
    required_fields = [
        'physical_time',
        'dominant_k',
        'dominant_D',
        'dominant_regime',
        'propagating_power_fraction',
        'overdamped_power_fraction',
        'critical_power_fraction',
        'weighted_D',
        'spectral_entropy',
        'c_nominal',
        'tau_nominal',
        'k_critical',
    ]
    
    print("\nValidating spectral observable structure:")
    for field_name in required_fields:
        if not hasattr(spectral_obs, field_name):
            print(f"✗ FAILED: Missing field: {field_name}")
            return False
        value = getattr(spectral_obs, field_name)
        print(f"  ✓ {field_name}: {value}")
    
    # Validate numerical consistency
    print("\nValidating numerical consistency:")
    assert spectral_obs.propagating_power_fraction >= 0.0, "f_prop must be >= 0"
    assert spectral_obs.overdamped_power_fraction >= 0.0, "f_over must be >= 0"
    assert spectral_obs.critical_power_fraction >= 0.0, "f_crit must be >= 0"
    total = (spectral_obs.propagating_power_fraction + 
             spectral_obs.overdamped_power_fraction + 
             spectral_obs.critical_power_fraction)
    assert abs(total - 1.0) < 0.01, f"Power fractions must sum to 1.0, got {total}"
    print(f"  ✓ Power fractions sum to {total:.4f}")
    
    assert spectral_obs.spectral_entropy >= 0.0, "Spectral entropy must be >= 0"
    print(f"  ✓ Spectral entropy: {spectral_obs.spectral_entropy:.4f}")
    
    assert spectral_obs.k_critical > 0.0, "k_critical must be > 0"
    print(f"  ✓ k_critical: {spectral_obs.k_critical:.4f}")
    
    print("\n✓ KERNEL SPECTRAL TRANSPORT INTEGRATION TEST PASSED")
    return True


def test_kernel_transport_observation_preserved():
    """Test that the existing transport observation system is preserved."""
    print("\n" + "="*80)
    print("KERNEL TRANSPORT OBSERVATION PRESERVATION TEST")
    print("="*80)
    
    # Create kernel
    world_id = WorldId.new("test_world")
    config = KernelConfig(world_id=world_id, initial_state={})
    kernel = WorldKernel(config=config)
    
    # Register physical field domain with simulation engine
    from sim_world.domains.physical_field import register as register_physical_field
    register_physical_field(kernel.simulation_engine)
    
    # Initialize physical field using kernel's method (per-world isolation)
    kernel.initialize_physical_field(c_nominal=1.0, tau_nominal=1.0)
    
    # Run a few ticks
    print("Running 5 ticks...")
    for i in range(5):
        revision = kernel.advance_tick()
    
    # Check that transport observation is still available
    transport_obs = kernel.last_transport_observation
    print(f"✓ Transport observation preserved: {transport_obs}")
    
    if transport_obs is None:
        print("✗ FAILED: Transport observation not available")
        return False
    
    # Check that spectral observable is also available
    spectral_obs = kernel.last_spectral_transport_observable
    print(f"✓ Spectral transport observable available: {spectral_obs}")
    
    if spectral_obs is None:
        print("✗ FAILED: Spectral transport observable not available")
        return False
    
    print("\n✓ Both transport systems coexist correctly")
    return True


def main():
    """Run all kernel integration tests."""
    print("="*80)
    print("MAIN KERNEL SPECTRAL TRANSPORT INTEGRATION TEST SUITE")
    print("="*80)
    
    tests = [
        test_kernel_spectral_observable_integration,
        test_kernel_transport_observation_preserved,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n✓ ALL KERNEL INTEGRATION TESTS PASSED")
        return 0
    else:
        print(f"\n✗ {failed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    exit(main())
