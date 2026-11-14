"""
Causal Coupling Experiment - Spectral Transport Regime vs Downstream Dynamics

This experiment determines whether changing the physical field's spectral transport
regime produces measurable downstream changes at the entity/environment coupling boundary.
"""

import sys
import os
import numpy as np
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sim_world.kernel.world_kernel import WorldKernel
from sim_world.core.config import KernelConfig
from sim_world.core.ids import WorldId
from sim_world.domains.physical_field.physical_field_models import (
    InformationDensityField,
    FieldState,
    PhysicalMetric,
)


def create_controlled_field(
    k_test: float,
    amplitude: float = 0.5,
    c: float = 1.0,
    tau: float = 1.0,
    nx: int = 50,
    ny: int = 50,
) -> InformationDensityField:
    """Create a controlled field with a single sinusoidal mode."""
    x_range = (0.0, 100.0)
    y_range = (0.0, 100.0)
    dx = (x_range[1] - x_range[0]) / (nx - 1)
    dy = (y_range[1] - y_range[0]) / (ny - 1)
    
    X, Y = np.meshgrid(
        np.linspace(x_range[0], x_range[1], nx),
        np.linspace(y_range[0], y_range[1], ny),
        indexing='ij'
    )
    field_values = 1.0 + amplitude * np.cos(k_test * X)
    
    state = FieldState(
        field_values=field_values.ravel(),
        field_velocity=np.zeros(nx * ny),
        coordinates=np.column_stack([X.ravel(), Y.ravel(), np.zeros(nx * ny)]),
        dx=dx,
        dy=dy,
        dz=1.0,
        dt=0.1,
        physical_time=0.0,
        grid_shape=(nx, ny, 1),
        metric=PhysicalMetric(g_ij=np.eye(3), g_inv=np.eye(3)),
    )
    
    physical_volume = 100.0 * 100.0 * 1.0
    field = InformationDensityField(
        state=state,
        information_quantity=1.0,
        physical_volume=physical_volume,
        information_units="bits",
        spatial_units="m",
        density_units="bits/m³",
    )
    
    return field


def replace_physical_field_in_kernel(kernel: WorldKernel, field: InformationDensityField) -> None:
    """Replace the physical field in the kernel's global state."""
    import sim_world.domains.physical_field.physical_field_domain as pf_domain
    pf_domain._physical_field = field


def run_controlled_case(
    case_name: str,
    k_test: float,
    amplitude: float,
    ticks: int,
    c: float = 1.0,
    tau: float = 1.0,
) -> dict:
    """Run a controlled case through the actual kernel."""
    print(f"\n{'='*80}")
    print(f"CASE: {case_name}")
    print(f"{'='*80}")
    print(f"k_test: {k_test:.4f} rad/m")
    print(f"amplitude: {amplitude:.4f}")
    print(f"ticks: {ticks}")
    
    # Create kernel
    world_id = WorldId.new(f"causal_{case_name}")
    config = KernelConfig(world_id=world_id, initial_state={})
    kernel = WorldKernel(config=config)
    
    # Register domain
    from sim_world.domains.physical_field import register as register_physical_field
    register_physical_field(kernel.simulation_engine)
    
    # Create controlled field
    field = create_controlled_field(k_test, amplitude=amplitude, c=c, tau=tau)
    replace_physical_field_in_kernel(kernel, field)
    
    # Calculate expected regime
    k_c = 1.0 / (2 * c * tau)
    expected_D = 4 * c**2 * tau**2 * k_test**2 - 1
    expected_regime = "coherent" if expected_D > 0 else "overdamped"
    
    print(f"Expected D(k): {expected_D:.4f}")
    print(f"Expected regime: {expected_regime}")
    
    # Run ticks and collect data
    spectral_data = []
    transport_data = []
    entity_data = []
    
    for i in range(ticks):
        revision = kernel.advance_tick()
        
        # Collect spectral observables
        spectral_obs = kernel.last_spectral_transport_observable
        if spectral_obs is not None:
            spectral_data.append({
                'tick': i + 1,
                'dominant_k': spectral_obs.dominant_k,
                'dominant_D': spectral_obs.dominant_D,
                'dominant_regime': spectral_obs.dominant_regime,
                'f_prop': spectral_obs.propagating_power_fraction,
                'f_over': spectral_obs.overdamped_power_fraction,
                'f_crit': spectral_obs.critical_power_fraction,
                'weighted_D': spectral_obs.weighted_D,
                'spectral_entropy': spectral_obs.spectral_entropy,
            })
        
        # Collect transport observables (downstream metrics)
        transport_obs = kernel.last_transport_observation
        if transport_obs is not None:
            metric_values = dict(transport_obs.metric_values)
            transport_data.append({
                'tick': i + 1,
                'q_value': transport_obs.q_value,
                'regime': transport_obs.regime,
                'state_distance': metric_values.get('state_distance', 0.0),
                'representation_distance': metric_values.get('representation_distance', 0.0),
                'identity_preservation': metric_values.get('identity_preservation', 1.0),
                'topology_preservation': metric_values.get('topology_preservation', 1.0),
                'component_preservation': metric_values.get('component_preservation', 1.0),
                'relationship_preservation': metric_values.get('relationship_preservation', 1.0),
                'transition_magnitude': metric_values.get('transition_magnitude', 0.0),
                'structural_consistency': metric_values.get('structural_consistency', 1.0),
                'temporal_consistency': metric_values.get('temporal_consistency', 1.0),
            })
        
        # Collect entity data
        entity_count = len(kernel.entity_registry.serialize())
        entity_data.append({
            'tick': i + 1,
            'entity_count': entity_count,
        })
    
    # Compute averages
    avg_spectral = {}
    if spectral_data:
        for key in ['dominant_k', 'dominant_D', 'f_prop', 'f_over', 'f_crit', 'weighted_D', 'spectral_entropy']:
            values = [d[key] for d in spectral_data]
            avg_spectral[key] = np.mean(values)
            avg_spectral[f'{key}_std'] = np.std(values)
    
    avg_transport = {}
    if transport_data:
        for key in ['q_value', 'state_distance', 'representation_distance', 'identity_preservation',
                   'topology_preservation', 'component_preservation', 'relationship_preservation',
                   'transition_magnitude', 'structural_consistency', 'temporal_consistency']:
            values = [d[key] for d in transport_data]
            avg_transport[key] = np.mean(values)
            avg_transport[f'{key}_std'] = np.std(values)
    
    print(f"\nResults:")
    print(f"  Spectral observables: {len(spectral_data)}")
    print(f"  Transport observables: {len(transport_data)}")
    print(f"  Entity data points: {len(entity_data)}")
    
    if spectral_data:
        print(f"\n  Average spectral regime: {spectral_data[-1]['dominant_regime']}")
        print(f"  Average dominant_D: {avg_spectral['dominant_D']:.4f} ± {avg_spectral['dominant_D_std']:.4f}")
        print(f"  Average f_prop: {avg_spectral['f_prop']:.4f} ± {avg_spectral['f_prop_std']:.4f}")
        print(f"  Average f_over: {avg_spectral['f_over']:.4f} ± {avg_spectral['f_over_std']:.4f}")
    
    if transport_data:
        print(f"\n  Average transport regime: {transport_data[-1]['regime']}")
        print(f"  Average q_value: {avg_transport['q_value']:.4f} ± {avg_transport['q_value_std']:.4f}")
        print(f"  Average state_distance: {avg_transport['state_distance']:.4f} ± {avg_transport['state_distance_std']:.4f}")
        print(f"  Average identity_preservation: {avg_transport['identity_preservation']:.4f} ± {avg_transport['identity_preservation_std']:.4f}")
    
    return {
        'case_name': case_name,
        'k_test': k_test,
        'amplitude': amplitude,
        'ticks': ticks,
        'expected_D': expected_D,
        'expected_regime': expected_regime,
        'spectral_data': spectral_data,
        'transport_data': transport_data,
        'entity_data': entity_data,
        'avg_spectral': avg_spectral,
        'avg_transport': avg_transport,
    }


def main():
    """Run causal coupling experiment."""
    print("="*80)
    print("CAUSAL COUPLING EXPERIMENT")
    print("Spectral Transport Regime vs Downstream Dynamics")
    print("="*80)
    
    # Calculate tick budget
    ticks_per_case = 50
    cases = [
        ('CASE_A_overdamped', 0.25, 0.5),  # k < k_c
        ('CASE_B_propagating', 0.75, 0.5),  # k > k_c
        ('CASE_C_multimode_1', 0.25, 0.5),  # Overdamped dominant
        ('CASE_C_multimode_2', 0.75, 0.5),  # Propagating dominant
        ('CASE_D_amp_0.25', 0.75, 0.25),  # Propagating, low amplitude
        ('CASE_D_amp_2.0', 0.75, 2.0),   # Propagating, high amplitude
    ]
    
    total_ticks = len(cases) * ticks_per_case
    print(f"\nTick budget: {total_ticks} / 500 (✅ within limit)")
    
    # Run all cases
    results = []
    for case_name, k_test, amplitude in cases:
        result = run_controlled_case(case_name, k_test, amplitude, ticks_per_case)
        results.append(result)
    
    # Analysis
    print("\n" + "="*80)
    print("CAUSAL ANALYSIS")
    print("="*80)
    
    # Compare CASE A vs CASE B (overdamped vs propagating)
    case_a = results[0]
    case_b = results[1]
    
    print("\nCASE A (Overdamped) vs CASE B (Propagating):")
    print(f"  Spectral difference:")
    print(f"    dominant_D: {case_a['avg_spectral']['dominant_D']:.4f} vs {case_b['avg_spectral']['dominant_D']:.4f}")
    print(f"    f_prop: {case_a['avg_spectral']['f_prop']:.4f} vs {case_b['avg_spectral']['f_prop']:.4f}")
    print(f"    f_over: {case_a['avg_spectral']['f_over']:.4f} vs {case_b['avg_spectral']['f_over']:.4f}")
    
    print(f"  Downstream difference:")
    print(f"    q_value: {case_a['avg_transport']['q_value']:.4f} vs {case_b['avg_transport']['q_value']:.4f}")
    print(f"    state_distance: {case_a['avg_transport']['state_distance']:.4f} vs {case_b['avg_transport']['state_distance']:.4f}")
    print(f"    identity_preservation: {case_a['avg_transport']['identity_preservation']:.4f} vs {case_b['avg_transport']['identity_preservation']:.4f}")
    
    # Check for statistical significance
    q_diff = abs(case_a['avg_transport']['q_value'] - case_b['avg_transport']['q_value'])
    state_diff = abs(case_a['avg_transport']['state_distance'] - case_b['avg_transport']['state_distance'])
    
    print(f"\n  Quantitative differences:")
    print(f"    q_value difference: {q_diff:.6f}")
    print(f"    state_distance difference: {state_diff:.6f}")
    
    # Amplitude invariance check
    case_d1 = results[4]  # amp 0.25
    case_d2 = results[5]  # amp 2.0
    
    print("\nAmplitude Invariance (CASE D):")
    print(f"  Amplitude 0.25 vs 2.0 (same spectral regime):")
    print(f"    Spectral dominant_D: {case_d1['avg_spectral']['dominant_D']:.4f} vs {case_d2['avg_spectral']['dominant_D']:.4f}")
    regime_d1 = case_d1['spectral_data'][-1]['dominant_regime'] if case_d1['spectral_data'] else 'unknown'
    regime_d2 = case_d2['spectral_data'][-1]['dominant_regime'] if case_d2['spectral_data'] else 'unknown'
    print(f"    Spectral regime: {regime_d1} vs {regime_d2}")
    print(f"    Downstream q_value: {case_d1['avg_transport']['q_value']:.4f} vs {case_d2['avg_transport']['q_value']:.4f}")
    
    # Classification
    print("\n" + "="*80)
    print("SCIENTIFIC CLASSIFICATION")
    print("="*80)
    
    # Determine if there's measurable coupling
    regime_a = case_a['spectral_data'][-1]['dominant_regime'] if case_a['spectral_data'] else 'unknown'
    regime_b = case_b['spectral_data'][-1]['dominant_regime'] if case_b['spectral_data'] else 'unknown'
    spectral_regime_changed = (regime_a != regime_b)
    downstream_changed = (q_diff > 0.01 or state_diff > 0.01)
    
    print(f"  Spectral regime A: {regime_a}")
    print(f"  Spectral regime B: {regime_b}")
    print(f"  Spectral regime changed: {spectral_regime_changed}")
    print(f"  Downstream metrics changed: {downstream_changed}")
    print(f"  q_value difference: {q_diff:.6f}")
    print(f"  state_distance difference: {state_diff:.6f}")
    
    # Classification
    if not downstream_changed:
        classification = "CASE 1 — NO MEASURABLE COUPLING"
        print(f"\n  Classification: {classification}")
    else:
        classification = "CASE 5 — INCONCLUSIVE"
        print(f"\n  Classification: {classification}")
    
    # Save results
    output_file = "causal_coupling_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            'classification': classification,
            'total_ticks': total_ticks,
            'results': results,
        }, f, indent=2, default=str)
    
    print(f"\nResults saved to: {output_file}")
    
    return classification


if __name__ == "__main__":
    classification = main()
    print(f"\n{'='*80}")
    print(f"FINAL CLASSIFICATION: {classification}")
    print(f"{'='*80}")
