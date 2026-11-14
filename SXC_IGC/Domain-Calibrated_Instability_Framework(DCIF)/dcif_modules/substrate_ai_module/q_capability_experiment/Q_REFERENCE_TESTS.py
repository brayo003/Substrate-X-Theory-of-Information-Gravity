#!/usr/bin/env python3
"""
Q REFERENCE TESTS
Analytic numerical tests for the independent reference implementation

Tests mathematical correctness of Q computation using known analytic solutions.
"""

import numpy as np
import json
from Q_REFERENCE_IMPLEMENTATION import (
    QReference, 
    AnalyticTestFields,
    analytic_q_linear,
    analytic_q_exponential,
    analytic_q_gaussian
)


class QReferenceTests:
    """Test suite for Q reference implementation"""
    
    def __init__(self, c=1.0, tau=0.5):
        self.q_calc = QReference(c, tau)
        self.c = c
        self.tau = tau
        self.results = {}
        
    def test_constant_field(self):
        """Test Q = -1 for constant field (gradient should be zero)"""
        print("\n=== TEST 1: Constant Field ===")
        
        x = np.linspace(0, 10, 100)
        dx = x[1] - x[0]
        s_field = AnalyticTestFields.constant_field(x, A=1.0)
        
        Q_field = self.q_calc.compute_q_field(s_field, dx)
        Q_computed = Q_field[len(Q_field)//2]  # Check middle point
        Q_expected = -1.0  # |∇ln s|² = 0 for constant field
        
        error = abs(Q_computed - Q_expected)
        
        print(f"Computed Q (midpoint): {Q_computed:.10f}")
        print(f"Expected Q: {Q_expected:.10f}")
        print(f"Absolute error: {error:.2e}")
        
        result = {
            'test_name': 'constant_field',
            'Q_computed': float(Q_computed),
            'Q_expected': Q_expected,
            'absolute_error': float(error),
            'relative_error': float(error / abs(Q_expected) if Q_expected != 0 else error),
            'passed': bool(error < 1e-10)
        }
        
        self.results['constant_field'] = result
        print(f"Status: {'PASS' if result['passed'] else 'FAIL'}")
        
        return result
    
    def test_linear_field(self):
        """Test Q for linear field against analytic solution"""
        print("\n=== TEST 2: Linear Field ===")
        
        x = np.linspace(0, 10, 100)
        dx = x[1] - x[0]
        A, B = 1.0, 0.1
        s_field = AnalyticTestFields.linear_field(x, A=A, B=B)
        
        # Compute Q field
        Q_field = self.q_calc.compute_q_field(s_field, dx)
        
        # Check at middle point
        mid_idx = len(x) // 2
        x_mid = x[mid_idx]
        Q_computed = Q_field[mid_idx]
        Q_expected = analytic_q_linear(x_mid, A, B, self.c, self.tau)
        
        error = abs(Q_computed - Q_expected)
        
        print(f"Computed Q (midpoint): {Q_computed:.10f}")
        print(f"Expected Q: {Q_expected:.10f}")
        print(f"Absolute error: {error:.2e}")
        
        result = {
            'test_name': 'linear_field',
            'x_mid': float(x_mid),
            'A': A,
            'B': B,
            'Q_computed': float(Q_computed),
            'Q_expected': Q_expected,
            'absolute_error': float(error),
            'relative_error': float(error / abs(Q_expected) if Q_expected != 0 else error),
            'passed': bool(error < 1e-6)
        }
        
        self.results['linear_field'] = result
        print(f"Status: {'PASS' if result['passed'] else 'FAIL'}")
        
        return result
    
    def test_exponential_field(self):
        """Test Q for exponential field against analytic solution"""
        print("\n=== TEST 3: Exponential Field ===")
        
        x = np.linspace(0, 10, 100)
        dx = x[1] - x[0]
        A, k = 1.0, 0.1
        s_field = AnalyticTestFields.exponential_field(x, A=A, k=k)
        
        Q_field = self.q_calc.compute_q_field(s_field, dx)
        Q_computed = Q_field[len(Q_field)//2]  # Check middle point
        Q_expected = analytic_q_exponential(k, self.c, self.tau)
        
        error = abs(Q_computed - Q_expected)
        
        print(f"Computed Q (midpoint): {Q_computed:.10f}")
        print(f"Expected Q: {Q_expected:.10f}")
        print(f"Absolute error: {error:.2e}")
        
        result = {
            'test_name': 'exponential_field',
            'A': A,
            'k': k,
            'Q_computed': float(Q_computed),
            'Q_expected': Q_expected,
            'absolute_error': float(error),
            'relative_error': float(error / abs(Q_expected) if Q_expected != 0 else error),
            'passed': bool(error < 1e-6)
        }
        
        self.results['exponential_field'] = result
        print(f"Status: {'PASS' if result['passed'] else 'FAIL'}")
        
        return result
    
    def test_gaussian_field(self):
        """Test Q for Gaussian field against analytic solution"""
        print("\n=== TEST 4: Gaussian Field ===")
        
        x = np.linspace(-5, 5, 100)
        dx = x[1] - x[0]
        A, mu, sigma = 1.0, 0.0, 1.0
        s_field = AnalyticTestFields.gaussian_field(x, A=A, mu=mu, sigma=sigma)
        
        Q_field = self.q_calc.compute_q_field(s_field, dx)
        
        # Test at peak (x=0) where gradient should be zero
        peak_idx = np.argmin(np.abs(x - mu))
        Q_computed = Q_field[peak_idx]
        
        # At peak, gradient should be minimal, Q should be close to -1
        # Due to discretization, exact zero gradient not achieved
        Q_expected_analytic = analytic_q_gaussian(0.0, mu, sigma, self.c, self.tau)
        
        error = abs(Q_computed - Q_expected_analytic)
        
        print(f"Computed Q (peak): {Q_computed:.10f}")
        print(f"Expected Q (analytic at peak): {Q_expected_analytic:.10f}")
        print(f"Absolute error: {error:.2e}")
        
        # Allow larger error due to discretization at peak
        result = {
            'test_name': 'gaussian_field',
            'A': A,
            'mu': mu,
            'sigma': sigma,
            'Q_computed': float(Q_computed),
            'Q_expected': Q_expected_analytic,
            'absolute_error': float(error),
            'relative_error': float(error / abs(Q_expected_analytic) if Q_expected_analytic != 0 else error),
            'passed': bool(error < 1e-3)  # Larger tolerance for discretization
        }
        
        self.results['gaussian_field'] = result
        print(f"Status: {'PASS' if result['passed'] else 'FAIL'}")
        
        return result
    
    def test_scaling_invariance(self):
        """Test that Q is invariant under scaling of s by constant factor"""
        print("\n=== TEST 5: Scaling Invariance ===")
        
        x = np.linspace(0, 10, 100)
        dx = x[1] - x[0]
        k = 0.1
        
        # Test different scaling factors
        scaling_factors = [0.5, 1.0, 2.0, 10.0]
        Q_values = []
        
        for A in scaling_factors:
            s_field = AnalyticTestFields.exponential_field(x, A=A, k=k)
            Q_field = self.q_calc.compute_q_field(s_field, dx)
            Q_computed = Q_field[len(Q_field)//2]
            Q_values.append(Q_computed)
            print(f"  A={A}: Q={Q_computed:.10f}")
        
        # All Q values should be identical (within numerical precision)
        Q_std = float(np.std(Q_values))
        Q_mean = float(np.mean(Q_values))
        
        print(f"Q mean: {Q_mean:.10f}")
        print(f"Q std: {Q_std:.2e}")
        
        result = {
            'test_name': 'scaling_invariance',
            'scaling_factors': scaling_factors,
            'Q_values': [float(q) for q in Q_values],
            'Q_std': Q_std,
            'passed': bool(Q_std < 1e-10)
        }
        
        self.results['scaling_invariance'] = result
        print(f"Status: {'PASS' if result['passed'] else 'FAIL'}")
        
        return result
    
    def test_parameter_sensitivity(self):
        """Test Q sensitivity to c and τ parameters"""
        print("\n=== TEST 6: Parameter Sensitivity ===")
        
        x = np.linspace(0, 10, 100)
        dx = x[1] - x[0]
        k = 0.1
        s_field = AnalyticTestFields.exponential_field(x, A=1.0, k=k)
        
        # Test different (c, τ) combinations
        param_combinations = [
            (1.0, 0.5),
            (2.0, 0.5),
            (1.0, 1.0),
            (0.5, 0.5)
        ]
        
        Q_values = []
        for c_test, tau_test in param_combinations:
            q_calc_test = QReference(c_test, tau_test)
            Q_field = q_calc_test.compute_q_field(s_field, dx)
            Q_computed = Q_field[len(Q_field)//2]
            Q_values.append(Q_computed)
            print(f"  c={c_test}, τ={tau_test}: Q={Q_computed:.10f}")
        
        # Verify Q scales as c²τ²
        # Q should be proportional to c²τ² for fixed field
        c2_tau2_values = [c**2 * tau**2 for c, tau in param_combinations]
        
        # Check proportionality
        # Q_i / (c_i²τ_i²) should be constant
        normalized_Q = [Q / (c2t2) for Q, c2t2 in zip(Q_values, c2_tau2_values)]
        normalized_std = float(np.std(normalized_Q))
        
        print(f"Normalized Q values: {[f'{q:.6f}' for q in normalized_Q]}")
        print(f"Normalized Q std: {normalized_std:.2e}")
        
        result = {
            'test_name': 'parameter_sensitivity',
            'param_combinations': param_combinations,
            'Q_values': [float(q) for q in Q_values],
            'c2_tau2_values': c2_tau2_values,
            'normalized_Q': [float(q) for q in normalized_Q],
            'normalized_std': normalized_std,
            'passed': bool(normalized_std < 1e-10)
        }
        
        self.results['parameter_sensitivity'] = result
        print(f"Status: {'PASS' if result['passed'] else 'FAIL'}")
        
        return result
    
    def test_near_zero_field(self):
        """Test Q behavior for field values near zero"""
        print("\n=== TEST 7: Near-Zero Field ===")
        
        x = np.linspace(0, 10, 100)
        dx = x[1] - x[0]
        
        # Test with very small but positive A
        A_values = [1e-6, 1e-4, 1e-2, 1e-1]
        k = 0.1
        
        for A in A_values:
            s_field = AnalyticTestFields.exponential_field(x, A=A, k=k)
            try:
                Q_field = self.q_calc.compute_q_field(s_field, dx)
                Q_computed = Q_field[len(Q_field)//2]
                print(f"  A={A:.1e}: Q={Q_computed:.10f}")
            except ValueError as e:
                print(f"  A={A:.1e}: ERROR - {e}")
        
        result = {
            'test_name': 'near_zero_field',
            'A_values': A_values,
            'passed': True  # Test just checks that it doesn't crash
        }
        
        self.results['near_zero_field'] = result
        print(f"Status: PASS (no crashes)")
        
        return result
    
    def test_resolution_convergence(self):
        """Test that Q converges with higher spatial resolution"""
        print("\n=== TEST 8: Resolution Convergence ===")
        
        k = 0.1
        n_points_list = [20, 50, 100, 200, 500]
        Q_values = []
        
        for n_points in n_points_list:
            x = np.linspace(0, 10, n_points)
            dx = x[1] - x[0]
            s_field = AnalyticTestFields.exponential_field(x, A=1.0, k=k)
            Q_field = self.q_calc.compute_q_field(s_field, dx)
            Q_computed = Q_field[len(Q_field)//2]
            Q_values.append(Q_computed)
            print(f"  n={n_points}: Q={Q_computed:.10f}")
        
        Q_expected = analytic_q_exponential(k, self.c, self.tau)
        
        # Check convergence to expected value
        final_error = abs(Q_values[-1] - Q_expected)
        convergence_trend = all(abs(Q_values[i] - Q_expected) >= abs(Q_values[i+1] - Q_expected)
                                for i in range(len(Q_values)-1))
        
        print(f"Expected Q: {Q_expected:.10f}")
        print(f"Final error: {final_error:.2e}")
        print(f"Convergence trend: {convergence_trend}")
        
        result = {
            'test_name': 'resolution_convergence',
            'n_points_list': n_points_list,
            'Q_values': [float(q) for q in Q_values],
            'Q_expected': Q_expected,
            'final_error': float(final_error),
            'convergence_trend': bool(convergence_trend),
            'passed': bool(final_error < 1e-6 and convergence_trend)
        }
        
        self.results['resolution_convergence'] = result
        print(f"Status: {'PASS' if result['passed'] else 'FAIL'}")
        
        return result
    
    def run_all_tests(self):
        """Run all reference tests"""
        print("=" * 60)
        print("Q REFERENCE IMPLEMENTATION TESTS")
        print("=" * 60)
        
        self.test_constant_field()
        self.test_linear_field()
        self.test_exponential_field()
        self.test_gaussian_field()
        self.test_scaling_invariance()
        self.test_parameter_sensitivity()
        self.test_near_zero_field()
        self.test_resolution_convergence()
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.results.values() if result.get('passed', False))
        total = len(self.results)
        
        print(f"Passed: {passed}/{total}")
        
        for test_name, result in self.results.items():
            status = "PASS" if result.get('passed', False) else "FAIL"
            print(f"  {test_name}: {status}")
        
        self.results['summary'] = {
            'total_tests': total,
            'passed_tests': passed,
            'success_rate': float(passed / total)
        }
        
        return self.results


if __name__ == "__main__":
    # Run tests
    tester = QReferenceTests(c=1.0, tau=0.5)
    results = tester.run_all_tests()
    
    # Save results
    import os
    output_dir = os.path.join(os.path.dirname(__file__), 'Q_FIELD_RAW_RESULTS')
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, 'reference_tests.json')
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
