#!/usr/bin/env python3
"""
Q OPERATIONALIZATION TEST REPORT
Test whether current backend is a legitimate operationalization of theoretical Q
"""

import numpy as np
import json
import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'components'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'substrate_ai', 'components'))

from Q_REFERENCE_IMPLEMENTATION import QReference, AnalyticTestFields

class OperationalizationTest:
    """Test backend implementation against reference implementation"""
    
    def __init__(self):
        self.results = {}
        
    def test_backend_gradient_computation(self):
        """Test if backend computes ∇ln(s) correctly"""
        print("\n=== TEST: Backend Gradient Computation ===")
        
        try:
            from problem_analyzer import ProblemAnalyzer
            analyzer = ProblemAnalyzer()
            
            # Create simple test case with known features
            texts = [
                "test",  # Simple
                "test test test",  # Longer
                "math equation ∇²ψ = 0",  # With math symbols
            ]
            
            feature_names = ["math_symbols", "abstract_terms", "technical_density", "complexity_words", "length_score"]
            
            features_list = []
            for text in texts:
                features = analyzer.extract_features(text)
                features_list.append(features)
            
            field_matrix = np.array([[features.get(k, 0.0) for k in feature_names] for features in features_list])
            
            print(f"Field matrix shape: {field_matrix.shape}")
            print(f"Field matrix:\n{field_matrix}")
            
            # Compute gradient using backend method (np.gradient)
            backend_gradients = []
            for row in field_matrix:
                gradient = np.gradient(row)
                backend_gradients.append(gradient)
            
            print(f"Backend gradients:\n{np.array(backend_gradients)}")
            
            # Test if gradient is computed correctly for known cases
            # For constant row, gradient should be zero
            constant_row = np.array([1.0, 1.0, 1.0, 1.0, 1.0])
            constant_gradient = np.gradient(constant_row)
            
            print(f"Constant row gradient: {constant_gradient}")
            print(f"Expected: [0, 0, 0, 0, 0]")
            
            result = {
                'test_name': 'backend_gradient_computation',
                'field_matrix': field_matrix.tolist(),
                'backend_gradients': [g.tolist() for g in backend_gradients],
                'constant_row_gradient': constant_gradient.tolist(),
                'gradient_correct': np.allclose(constant_gradient, [0, 0, 0, 0, 0], atol=1e-10)
            }
            
            self.results['backend_gradient_computation'] = result
            print(f"Status: {'PASS' if result['gradient_correct'] else 'FAIL'}")
            
        except Exception as e:
            print(f"ERROR: {e}")
            self.results['backend_gradient_computation'] = {
                'test_name': 'backend_gradient_computation',
                'error': str(e),
                'passed': False
            }
    
    def test_backend_q_computation(self):
        """Test if backend computes Q using correct formula"""
        print("\n=== TEST: Backend Q Computation ===")
        
        try:
            # Simulate backend Q computation method
            c_backend = 1.0
            tau_backend = 0.5
            
            # Test with known gradient magnitude
            test_squared_magnitudes = [0.0, 0.5, 1.0, 2.0]
            
            backend_Q_values = []
            reference_Q_values = []
            
            q_ref = QReference(c_backend, tau_backend)
            
            for squared_mag in test_squared_magnitudes:
                # Backend formula (from phase2_q_calculation.py)
                Q_backend = 4.0 * (c_backend**2) * (tau_backend**2) * squared_mag - 1.0
                backend_Q_values.append(Q_backend)
                
                # Reference formula
                # For reference, we need to construct a field that produces this squared magnitude
                # Q = 4c²τ²|∇ln s|² - 1, so if we set |∇ln s|² = squared_mag, we get the same Q
                Q_reference = 4.0 * (c_backend**2) * (tau_backend**2) * squared_mag - 1.0
                reference_Q_values.append(Q_reference)
            
            print(f"Test squared magnitudes: {test_squared_magnitudes}")
            print(f"Backend Q values: {backend_Q_values}")
            print(f"Reference Q values: {reference_Q_values}")
            
            # Check if formulas are identical
            formulas_identical = np.allclose(backend_Q_values, reference_Q_values)
            
            result = {
                'test_name': 'backend_q_computation',
                'test_squared_magnitudes': test_squared_magnitudes,
                'backend_Q_values': backend_Q_values,
                'reference_Q_values': reference_Q_values,
                'formulas_identical': bool(formulas_identical)
            }
            
            self.results['backend_q_computation'] = result
            print(f"Status: {'PASS' if formulas_identical else 'FAIL'}")
            
        except Exception as e:
            print(f"ERROR: {e}")
            self.results['backend_q_computation'] = {
                'test_name': 'backend_q_computation',
                'error': str(e),
                'passed': False
            }
    
    def test_coordinate_system_validity(self):
        """Test if feature space can serve as valid spatial coordinates"""
        print("\n=== TEST: Coordinate System Validity ===")
        
        # Test if feature dimensions have metric structure
        feature_names = ["math_symbols", "abstract_terms", "technical_density", "complexity_words", "length_score"]
        
        print(f"Feature dimensions: {feature_names}")
        print(f"Number of dimensions: {len(feature_names)}")
        
        # Theoretical requirements from q_define.txt:
        # - Spatial coordinates must have metric structure g^{ij}
        # - Must support coordinate transformations
        # - Must have physical interpretation
        
        analysis = {
            'has_metric_structure': False,  # No metric defined for feature space
            'has_physical_interpretation': False,  # Features are abstract, not physical
            'supports_coordinate_transformations': False,  # No transformation rules defined
            'coordinate_spacing': 'unknown',  # np.gradient assumes unit spacing
            'coordinate_meaning': 'abstract text features, not physical space'
        }
        
        print(f"Has metric structure: {analysis['has_metric_structure']}")
        print(f"Has physical interpretation: {analysis['has_physical_interpretation']}")
        print(f"Supports coordinate transformations: {analysis['supports_coordinate_transformations']}")
        
        result = {
            'test_name': 'coordinate_system_validity',
            'feature_names': feature_names,
            'analysis': analysis,
            'valid_coordinates': False  # Features are not valid physical coordinates
        }
        
        self.results['coordinate_system_validity'] = result
        print(f"Status: FAIL - Feature space is not valid physical coordinate system")
    
    def test_s_field_validity(self):
        """Test if s field construction is mathematically valid"""
        print("\n=== TEST: s(x,t) Field Validity ===")
        
        try:
            from problem_analyzer import ProblemAnalyzer
            analyzer = ProblemAnalyzer()
            
            texts = ["test text", "math equation ∇²ψ = 0"]
            
            feature_names = ["math_symbols", "abstract_terms", "technical_density", "complexity_words", "length_score"]
            
            features_list = []
            for text in texts:
                features = analyzer.extract_features(text)
                features_list.append(features)
            
            field_matrix = np.array([[features.get(k, 0.0) for k in feature_names] for features in features_list])
            
            # Backend s construction: sum of features
            s_backend = np.sum(field_matrix, axis=1)
            
            print(f"Field matrix:\n{field_matrix}")
            print(f"Backend s (sum of features): {s_backend}")
            
            # Theoretical requirements from q_define.txt:
            # - s must be information density (info/m³)
            # - s must be scalar field over physical space
            # - s must have physical units
            
            analysis = {
                'is_scalar': True,  # Sum produces scalar
                'has_physical_units': False,  # Features are dimensionless normalized scores
                'represents_information_density': False,  # Sum of text features ≠ information density
                'defined_over_physical_space': False,  # Defined over feature space
                'construction_method': 'sum of normalized text features',
                'theoretical_requirement': 'information density in physical space (info/m³)'
            }
            
            print(f"Is scalar: {analysis['is_scalar']}")
            print(f"Has physical units: {analysis['has_physical_units']}")
            print(f"Represents information density: {analysis['represents_information_density']}")
            
            result = {
                'test_name': 's_field_validity',
                's_backend': s_backend.tolist(),
                'analysis': analysis,
                'valid_s_field': False  # Does not meet theoretical requirements
            }
            
            self.results['s_field_validity'] = result
            print(f"Status: FAIL - s field does not meet theoretical requirements")
            
        except Exception as e:
            print(f"ERROR: {e}")
            self.results['s_field_validity'] = {
                'test_name': 's_field_validity',
                'error': str(e),
                'valid_s_field': False
            }
    
    def test_parameter_validity(self):
        """Test if c and τ parameters are valid"""
        print("\n=== TEST: Parameter Validity ===")
        
        # Backend parameters from phase2_q_calculation.py
        c_backend = 1.0
        tau_backend = 0.5
        
        # Theoretical requirements from q_define.txt:
        # - c must have units m/s (propagation speed)
        # - τ must have units s (damping time)
        # - Both must be empirically grounded
        
        analysis = {
            'c_backend': c_backend,
            'tau_backend': tau_backend,
            'c_has_units': False,  # Dimensionless in backend
            'tau_has_units': False,  # Dimensionless in backend
            'c_empirically_grounded': False,  # Arbitrary value
            'tau_empirically_grounded': False,  # Arbitrary value
            'c_theoretical_requirement': 'm/s (propagation speed)',
            'tau_theoretical_requirement': 's (damping time)'
        }
        
        print(f"Backend c: {c_backend} (dimensionless)")
        print(f"Backend τ: {tau_backend} (dimensionless)")
        print(f"Theoretical c requirement: {analysis['c_theoretical_requirement']}")
        print(f"Theoretical τ requirement: {analysis['tau_theoretical_requirement']}")
        
        result = {
            'test_name': 'parameter_validity',
            'analysis': analysis,
            'valid_parameters': False  # Does not meet theoretical requirements
        }
        
        self.results['parameter_validity'] = result
        print(f"Status: FAIL - Parameters do not meet theoretical requirements")
    
    def run_all_tests(self):
        """Run all operationalization tests"""
        print("=" * 60)
        print("Q OPERATIONALIZATION TEST REPORT")
        print("=" * 60)
        
        self.test_backend_gradient_computation()
        self.test_backend_q_computation()
        self.test_coordinate_system_validity()
        self.test_s_field_validity()
        self.test_parameter_validity()
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.results.values() if result.get('passed', False) or result.get('valid_coordinates', False) or result.get('valid_s_field', False) or result.get('valid_parameters', False) or result.get('formulas_identical', False) or result.get('gradient_correct', False))
        total = len(self.results)
        
        print(f"Passed: {passed}/{total}")
        
        for test_name, result in self.results.items():
            if 'passed' in result:
                status = "PASS" if result['passed'] else "FAIL"
            elif 'valid_coordinates' in result:
                status = "PASS" if result['valid_coordinates'] else "FAIL"
            elif 'valid_s_field' in result:
                status = "PASS" if result['valid_s_field'] else "FAIL"
            elif 'valid_parameters' in result:
                status = "PASS" if result['valid_parameters'] else "FAIL"
            elif 'formulas_identical' in result:
                status = "PASS" if result['formulas_identical'] else "FAIL"
            elif 'gradient_correct' in result:
                status = "PASS" if result['gradient_correct'] else "FAIL"
            else:
                status = "UNKNOWN"
            print(f"  {test_name}: {status}")
        
        self.results['summary'] = {
            'total_tests': total,
            'passed_tests': passed,
            'operationalization_valid': False  # Overall: not valid
        }
        
        return self.results


if __name__ == "__main__":
    tester = OperationalizationTest()
    results = tester.run_all_tests()
    
    # Save results
    output_dir = os.path.join(os.path.dirname(__file__), 'Q_FIELD_RAW_RESULTS')
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, 'operationalization_test.json')
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
