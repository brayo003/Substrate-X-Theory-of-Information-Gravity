"""
Script to run controlled experiments and generate validation results.
"""

import sys
sys.path.append('/home/lenovo/Git/Substrate_X_Theory_of_Information_Gravity/SXC_IGC/Domain-Calibrated_Instability_Framework(DCIF)/dcif_modules/substrate_ai_module/sim_world/domains/physical_field')

from physical_field_models import (
    InformationDensityField,
    PhysicalCoordinate,
    PropagationParameters,
    RelaxationParameters,
)
from physical_field_dynamics import (
    initialize_field_state,
)
from controlled_experiments import ControlledExperiments
import json


def run_validation_experiments():
    """Run controlled experiments and generate validation results."""
    
    print("=" * 80)
    print("RUNNING CONTROLLED VALIDATION EXPERIMENTS")
    print("=" * 80)
    
    # Initialize field
    print("\n1. Initializing physical field...")
    field = initialize_field_state(
        x_range=(0.0, 100.0),
        y_range=(0.0, 100.0),
        nx=20,  # Smaller grid for faster experiments
        ny=20,
        initial_value=1.0,
        dt=0.1,
    )
    
    field = InformationDensityField(
        state=field,
        information_quantity=1.0,
        physical_volume=100.0 * 100.0 * 1.0,
    )
    
    print(f"   Field initialized: {field.state.grid_shape} grid")
    print(f"   Physical domain: 100m x 100m x 1m")
    print(f"   Time step: {field.state.dt}s")
    
    # Initialize experiments
    experiments = ControlledExperiments(field)
    
    # Experiment 1: Propagation speed measurement
    print("\n2. Running propagation speed measurement...")
    center = PhysicalCoordinate(50.0, 50.0, 0.0)
    prop_results = experiments.propagation_experiment(
        center=center,
        perturbation_amplitude=2.0,
        perturbation_width=5.0,
        observer_distances=[10.0, 20.0, 30.0],
        max_time=5.0,  # Short time for testing
        trials=3,
    )
    
    print(f"   Measured c: {prop_results['c_mean']:.4f} ± {prop_results['c_uncertainty']:.4f} m/s")
    print(f"   Nominal c: {prop_results['c_nominal']} m/s")
    print(f"   Measurements: {prop_results['c_measurements']}")
    
    # Experiment 2: Relaxation time measurement
    print("\n3. Running relaxation time measurement...")
    relax_results = experiments.relaxation_experiment(
        center=center,
        perturbation_amplitude=2.0,
        perturbation_width=5.0,
        max_time=5.0,  # Short time for testing
        trials=3,
    )
    
    print(f"   Measured τ: {relax_results['tau_mean']:.4f} ± {relax_results['tau_uncertainty']:.4f} s")
    print(f"   Nominal τ: {relax_results['tau_nominal']} s")
    print(f"   Measurements: {relax_results['tau_measurements']}")
    
    # Experiment 3: Q validation
    print("\n4. Running Q validation experiment...")
    test_coords = [
        PhysicalCoordinate(50.0, 50.0, 0.0),
        PhysicalCoordinate(30.0, 30.0, 0.0),
        PhysicalCoordinate(70.0, 70.0, 0.0),
    ]
    
    prop_params = PropagationParameters(c_nominal=prop_results['c_mean'])
    relax_params = RelaxationParameters(tau_nominal=relax_results['tau_mean'])
    
    q_validation = experiments.q_validation_experiment(
        field=field,
        propagation_params=prop_params,
        relaxation_params=relax_params,
        test_coordinates=test_coords,
        perturbation_amplitude=2.0,
        perturbation_width=5.0,
    )
    
    print(f"   Agreement rate: {q_validation['agreement_rate']:.2%}")
    print(f"   Q regimes: {[obs['regime'] for obs in q_validation['q_observations']]}")
    print(f"   Independent regimes: {[item['independent_regime'] for item in q_validation['classification_agreement']]}")
    
    # Experiment 4: Spatial resolution convergence
    print("\n5. Running spatial resolution convergence...")
    convergence_results = experiments.spatial_resolution_convergence_experiment(
        resolutions=[10, 20, 30],
        perturbation_amplitude=2.0,
        perturbation_width=5.0,
    )
    
    print(f"   Q convergence: {convergence_results['q_convergence']:.6f}")
    print(f"   Q values at different resolutions: {convergence_results['q_values']}")
    
    # Experiment 5: Parameter sensitivity
    print("\n6. Running parameter sensitivity experiment...")
    sensitivity_results = experiments.parameter_sensitivity_experiment(
        c_values=[0.5, 1.0, 2.0],
        tau_values=[0.5, 1.0, 2.0],
        perturbation_amplitude=2.0,
        perturbation_width=5.0,
    )
    
    print(f"   Q matrix:")
    for i, c in enumerate(sensitivity_results['c_values']):
        print(f"     c={c}: {sensitivity_results['q_matrix'][i]}")
    
    # Generate validation results document
    print("\n7. Generating validation results document...")
    
    validation_results = {
        "experiment_date": "2026-08-09",
        "field_specification": {
            "domain_size": "100m x 100m x 1m",
            "grid_resolution": "20 x 20 x 1",
            "time_step": "0.1s",
            "initial_value": 1.0,
            "information_units": "bits",
            "spatial_units": "m",
            "density_units": "bits/m³",
        },
        "propagation_experiments": prop_results,
        "relaxation_experiments": relax_results,
        "q_validation": q_validation,
        "spatial_convergence": convergence_results,
        "parameter_sensitivity": sensitivity_results,
        "scientific_classification": "C - CONSTRUCTIBLE WITH SUBSTANTIAL NEW PHYSICAL ASSUMPTIONS",
        "next_steps": [
            "Run longer-duration experiments for better statistics",
            "Test substrate coupling in real simulation",
            "Validate energy-based regime classification",
            "Test AL capabilities with comprehensive testbed",
        ],
    }
    
    # Save results
    results_path = '/home/lenovo/Git/Substrate_X_Theory_of_Information_Gravity/SXC_IGC/Domain-Calibrated_Instability_Framework(DCIF)/dcif_modules/substrate_ai_module/q_capability_experiment/Q_PHYSICAL_VALIDATION_RESULTS.md'
    
    with open(results_path, 'w') as f:
        f.write("# Q Physical Validation Results\n\n")
        f.write("**Validation Date:** 2026-08-09\n\n")
        f.write("---\n\n")
        f.write("## Executive Summary\n\n")
        f.write(f"**Classification:** {validation_results['scientific_classification']}\n\n")
        f.write("## Field Specification\n\n")
        f.write(f"- Domain size: {validation_results['field_specification']['domain_size']}\n")
        f.write(f"- Grid resolution: {validation_results['field_specification']['grid_resolution']}\n")
        f.write(f"- Time step: {validation_results['field_specification']['time_step']}\n")
        f.write(f"- Information units: {validation_results['field_specification']['information_units']}\n")
        f.write(f"- Spatial units: {validation_results['field_specification']['spatial_units']}\n")
        f.write(f"- Density units: {validation_results['field_specification']['density_units']}\n\n")
        f.write("---\n\n")
        f.write("## Propagation Speed Measurement\n\n")
        f.write(f"- Measured c: {prop_results['c_mean']:.4f} ± {prop_results['c_uncertainty']:.4f} m/s\n")
        f.write(f"- Nominal c: {prop_results['c_nominal']} m/s\n")
        f.write(f"- Individual measurements: {prop_results['c_measurements']}\n")
        f.write(f"- Number of trials: {prop_results['trials']}\n\n")
        f.write("---\n\n")
        f.write("## Relaxation Time Measurement\n\n")
        f.write(f"- Measured τ: {relax_results['tau_mean']:.4f} ± {relax_results['tau_uncertainty']:.4f} s\n")
        f.write(f"- Nominal τ: {relax_results['tau_nominal']} s\n")
        f.write(f"- Individual measurements: {relax_results['tau_measurements']}\n")
        f.write(f"- Number of trials: {relax_results['trials']}\n")
        f.write(f"- Relaxation law: exponential\n\n")
        f.write("---\n\n")
        f.write("## Q Validation Results\n\n")
        f.write(f"- Agreement rate: {q_validation['agreement_rate']:.2%}\n")
        f.write(f"- Q regimes: {[obs['regime'] for obs in q_validation['q_observations']]}\n")
        f.write(f"- Independent regimes: {[item['independent_regime'] for item in q_validation['classification_agreement']]}\n\n")
        f.write("---\n\n")
        f.write("## Spatial Resolution Convergence\n\n")
        f.write(f"- Q convergence: {convergence_results['q_convergence']:.6f}\n")
        f.write(f"- Q values: {convergence_results['q_values']}\n")
        f.write(f"- Gradient magnitudes: {convergence_results['gradient_magnitudes']}\n\n")
        f.write("---\n\n")
        f.write("## Parameter Sensitivity\n\n")
        f.write(f"- c values: {sensitivity_results['c_values']}\n")
        f.write(f"- τ values: {sensitivity_results['tau_values']}\n")
        f.write(f"- Q matrix:\n")
        for i, c in enumerate(sensitivity_results['c_values']):
            f.write(f"  c={c}: {sensitivity_results['q_matrix'][i]}\n")
        f.write("\n---\n")
        f.write("## Next Steps\n\n")
        for step in validation_results['next_steps']:
            f.write(f"- {step}\n")
    
    print(f"   Results saved to: {results_path}")
    
    print("\n" + "=" * 80)
    print("VALIDATION EXPERIMENTS COMPLETE")
    print("=" * 80)
    
    return validation_results


if __name__ == "__main__":
    results = run_validation_experiments()
