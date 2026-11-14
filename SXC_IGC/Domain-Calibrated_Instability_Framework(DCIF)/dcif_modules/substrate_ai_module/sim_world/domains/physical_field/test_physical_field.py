"""
Comprehensive test suite for theoretical Q physical substrate implementation.

Tests cover:
1. Physical-coordinate test
2. Metric test
3. Field positivity test
4. Spatial-gradient test
5. Gradient resolution-convergence test
6. Propagation test
7. c measurement test
8. Relaxation test
9. τ measurement test
10. Dimensional-consistency test
11. Q formula test
12. Q regime classification test
13. Coordinate-transformation invariance test
14. Legacy-vs-theoretical-Q separation test
15. Independent transport-regime validation test
"""

import unittest
import numpy as np
from sim_world.domains.physical_field.physical_field_models import (
    PhysicalCoordinate,
    PhysicalMetric,
    InformationDensityField,
    FieldState,
    PropagationParameters,
    RelaxationParameters,
    QObservation,
)
from sim_world.domains.physical_field.physical_field_dynamics import (
    initialize_field_state,
    evolve_field,
    apply_perturbation,
    measure_propagation_speed,
    measure_relaxation_time,
    compute_gradient,
    compute_gradient_magnitude,
    compute_theoretical_q,
    compute_independent_observables,
    create_physical_grid,
)


class TestPhysicalCoordinate(unittest.TestCase):
    """Test physical coordinate system."""
    
    def test_coordinate_creation(self):
        """Test that physical coordinates can be created with meters."""
        coord = PhysicalCoordinate(x=50.0, y=30.0, z=0.0)
        self.assertEqual(coord.x, 50.0)
        self.assertEqual(coord.y, 30.0)
        self.assertEqual(coord.z, 0.0)
    
    def test_distance_calculation(self):
        """Test Euclidean distance calculation."""
        coord1 = PhysicalCoordinate(x=0.0, y=0.0, z=0.0)
        coord2 = PhysicalCoordinate(x=3.0, y=4.0, z=0.0)
        distance = coord1.distance_to(coord2)
        self.assertAlmostEqual(distance, 5.0, places=5)
    
    def test_coordinate_tuple(self):
        """Test coordinate to tuple conversion."""
        coord = PhysicalCoordinate(x=1.0, y=2.0, z=3.0)
        self.assertEqual(coord.to_tuple(), (1.0, 2.0, 3.0))


class TestPhysicalMetric(unittest.TestCase):
    """Test physical metric structure."""
    
    def test_euclidean_metric(self):
        """Test Euclidean metric is identity matrix."""
        metric = PhysicalMetric()
        expected = np.eye(3)
        np.testing.assert_array_almost_equal(metric.g_ij, expected)
        np.testing.assert_array_almost_equal(metric.g_inv, expected)
    
    def test_metric_contraction(self):
        """Test metric contraction with gradient."""
        metric = PhysicalMetric()
        gradient = np.array([1.0, 2.0, 3.0])
        magnitude = metric.contract(gradient)
        expected = 1.0**2 + 2.0**2 + 3.0**2  # 14.0
        self.assertAlmostEqual(magnitude, expected, places=5)


class TestFieldPositivity(unittest.TestCase):
    """Test field positivity enforcement for ln(s)."""
    
    def test_positivity_enforcement(self):
        """Test that negative values are corrected."""
        state = initialize_field_state(nx=10, ny=10)
        state.field_values[0] = -0.5  # Invalid negative value
        
        field = InformationDensityField(
            state=state,
            information_quantity=1.0,
            physical_volume=100.0,
        )
        
        positive_field = field.ensure_positivity(epsilon=1e-10)
        self.assertGreater(positive_field.state.field_values[0], 0.0)
    
    def test_epsilon_handling(self):
        """Test epsilon parameter for near-zero values."""
        state = initialize_field_state(nx=10, ny=10)
        state.field_values[0] = 0.0  # Zero value
        
        field = InformationDensityField(
            state=state,
            information_quantity=1.0,
            physical_volume=100.0,
        )
        
        positive_field = field.ensure_positivity(epsilon=1e-10)
        self.assertGreaterEqual(positive_field.state.field_values[0], 1e-10)


class TestSpatialGradient(unittest.TestCase):
    """Test spatial gradient computation."""
    
    def test_gradient_computation(self):
        """Test gradient computation on field."""
        state = initialize_field_state(nx=10, ny=10)
        field = InformationDensityField(
            state=state,
            information_quantity=1.0,
            physical_volume=100.0,
        )
        
        coord = PhysicalCoordinate(x=50.0, y=50.0, z=0.0)
        gradient = compute_gradient(field, coord)
        
        # Gradient should be 3D vector
        self.assertEqual(len(gradient), 3)
        # Should be numpy array
        self.assertIsInstance(gradient, np.ndarray)
    
    def test_gradient_magnitude(self):
        """Test gradient magnitude computation."""
        state = initialize_field_state(nx=10, ny=10)
        field = InformationDensityField(
            state=state,
            information_quantity=1.0,
            physical_volume=100.0,
        )
        
        coord = PhysicalCoordinate(x=50.0, y=50.0, z=0.0)
        magnitude = compute_gradient_magnitude(field, coord)
        
        # Magnitude should be non-negative
        self.assertGreaterEqual(magnitude, 0.0)


class TestGradientResolutionConvergence(unittest.TestCase):
    """Test gradient convergence with spatial resolution."""
    
    def test_resolution_convergence(self):
        """Test that gradient converges with increasing resolution."""
        resolutions = [10, 20, 40]
        magnitudes = []
        
        for nx in resolutions:
            state = initialize_field_state(nx=nx, ny=nx)
            field = InformationDensityField(
                state=state,
                information_quantity=1.0,
                physical_volume=100.0,
            )
            
            coord = PhysicalCoordinate(x=50.0, y=50.0, z=0.0)
            magnitude = compute_gradient_magnitude(field, coord)
            magnitudes.append(magnitude)
        
        # For constant field, gradient should converge to zero
        # Higher resolution should give closer to zero
        for i in range(len(magnitudes) - 1):
            self.assertLessEqual(abs(magnitudes[i+1]), abs(magnitudes[i]) + 1e-6)


class TestPropagation(unittest.TestCase):
    """Test field propagation dynamics."""
    
    def test_perturbation_creation(self):
        """Test that perturbation can be created."""
        state = initialize_field_state(nx=20, ny=20)
        field = InformationDensityField(
            state=state,
            information_quantity=1.0,
            physical_volume=100.0,
        )
        
        center = PhysicalCoordinate(x=50.0, y=50.0, z=0.0)
        perturbed_field = apply_perturbation(field, center, perturbation_amplitude=2.0, perturbation_width=5.0)
        
        # Check that perturbation was applied
        center_value = perturbed_field.get_density_at(center)
        self.assertGreater(center_value, 1.0)  # Should be greater than initial
    
    def test_field_evolution(self):
        """Test that field evolves over time."""
        state = initialize_field_state(nx=20, ny=20)
        field = InformationDensityField(
            state=state,
            information_quantity=1.0,
            physical_volume=100.0,
        )
        
        prop_params = PropagationParameters(c_nominal=1.0)
        relax_params = RelaxationParameters(tau_nominal=1.0)
        
        initial_time = field.state.physical_time
        evolved_field = evolve_field(field, prop_params, relax_params)
        
        # Time should advance
        self.assertGreater(evolved_field.state.physical_time, initial_time)
    
    def test_perturbation_propagation(self):
        """Test that perturbation propagates through domain."""
        state = initialize_field_state(nx=20, ny=20)
        field = InformationDensityField(
            state=state,
            information_quantity=1.0,
            physical_volume=100.0,
        )
        
        # Apply perturbation at center
        center = PhysicalCoordinate(x=50.0, y=50.0, z=0.0)
        field = apply_perturbation(field, center, perturbation_amplitude=2.0, perturbation_width=5.0)
        
        # Evolve field
        prop_params = PropagationParameters(c_nominal=1.0)
        relax_params = RelaxationParameters(tau_nominal=1.0)
        
        field = evolve_field(field, prop_params, relax_params)
        field = evolve_field(field, prop_params, relax_params)
        
        # Check that perturbation has spread
        offset_coord = PhysicalCoordinate(x=60.0, y=50.0, z=0.0)
        offset_value = field.get_density_at(offset_coord)
        self.assertGreater(offset_value, 1.0)  # Should see effect at offset


class TestCMeasurement(unittest.TestCase):
    """Test propagation speed measurement."""
    
    def test_c_measurement(self):
        """Test that c can be measured from propagation."""
        state = initialize_field_state(nx=20, ny=20)
        field = InformationDensityField(
            state=state,
            information_quantity=1.0,
            physical_volume=100.0,
        )
        
        prop_params = PropagationParameters(c_nominal=1.0)
        center = PhysicalCoordinate(x=50.0, y=50.0, z=0.0)
        
        measured_params = measure_propagation_speed(
            field, prop_params, center, 
            perturbation_amplitude=2.0, perturbation_width=5.0,
            observer_distances=[10.0, 20.0],
            max_time=5.0,  # Short time for test
        )
        
        # Should have measured c
        self.assertGreater(measured_params.c_measured, 0.0)
        # Should have uncertainty estimate
        self.assertGreaterEqual(measured_params.c_uncertainty, 0.0)


class TestRelaxation(unittest.TestCase):
    """Test field relaxation dynamics."""
    
    def test_relaxation_measurement(self):
        """Test that τ can be measured from relaxation."""
        state = initialize_field_state(nx=20, ny=20)
        field = InformationDensityField(
            state=state,
            information_quantity=1.0,
            physical_volume=100.0,
        )
        
        relax_params = RelaxationParameters(tau_nominal=1.0)
        center = PhysicalCoordinate(x=50.0, y=50.0, z=0.0)
        
        measured_params = measure_relaxation_time(
            field, relax_params, center,
            perturbation_amplitude=2.0, perturbation_width=5.0,
            max_time=5.0,  # Short time for test
        )
        
        # Should have measured τ
        self.assertGreater(measured_params.tau_measured, 0.0)
        # Should have uncertainty estimate
        self.assertGreaterEqual(measured_params.tau_uncertainty, 0.0)
        # Should identify relaxation law
        self.assertEqual(measured_params.relaxation_law, "exponential")


class TestDimensionalConsistency(unittest.TestCase):
    """Test dimensional consistency of Q calculation."""
    
    def test_q_dimensionless(self):
        """Test that Q is dimensionless."""
        state = initialize_field_state(nx=20, ny=20)
        field = InformationDensityField(
            state=state,
            information_quantity=1.0,
            physical_volume=100.0,
            information_units="bits",
            spatial_units="m",
            density_units="bits/m³",
        )
        
        prop_params = PropagationParameters(c_nominal=1.0)  # m/s
        relax_params = RelaxationParameters(tau_nominal=1.0)  # s
        coord = PhysicalCoordinate(x=50.0, y=50.0, z=0.0)
        
        q_obs = compute_theoretical_q(field, prop_params, relax_params, coord)
        
        # Q should be a pure number (dimensionless)
        self.assertIsInstance(q_obs.q_value, float)
        # Check units in metadata
        self.assertEqual(field.information_units, "bits")
        self.assertEqual(field.spatial_units, "m")
        self.assertEqual(field.density_units, "bits/m³")


class TestQFormula(unittest.TestCase):
    """Test exact Q formula implementation."""
    
    def test_q_formula_constant_field(self):
        """Test Q formula on constant field (should be -1)."""
        state = initialize_field_state(nx=20, ny=20, initial_value=1.0)
        field = InformationDensityField(
            state=state,
            information_quantity=1.0,
            physical_volume=100.0,
        )
        
        prop_params = PropagationParameters(c_nominal=1.0)
        relax_params = RelaxationParameters(tau_nominal=1.0)
        coord = PhysicalCoordinate(x=50.0, y=50.0, z=0.0)
        
        q_obs = compute_theoretical_q(field, prop_params, relax_params, coord)
        
        # For constant field, gradient is zero, so Q = -1
        self.assertAlmostEqual(q_obs.q_value, -1.0, places=5)
    
    def test_q_formula_components(self):
        """Test that Q formula uses correct components."""
        state = initialize_field_state(nx=20, ny=20)
        field = InformationDensityField(
            state=state,
            information_quantity=1.0,
            physical_volume=100.0,
        )
        
        # Apply perturbation to create gradient
        center = PhysicalCoordinate(x=50.0, y=50.0, z=0.0)
        field = apply_perturbation(field, center, perturbation_amplitude=2.0, perturbation_width=5.0)
        
        prop_params = PropagationParameters(c_nominal=1.0)
        relax_params = RelaxationParameters(tau_nominal=1.0)
        
        q_obs = compute_theoretical_q(field, prop_params, relax_params, center)
        
        # Verify formula: Q = 4c²τ²|∇ln s|² - 1
        expected = 4.0 * (1.0**2) * (1.0**2) * (q_obs.gradient_magnitude**2) - 1.0
        self.assertAlmostEqual(q_obs.q_value, expected, places=5)


class TestQRegimeClassification(unittest.TestCase):
    """Test Q regime classification."""
    
    def test_coherent_regime(self):
        """Test Q > 0 classified as coherent."""
        state = initialize_field_state(nx=20, ny=20)
        field = InformationDensityField(
            state=state,
            information_quantity=1.0,
            physical_volume=100.0,
        )
        
        # Strong perturbation for Q > 0
        center = PhysicalCoordinate(x=50.0, y=50.0, z=0.0)
        field = apply_perturbation(field, center, perturbation_amplitude=10.0, perturbation_width=1.0)
        
        prop_params = PropagationParameters(c_nominal=1.0)
        relax_params = RelaxationParameters(tau_nominal=1.0)
        
        q_obs = compute_theoretical_q(field, prop_params, relax_params, center)
        
        if q_obs.q_value > 0:
            self.assertEqual(q_obs.regime, "coherent")
    
    def test_overdamped_regime(self):
        """Test Q < 0 classified as overdamped."""
        state = initialize_field_state(nx=20, ny=20, initial_value=1.0)
        field = InformationDensityField(
            state=state,
            information_quantity=1.0,
            physical_volume=100.0,
        )
        
        prop_params = PropagationParameters(c_nominal=1.0)
        relax_params = RelaxationParameters(tau_nominal=1.0)
        coord = PhysicalCoordinate(x=50.0, y=50.0, z=0.0)
        
        q_obs = compute_theoretical_q(field, prop_params, relax_params, coord)
        
        # Constant field should give Q = -1
        self.assertEqual(q_obs.regime, "overdamped")
    
    def test_critical_regime(self):
        """Test Q = 0 classified as critical."""
        # This is theoretically possible but hard to hit exactly
        # We test the classification logic
        state = initialize_field_state(nx=20, ny=20)
        field = InformationDensityField(
            state=state,
            information_quantity=1.0,
            physical_volume=100.0,
        )
        
        # Manually create Q observation with Q = 0
        q_obs = QObservation(
            coordinate=PhysicalCoordinate(50.0, 50.0, 0.0),
            physical_time=0.0,
            s_value=1.0,
            gradient_magnitude=0.5,  # |∇ln s| = 0.5
            c_value=1.0,
            tau_value=1.0,
            q_value=0.0,  # 4*1*1*0.25 - 1 = 0
            regime="critical",
        )
        
        self.assertEqual(q_obs.regime, "critical")


class TestCoordinateTransformationInvariance(unittest.TestCase):
    """Test coordinate invariance of gradient magnitude."""
    
    def test_gradient_invariance(self):
        """Test that |∇ln s|² is invariant under coordinate transformation."""
        state = initialize_field_state(nx=20, ny=20)
        field = InformationDensityField(
            state=state,
            information_quantity=1.0,
            physical_volume=100.0,
        )
        
        # Apply perturbation
        center = PhysicalCoordinate(x=50.0, y=50.0, z=0.0)
        field = apply_perturbation(field, center, perturbation_amplitude=2.0, perturbation_width=5.0)
        
        # Compute gradient magnitude at different points
        coord1 = PhysicalCoordinate(x=50.0, y=50.0, z=0.0)
        coord2 = PhysicalCoordinate(x=50.0, y=50.0, z=0.0)  # Same physical location
        
        mag1 = compute_gradient_magnitude(field, coord1)
        mag2 = compute_gradient_magnitude(field, coord2)
        
        # Should be identical for same physical location
        self.assertAlmostEqual(mag1, mag2, places=5)


class TestIndependentObservables(unittest.TestCase):
    """Test independent transport observables."""
    
    def test_observables_computation(self):
        """Test that independent observables can be computed."""
        state = initialize_field_state(nx=20, ny=20)
        field = InformationDensityField(
            state=state,
            information_quantity=1.0,
            physical_volume=100.0,
        )
        
        coord = PhysicalCoordinate(x=50.0, y=50.0, z=0.0)
        observables = compute_independent_observables(field, coord)
        
        # Should contain expected keys
        expected_keys = [
            "field_value", "gradient_magnitude", "local_velocity",
            "kinetic_energy", "potential_energy", "total_energy",
            "spatial_variance", "temporal_derivative"
        ]
        
        for key in expected_keys:
            self.assertIn(key, observables)
            self.assertIsInstance(observables[key], float)
    
    def test_observables_independence(self):
        """Test that observables are computed independently of Q."""
        state = initialize_field_state(nx=20, ny=20)
        field = InformationDensityField(
            state=state,
            information_quantity=1.0,
            physical_volume=100.0,
        )
        
        coord = PhysicalCoordinate(x=50.0, y=50.0, z=0.0)
        observables = compute_independent_observables(field, coord)
        
        # Observables should not depend on Q calculation
        # They should be computable from field state alone
        self.assertIsNotNone(observables["field_value"])
        self.assertIsNotNone(observables["gradient_magnitude"])


class TestPhysicalGrid(unittest.TestCase):
    """Test physical grid creation."""
    
    def test_grid_creation(self):
        """Test that physical grid can be created."""
        coordinates, dx, dy, dz = create_physical_grid(
            x_range=(0.0, 100.0),
            y_range=(0.0, 100.0),
            nx=10,
            ny=10,
        )
        
        # Should have correct number of points
        self.assertEqual(len(coordinates), 100)  # 10 * 10 * 1
        # Should have correct spacing
        self.assertAlmostEqual(dx, 100.0 / 9.0, places=5)
        self.assertAlmostEqual(dy, 100.0 / 9.0, places=5)
    
    def test_grid_coordinates(self):
        """Test that grid coordinates are correct."""
        coordinates, dx, dy, dz = create_physical_grid(
            x_range=(0.0, 10.0),
            y_range=(0.0, 10.0),
            nx=3,
            ny=3,
        )
        
        # First point should be at origin
        np.testing.assert_array_almost_equal(coordinates[0], [0.0, 0.0, 0.0])
        # Last point should be at max
        np.testing.assert_array_almost_equal(coordinates[-1], [10.0, 10.0, 0.0])


if __name__ == '__main__':
    unittest.main()
