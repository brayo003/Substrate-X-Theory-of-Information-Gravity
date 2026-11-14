"""
Controlled physical field experiments.

This module implements controlled experiments to validate the theoretical Q implementation
and measure propagation speed c and relaxation time τ from actual substrate dynamics.
"""

import numpy as np
from typing import Dict, Any, List, Tuple
from .physical_field_models import (
    InformationDensityField,
    PhysicalCoordinate,
    PropagationParameters,
    RelaxationParameters,
    QObservation,
)
from .physical_field_dynamics import (
    initialize_field_state,
    evolve_field,
    apply_perturbation,
    measure_propagation_speed,
    measure_relaxation_time,
    compute_theoretical_q,
    compute_independent_observables,
)


class ControlledExperiments:
    """Controlled experiments for physical field validation."""
    
    def __init__(self, field: InformationDensityField):
        self.field = field
        self.experiment_results: List[Dict[str, Any]] = []
    
    def propagation_experiment(
        self,
        center: PhysicalCoordinate,
        perturbation_amplitude: float = 2.0,
        perturbation_width: float = 5.0,
        observer_distances: List[float] = [10.0, 20.0, 30.0, 40.0],
        max_time: float = 10.0,
        trials: int = 3,
    ) -> Dict[str, Any]:
        """Run controlled propagation experiment to measure c.
        
        Args:
            center: Center of perturbation
            perturbation_amplitude: Amplitude of perturbation
            perturbation_width: Spatial width of perturbation
            observer_distances: Distances to observe propagation
            max_time: Maximum simulation time
            trials: Number of experimental trials
        
        Returns:
            Experiment results with measured c and uncertainty
        """
        results = {
            "experiment_type": "propagation",
            "center": {"x": center.x, "y": center.y, "z": center.z},
            "perturbation_amplitude": perturbation_amplitude,
            "perturbation_width": perturbation_width,
            "observer_distances": observer_distances,
            "max_time": max_time,
            "trials": trials,
            "c_measurements": [],
            "c_nominal": 1.0,
        }
        
        c_measurements = []
        
        for trial in range(trials):
            # Reset field to initial state
            field = initialize_field_state(
                nx=self.field.state.grid_shape[0],
                ny=self.field.state.grid_shape[1],
                initial_value=1.0,
                dt=self.field.state.dt,
            )
            
            # Set up propagation parameters
            prop_params = PropagationParameters(c_nominal=1.0)
            
            # Measure c
            measured_params = measure_propagation_speed(
                field,
                prop_params,
                center,
                perturbation_amplitude=perturbation_amplitude,
                perturbation_width=perturbation_width,
                observer_distances=observer_distances,
                max_time=max_time,
            )
            
            c_measurements.append(measured_params.c_measured)
        
        # Calculate statistics
        results["c_mean"] = float(np.mean(c_measurements))
        results["c_std"] = float(np.std(c_measurements))
        results["c_uncertainty"] = float(np.std(c_measurements) / np.sqrt(len(c_measurements)))
        results["c_measurements"] = [float(c) for c in c_measurements]
        
        # Store results
        self.experiment_results.append(results)
        
        return results
    
    def relaxation_experiment(
        self,
        center: PhysicalCoordinate,
        perturbation_amplitude: float = 2.0,
        perturbation_width: float = 5.0,
        max_time: float = 20.0,
        trials: int = 3,
    ) -> Dict[str, Any]:
        """Run controlled relaxation experiment to measure τ.
        
        Args:
            center: Center of perturbation
            perturbation_amplitude: Amplitude of perturbation
            perturbation_width: Spatial width of perturbation
            max_time: Maximum simulation time
            trials: Number of experimental trials
        
        Returns:
            Experiment results with measured τ and uncertainty
        """
        results = {
            "experiment_type": "relaxation",
            "center": {"x": center.x, "y": center.y, "z": center.z},
            "perturbation_amplitude": perturbation_amplitude,
            "perturbation_width": perturbation_width,
            "max_time": max_time,
            "trials": trials,
            "tau_measurements": [],
            "tau_nominal": 1.0,
        }
        
        tau_measurements = []
        
        for trial in range(trials):
            # Reset field to initial state
            field = initialize_field_state(
                nx=self.field.state.grid_shape[0],
                ny=self.field.state.grid_shape[1],
                initial_value=1.0,
                dt=self.field.state.dt,
            )
            
            # Set up relaxation parameters
            relax_params = RelaxationParameters(tau_nominal=1.0)
            
            # Measure τ
            measured_params = measure_relaxation_time(
                field,
                relax_params,
                center,
                perturbation_amplitude=perturbation_amplitude,
                perturbation_width=perturbation_width,
                max_time=max_time,
            )
            
            tau_measurements.append(measured_params.tau_measured)
        
        # Calculate statistics
        results["tau_mean"] = float(np.mean(tau_measurements))
        results["tau_std"] = float(np.std(tau_measurements))
        results["tau_uncertainty"] = float(np.std(tau_measurements) / np.sqrt(len(tau_measurements)))
        results["tau_measurements"] = [float(tau) for tau in tau_measurements]
        
        # Store results
        self.experiment_results.append(results)
        
        return results
    
    def q_validation_experiment(
        self,
        field: InformationDensityField,
        propagation_params: PropagationParameters,
        relaxation_params: RelaxationParameters,
        test_coordinates: List[PhysicalCoordinate],
        perturbation_amplitude: float = 2.0,
        perturbation_width: float = 5.0,
    ) -> Dict[str, Any]:
        """Run Q validation experiment comparing Q to independent observables.
        
        Args:
            field: Information density field
            propagation_params: Propagation parameters (c)
            relaxation_params: Relaxation parameters (τ)
            test_coordinates: Coordinates to test Q
            perturbation_amplitude: Amplitude of perturbation
            perturbation_width: Spatial width of perturbation
        
        Returns:
            Validation results comparing Q classification to independent observables
        """
        results = {
            "experiment_type": "q_validation",
            "test_coordinates": [
                {"x": coord.x, "y": coord.y, "z": coord.z}
                for coord in test_coordinates
            ],
            "perturbation_amplitude": perturbation_amplitude,
            "perturbation_width": perturbation_width,
            "q_observations": [],
            "independent_observables": [],
            "classification_agreement": [],
        }
        
        # Apply perturbation
        center = test_coordinates[0] if test_coordinates else PhysicalCoordinate(50.0, 50.0, 0.0)
        field = apply_perturbation(field, center, perturbation_amplitude, perturbation_width)
        
        # Evolve field
        field = evolve_field(field, propagation_params, relaxation_params)
        field = evolve_field(field, propagation_params, relaxation_params)
        
        # Collect Q observations and independent observables
        for coord in test_coordinates:
            q_obs = compute_theoretical_q(field, propagation_params, relaxation_params, coord)
            indep_obs = compute_independent_observables(field, coord)
            
            results["q_observations"].append({
                "coordinate": {"x": coord.x, "y": coord.y, "z": coord.z},
                "q_value": float(q_obs.q_value),
                "regime": str(q_obs.regime),
                "s_value": float(q_obs.s_value),
                "gradient_magnitude": float(q_obs.gradient_magnitude),
                "c_value": float(q_obs.c_value),
                "tau_value": float(q_obs.tau_value),
            })
            
            results["independent_observables"].append({
                "coordinate": {"x": coord.x, "y": coord.y, "z": coord.z},
                "field_value": float(indep_obs["field_value"]),
                "gradient_magnitude": float(indep_obs["gradient_magnitude"]),
                "local_velocity": float(indep_obs["local_velocity"]),
                "kinetic_energy": float(indep_obs["kinetic_energy"]),
                "potential_energy": float(indep_obs["potential_energy"]),
                "total_energy": float(indep_obs["total_energy"]),
            })
        
        # Analyze classification agreement
        for i in range(len(test_coordinates)):
            q_regime = results["q_observations"][i]["regime"]
            
            # Determine independent regime from total energy
            total_energy = results["independent_observables"][i]["total_energy"]
            
            # Independent regime classification based on energy
            if total_energy > 1.5:  # High energy → coherent
                indep_regime = "coherent"
            elif total_energy < 0.5:  # Low energy → overdamped
                indep_regime = "overdamped"
            else:  # Medium energy → critical
                indep_regime = "critical"
            
            agreement = q_regime == indep_regime
            results["classification_agreement"].append({
                "coordinate_index": i,
                "q_regime": q_regime,
                "independent_regime": indep_regime,
                "agreement": agreement,
            })
        
        # Calculate overall agreement rate
        agreement_count = sum(1 for item in results["classification_agreement"] if item["agreement"])
        results["agreement_rate"] = agreement_count / len(results["classification_agreement"])
        
        # Store results
        self.experiment_results.append(results)
        
        return results
    
    def spatial_resolution_convergence_experiment(
        self,
        resolutions: List[int] = [10, 20, 40, 80],
        perturbation_amplitude: float = 2.0,
        perturbation_width: float = 5.0,
    ) -> Dict[str, Any]:
        """Test spatial resolution convergence of Q calculation.
        
        Args:
            resolutions: List of grid resolutions (nx = ny)
            perturbation_amplitude: Amplitude of perturbation
            perturbation_width: Spatial width of perturbation
        
        Returns:
            Convergence results showing Q stability with resolution
        """
        results = {
            "experiment_type": "spatial_resolution_convergence",
            "resolutions": resolutions,
            "perturbation_amplitude": perturbation_amplitude,
            "perturbation_width": perturbation_width,
            "q_values": [],
            "gradient_magnitudes": [],
        }
        
        center = PhysicalCoordinate(50.0, 50.0, 0.0)
        prop_params = PropagationParameters(c_nominal=1.0)
        relax_params = RelaxationParameters(tau_nominal=1.0)
        
        for nx in resolutions:
            # Initialize field at resolution
            field = initialize_field_state(nx=nx, ny=nx, initial_value=1.0)
            
            # Apply perturbation
            field = apply_perturbation(field, center, perturbation_amplitude, perturbation_width)
            
            # Evolve field
            field = evolve_field(field, prop_params, relax_params)
            
            # Compute Q at center
            q_obs = compute_theoretical_q(field, prop_params, relax_params, center)
            
            results["q_values"].append(float(q_obs.q_value))
            results["gradient_magnitudes"].append(float(q_obs.gradient_magnitude))
        
        # Analyze convergence
        q_values = np.array(results["q_values"])
        results["q_convergence"] = np.std(q_values[-3:]) / np.abs(np.mean(q_values[-3:])) if len(q_values) >= 3 else 0.0
        
        # Store results
        self.experiment_results.append(results)
        
        return results
    
    def parameter_sensitivity_experiment(
        self,
        c_values: List[float] = [0.5, 1.0, 2.0, 5.0],
        tau_values: List[float] = [0.5, 1.0, 2.0, 5.0],
        perturbation_amplitude: float = 2.0,
        perturbation_width: float = 5.0,
    ) -> Dict[str, Any]:
        """Test parameter sensitivity of Q calculation.
        
        Args:
            c_values: List of propagation speed values to test
            tau_values: List of relaxation time values to test
            perturbation_amplitude: Amplitude of perturbation
            perturbation_width: Spatial width of perturbation
        
        Returns:
            Sensitivity results showing Q dependence on c and τ
        """
        results = {
            "experiment_type": "parameter_sensitivity",
            "c_values": c_values,
            "tau_values": tau_values,
            "perturbation_amplitude": perturbation_amplitude,
            "perturbation_width": perturbation_width,
            "q_matrix": [],
        }
        
        center = PhysicalCoordinate(50.0, 50.0, 0.0)
        
        for c in c_values:
            q_row = []
            for tau in tau_values:
                # Initialize field
                field = initialize_field_state(nx=20, ny=20, initial_value=1.0)
                
                # Apply perturbation
                field = apply_perturbation(field, center, perturbation_amplitude, perturbation_width)
                
                # Evolve field
                prop_params = PropagationParameters(c_nominal=c)
                relax_params = RelaxationParameters(tau_nominal=tau)
                field = evolve_field(field, prop_params, relax_params)
                
                # Compute Q
                q_obs = compute_theoretical_q(field, prop_params, relax_params, center)
                q_row.append(float(q_obs.q_value))
            
            results["q_matrix"].append(q_row)
        
        # Store results
        self.experiment_results.append(results)
        
        return results
    
    def get_all_results(self) -> List[Dict[str, Any]]:
        """Get all experiment results."""
        return self.experiment_results
    
    def clear_results(self) -> None:
        """Clear all experiment results."""
        self.experiment_results = []
