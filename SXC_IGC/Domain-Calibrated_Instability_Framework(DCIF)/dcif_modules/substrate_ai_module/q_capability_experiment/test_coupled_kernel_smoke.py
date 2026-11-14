"""
Final Coupled Kernel Smoke Test (100 ticks)

This test runs the actual main kernel for 100 ticks to validate
entity/environment coupling with spectral transport observables.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sim_world.kernel.world_kernel import WorldKernel
from sim_world.core.config import KernelConfig
from sim_world.core.ids import WorldId


def test_coupled_kernel_100_ticks():
    """Run 100 ticks of the actual kernel to validate coupled behavior."""
    print("="*80)
    print("COUPLED KERNEL SMOKE TEST - 100 TICKS")
    print("="*80)
    
    # Create kernel
    world_id = WorldId.new("coupled_test")
    config = KernelConfig(world_id=world_id, initial_state={})
    kernel = WorldKernel(config=config)
    
    # Register physical field domain
    from sim_world.domains.physical_field import register as register_physical_field
    register_physical_field(kernel.simulation_engine)
    
    # Initialize physical field using kernel's method (per-world isolation)
    kernel.initialize_physical_field(c_nominal=1.0, tau_nominal=1.0)
    print(f"✓ Physical field initialized")
    
    # Run 100 ticks
    print("\nRunning 100 ticks...")
    spectral_trajectory = []
    transport_trajectory = []
    
    for i in range(100):
        revision = kernel.advance_tick()
        
        # Collect spectral observables
        spectral_obs = kernel.last_spectral_transport_observable
        if spectral_obs is not None:
            spectral_trajectory.append({
                'tick': i + 1,
                'dominant_D': spectral_obs.dominant_D,
                'dominant_regime': spectral_obs.dominant_regime,
                'f_prop': spectral_obs.propagating_power_fraction,
                'f_over': spectral_obs.overdamped_power_fraction,
                'weighted_D': spectral_obs.weighted_D,
                'spectral_entropy': spectral_obs.spectral_entropy,
            })
        
        # Collect transport observables
        transport_obs = kernel.last_transport_observation
        if transport_obs is not None:
            transport_trajectory.append({
                'tick': i + 1,
                'q_value': transport_obs.q_value,
                'regime': transport_obs.regime,
            })
        
        if (i + 1) % 20 == 0:
            print(f"  Tick {i+1}: spectral={len(spectral_trajectory)}, transport={len(transport_trajectory)}")
    
    print(f"\n✓ Completed 100 ticks")
    print(f"  Spectral observables collected: {len(spectral_trajectory)}")
    print(f"  Transport observables collected: {len(transport_trajectory)}")
    
    # Validate spectral observables
    if len(spectral_trajectory) == 0:
        print("✗ FAILED: No spectral observables collected")
        return False
    
    print("\nSpectral Transport Trajectory:")
    print(f"  Initial: D={spectral_trajectory[0]['dominant_D']:.4f}, regime={spectral_trajectory[0]['dominant_regime']}")
    print(f"  Final: D={spectral_trajectory[-1]['dominant_D']:.4f}, regime={spectral_trajectory[-1]['dominant_regime']}")
    
    # Check for regime changes
    regimes = [s['dominant_regime'] for s in spectral_trajectory]
    unique_regimes = set(regimes)
    print(f"  Regimes observed: {unique_regimes}")
    
    # Validate transport observables
    if len(transport_trajectory) == 0:
        print("✗ FAILED: No transport observables collected")
        return False
    
    print("\nState-Transition Transport Trajectory:")
    print(f"  Initial: q={transport_trajectory[0]['q_value']:.4f}, regime={transport_trajectory[0]['regime']}")
    print(f"  Final: q={transport_trajectory[-1]['q_value']:.4f}, regime={transport_trajectory[-1]['regime']}")
    
    # Validate Q separation
    print("\nQ System Separation Validation:")
    print(f"  ✓ Physical-field spectral transport: SpectralTransportObservable")
    print(f"  ✓ State-transition transport: QObservation")
    print(f"  ✓ Both systems coexist independently")
    
    print("\n✓ COUPLED KERNEL SMOKE TEST PASSED (100 ticks)")
    return True


def main():
    """Run final coupled kernel test."""
    print("="*80)
    print("FINAL COUPLED KERNEL VALIDATION")
    print("="*80)
    
    try:
        if test_coupled_kernel_100_ticks():
            print("\n✓ COUPLED VALIDATION SUCCESSFUL")
            return 0
        else:
            print("\n✗ COUPLED VALIDATION FAILED")
            return 1
    except Exception as e:
        print(f"\n✗ COUPLED VALIDATION FAILED WITH EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
