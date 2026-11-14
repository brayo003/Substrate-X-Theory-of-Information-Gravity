"""
Artificial-life capability testbed for theoretical Q substrate.

This module creates a controlled experimental environment to test whether the physical
substrate can exhibit artificial-life-like behaviors and whether Q provides useful diagnostics.
"""

import numpy as np
from typing import Dict, Any, List, Optional
from .physical_field_models import (
    InformationDensityField,
    PhysicalCoordinate,
    PropagationParameters,
    RelaxationParameters,
)
from .physical_field_dynamics import (
    initialize_field_state,
    evolve_field,
    apply_perturbation,
    compute_theoretical_q,
    compute_independent_observables,
)
from .controlled_experiments import ControlledExperiments


class ArtificialLifeTestbed:
    """Testbed for artificial-life capabilities in physical substrate."""
    
    def __init__(self, field: InformationDensityField):
        self.field = field
        self.experiments = ControlledExperiments(field)
        self.structures: List[Dict[str, Any]] = []
        self.observation_history: List[Dict[str, Any]] = []
    
    def create_persistent_structure(
        self,
        center: PhysicalCoordinate,
        amplitude: float,
        width: float,
        duration: float,
    ) -> Dict[str, Any]:
        """Create a persistent structure in the field.
        
        Args:
            center: Center of structure
            amplitude: Initial amplitude
            width: Spatial extent
            duration: Time to maintain structure
        
        Returns:
            Structure properties and persistence metrics
        """
        # Initialize structure
        field = apply_perturbation(self.field, center, amplitude, width)
        
        prop_params = PropagationParameters(c_nominal=1.0)
        relax_params = RelaxationParameters(tau_nominal=1.0)
        
        # Evolve for duration
        structure_values = []
        for _ in range(int(duration / field.state.dt)):
            field = evolve_field(field, prop_params, relax_params)
            structure_values.append(field.get_density_at(center))
        
        # Analyze persistence
        initial_value = structure_values[0]
        final_value = structure_values[-1]
        decay_rate = (initial_value - final_value) / duration if duration > 0 else 0.0
        
        structure = {
            "center": {"x": center.x, "y": center.y, "z": center.z},
            "initial_amplitude": amplitude,
            "width": width,
            "duration": duration,
            "initial_value": float(initial_value),
            "final_value": float(final_value),
            "decay_rate": float(decay_rate),
            "persistence_ratio": float(final_value / initial_value) if initial_value > 0 else 0.0,
            "structure_values": [float(v) for v in structure_values],
        }
        
        self.structures.append(structure)
        return structure
    
    def test_self_maintenance(
        self,
        center: PhysicalCoordinate,
        maintenance_amplitude: float,
        maintenance_interval: float,
        total_time: float,
    ) -> Dict[str, Any]:
        """Test self-maintenance behavior with periodic perturbations.
        
        Args:
            center: Center of structure
            maintenance_amplitude: Amplitude of maintenance perturbations
            maintenance_interval: Time between maintenance
            total_time: Total simulation time
        
        Returns:
            Self-maintenance metrics
        """
        field = self.field
        prop_params = PropagationParameters(c_nominal=1.0)
        relax_params = RelaxationParameters(tau_nominal=1.0)
        
        field_values = []
        maintenance_times = []
        
        current_time = 0.0
        maintenance_count = 0
        
        while current_time < total_time:
            # Evolve field
            field = evolve_field(field, prop_params, relax_params)
            current_time += field.state.dt
            
            # Apply maintenance if interval elapsed
            if current_time >= maintenance_count * maintenance_interval:
                field = apply_perturbation(field, center, maintenance_amplitude, 5.0)
                maintenance_count += 1
                maintenance_times.append(current_time)
            
            field_values.append(field.get_density_at(center))
        
        # Analyze self-maintenance
        mean_value = np.mean(field_values)
        std_value = np.std(field_values)
        stability_ratio = std_value / mean_value if mean_value > 0 else 0.0
        
        return {
            "center": {"x": center.x, "y": center.y, "z": center.z},
            "maintenance_amplitude": maintenance_amplitude,
            "maintenance_interval": maintenance_interval,
            "total_time": total_time,
            "maintenance_count": maintenance_count,
            "mean_value": float(mean_value),
            "std_value": float(std_value),
            "stability_ratio": float(stability_ratio),
            "field_values": [float(v) for v in field_values],
            "maintenance_times": maintenance_times,
        }
    
    def test_spatial_organization(
        self,
        perturbation_centers: List[PhysicalCoordinate],
        amplitude: float,
        width: float,
        evolution_time: float,
    ) -> Dict[str, Any]:
        """Test spatial organization from multiple perturbations.
        
        Args:
            perturbation_centers: Centers of multiple perturbations
            amplitude: Amplitude of perturbations
            width: Spatial extent
            evolution_time: Time to evolve
        
        Returns:
            Spatial organization metrics
        """
        field = self.field
        prop_params = PropagationParameters(c_nominal=1.0)
        relax_params = RelaxationParameters(tau_nominal=1.0)
        
        # Apply multiple perturbations
        for center in perturbation_centers:
            field = apply_perturbation(field, center, amplitude, width)
        
        # Evolve field
        for _ in range(int(evolution_time / field.state.dt)):
            field = evolve_field(field, prop_params, relax_params)
        
        # Analyze spatial organization
        field_values = []
        for center in perturbation_centers:
            field_values.append(field.get_density_at(center))
        
        # Calculate spatial correlations
        correlation_matrix = np.zeros((len(perturbation_centers), len(perturbation_centers)))
        for i in range(len(perturbation_centers)):
            for j in range(len(perturbation_centers)):
                # Simple correlation based on distance
                distance = perturbation_centers[i].distance_to(perturbation_centers[j])
                correlation_matrix[i, j] = np.exp(-distance / 10.0)  # Exponential decay with distance
        
        return {
            "perturbation_centers": [
                {"x": center.x, "y": center.y, "z": center.z}
                for center in perturbation_centers
            ],
            "amplitude": amplitude,
            "width": width,
            "evolution_time": evolution_time,
            "field_values": [float(v) for v in field_values],
            "correlation_matrix": correlation_matrix.tolist(),
            "mean_field_value": float(np.mean(field_values)),
            "spatial_variance": float(np.var(field_values)),
        }
    
    def test_regime_transitions(
        self,
        center: PhysicalCoordinate,
        perturbation_amplitudes: List[float],
        evolution_time: float,
    ) -> Dict[str, Any]:
        """Test regime transitions with different perturbation amplitudes.
        
        Args:
            center: Center of perturbations
            perturbation_amplitudes: Different amplitudes to test
            evolution_time: Time to evolve
        
        Returns:
            Regime transition analysis
        """
        prop_params = PropagationParameters(c_nominal=1.0)
        relax_params = RelaxationParameters(tau_nominal=1.0)
        
        regime_sequence = []
        
        for amplitude in perturbation_amplitudes:
            # Initialize field
            field = initialize_field_state(
                nx=self.field.state.grid_shape[0],
                ny=self.field.state.grid_shape[1],
                initial_value=1.0,
                dt=self.field.state.dt,
            )
            
            # Apply perturbation
            field = apply_perturbation(field, center, amplitude, 5.0)
            
            # Evolve field
            field = evolve_field(field, prop_params, relax_params)
            
            # Compute Q
            q_obs = compute_theoretical_q(field, prop_params, relax_params, center)
            
            regime_sequence.append({
                "amplitude": amplitude,
                "q_value": float(q_obs.q_value),
                "regime": str(q_obs.regime),
                "s_value": float(q_obs.s_value),
                "gradient_magnitude": float(q_obs.gradient_magnitude),
            })
        
        # Analyze transitions
        transitions = []
        for i in range(len(regime_sequence) - 1):
            if regime_sequence[i]["regime"] != regime_sequence[i + 1]["regime"]:
                transitions.append({
                    "from_regime": regime_sequence[i]["regime"],
                    "to_regime": regime_sequence[i + 1]["regime"],
                    "amplitude_threshold": regime_sequence[i]["amplitude"],
                })
        
        return {
            "center": {"x": center.x, "y": center.y, "z": center.z},
            "perturbation_amplitudes": perturbation_amplitudes,
            "evolution_time": evolution_time,
            "regime_sequence": regime_sequence,
            "transitions": transitions,
            "transition_count": len(transitions),
        }
    
    def test_adaptive_response(
        self,
        center: PhysicalCoordinate,
        perturbation_amplitude: float,
        adaptive_feedback_strength: float,
        evolution_time: float,
    ) -> Dict[str, Any]:
        """Test adaptive response with feedback mechanism.
        
        Args:
            center: Center of perturbation
            perturbation_amplitude: Initial amplitude
            adaptive_feedback_strength: Strength of adaptive feedback
            evolution_time: Time to evolve
        
        Returns:
            Adaptive response metrics
        """
        field = self.field
        prop_params = PropagationParameters(c_nominal=1.0)
        relax_params = RelaxationParameters(tau_nominal=1.0)
        
        field_values = []
        feedback_applied = []
        
        current_time = 0.0
        
        while current_time < evolution_time:
            # Evolve field
            field = evolve_field(field, prop_params, relax_params)
            current_time += field.state.dt
            
            # Get current field value
            current_value = field.get_density_at(center)
            field_values.append(current_value)
            
            # Apply adaptive feedback if field deviates from target
            target_value = 1.0
            deviation = current_value - target_value
            
            if abs(deviation) > 0.5:  # Threshold for feedback
                feedback_amplitude = -deviation * adaptive_feedback_strength
                field = apply_perturbation(field, center, feedback_amplitude, 5.0)
                feedback_applied.append({
                    "time": current_time,
                    "deviation": float(deviation),
                    "feedback_amplitude": float(feedback_amplitude),
                })
        
        # Analyze adaptive response
        final_value = field_values[-1]
        target_error = abs(final_value - 1.0)
        
        return {
            "center": {"x": center.x, "y": center.y, "z": center.z},
            "perturbation_amplitude": perturbation_amplitude,
            "adaptive_feedback_strength": adaptive_feedback_strength,
            "evolution_time": evolution_time,
            "initial_value": float(field_values[0]),
            "final_value": float(final_value),
            "target_error": float(target_error),
            "feedback_count": len(feedback_applied),
            "feedback_events": feedback_applied,
            "field_values": [float(v) for v in field_values],
        }
    
    def run_comprehensive_al_test(
        self,
        test_duration: float = 20.0,
    ) -> Dict[str, Any]:
        """Run comprehensive artificial-life test.
        
        Args:
            test_duration: Total test duration
        
        Returns:
            Comprehensive test results
        """
        results = {
            "test_duration": test_duration,
            "persistent_structures": [],
            "self_maintenance": None,
            "spatial_organization": None,
            "regime_transitions": None,
            "adaptive_response": None,
            "q_diagnostics": [],
        }
        
        # Test 1: Persistent structures
        centers = [
            PhysicalCoordinate(30.0, 30.0, 0.0),
            PhysicalCoordinate(70.0, 70.0, 0.0),
        ]
        for center in centers:
            structure = self.create_persistent_structure(center, 2.0, 5.0, 10.0)
            results["persistent_structures"].append(structure)
        
        # Test 2: Self-maintenance
        self_maintenance = self.test_self_maintenance(
            PhysicalCoordinate(50.0, 50.0, 0.0),
            0.5,
            2.0,
            10.0,
        )
        results["self_maintenance"] = self_maintenance
        
        # Test 3: Spatial organization
        spatial_org = self.test_spatial_organization(
            [
                PhysicalCoordinate(25.0, 25.0, 0.0),
                PhysicalCoordinate(75.0, 25.0, 0.0),
                PhysicalCoordinate(25.0, 75.0, 0.0),
                PhysicalCoordinate(75.0, 75.0, 0.0),
            ],
            1.5,
            5.0,
            5.0,
        )
        results["spatial_organization"] = spatial_org
        
        # Test 4: Regime transitions
        regime_trans = self.test_regime_transitions(
            PhysicalCoordinate(50.0, 50.0, 0.0),
            [0.5, 1.0, 2.0, 5.0, 10.0],
            5.0,
        )
        results["regime_transitions"] = regime_trans
        
        # Test 5: Adaptive response
        adaptive_resp = self.test_adaptive_response(
            PhysicalCoordinate(50.0, 50.0, 0.0),
            2.0,
            0.3,
            10.0,
        )
        results["adaptive_response"] = adaptive_resp
        
        # Test 6: Q diagnostics throughout
        prop_params = PropagationParameters(c_nominal=1.0)
        relax_params = RelaxationParameters(tau_nominal=1.0)
        
        for i in range(10):
            q_obs = compute_theoretical_q(
                self.field,
                prop_params,
                relax_params,
                PhysicalCoordinate(50.0, 50.0, 0.0),
            )
            results["q_diagnostics"].append({
                "step": i,
                "q_value": float(q_obs.q_value),
                "regime": str(q_obs.regime),
            })
            
            self.field = evolve_field(self.field, prop_params, relax_params)
        
        return results
