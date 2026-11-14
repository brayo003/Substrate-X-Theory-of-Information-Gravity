"""
Main Kernel Smoke Test (≤100 ticks)

This test runs the actual main kernel for a bounded number of ticks to verify
that the spectral transport observable integration works in a real execution.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sim_world.kernel.world_kernel import WorldKernel
from sim_world.core.config import KernelConfig
from sim_world.core.ids import WorldId


def test_kernel_smoke_50_ticks():
    """Run 50 ticks of the actual kernel to verify spectral observable integration."""
    print("="*80)
    print("KERNEL SMOKE TEST - 50 TICKS")
    print("="*80)
    
    # Create kernel
    world_id = WorldId.new("smoke_test")
    config = KernelConfig(world_id=world_id, initial_state={})
    kernel = WorldKernel(config=config)
    
    # Register physical field domain
    from sim_world.domains.physical_field import register as register_physical_field
    register_physical_field(kernel.simulation_engine)
    
    # Initialize physical field
    from sim_world.domains.physical_field import initialize_physical_field
    field = initialize_physical_field(kernel)
    print(f"✓ Physical field initialized")
    
    # Run 50 ticks
    print("\nRunning 50 ticks...")
    spectral_observables = []
    transport_observables = []
    
    for i in range(50):
        revision = kernel.advance_tick()
        
        # Collect spectral observables
        spectral_obs = kernel.last_spectral_transport_observable
        if spectral_obs is not None:
            spectral_observables.append(spectral_obs)
        
        # Collect transport observables
        transport_obs = kernel.last_transport_observation
        if transport_obs is not None:
            transport_observables.append(transport_obs)
        
        if (i + 1) % 10 == 0:
            print(f"  Tick {i+1}: spectral={spectral_obs is not None}, transport={transport_obs is not None}")
    
    print(f"\n✓ Completed 50 ticks")
    print(f"  Spectral observables collected: {len(spectral_observables)}")
    print(f"  Transport observables collected: {len(transport_observables)}")
    
    # Validate spectral observables
    if len(spectral_observables) == 0:
        print("✗ FAILED: No spectral observables collected")
        return False
    
    print("\nValidating spectral observables:")
    last_spectral = spectral_observables[-1]
    print(f"  ✓ Last observable: dominant_regime={last_spectral.dominant_regime}")
    print(f"  ✓ dominant_D: {last_spectral.dominant_D:.4f}")
    print(f"  ✓ propagating_power_fraction: {last_spectral.propagating_power_fraction:.4f}")
    print(f"  ✓ overdamped_power_fraction: {last_spectral.overdamped_power_fraction:.4f}")
    
    # Validate transport observables still work
    if len(transport_observables) == 0:
        print("✗ FAILED: No transport observables collected")
        return False
    
    print("\nValidating transport observables:")
    last_transport = transport_observables[-1]
    print(f"  ✓ Last transport observation: regime={last_transport.regime}")
    print(f"  ✓ q_value: {last_transport.q_value:.4f}")
    
    print("\n✓ KERNEL SMOKE TEST PASSED (50 ticks)")
    return True


def main():
    """Run kernel smoke test."""
    print("="*80)
    print("MAIN KERNEL SMOKE TEST")
    print("="*80)
    
    try:
        if test_kernel_smoke_50_ticks():
            print("\n✓ SMOKE TEST SUCCESSFUL")
            return 0
        else:
            print("\n✗ SMOKE TEST FAILED")
            return 1
    except Exception as e:
        print(f"\n✗ SMOKE TEST FAILED WITH EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
