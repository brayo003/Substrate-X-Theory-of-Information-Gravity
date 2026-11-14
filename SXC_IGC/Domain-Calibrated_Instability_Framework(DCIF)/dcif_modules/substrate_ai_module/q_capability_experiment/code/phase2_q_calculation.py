#!/usr/bin/env python3
"""
Q FIELD INSTANTIATION EXPERIMENT - Phase 2: Q Calculation Test
Tests whether theoretical Q can be calculated using constructed s(x,t)
"""

import sys
import os
import numpy as np
import json
from typing import List, Dict, Tuple
import time

# Add components to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'substrate_ai', 'components'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'substrate_ai'))

class QCalculationExperiment:
    """Test whether theoretical Q can be calculated"""
    
    def __init__(self):
        self.results = {
            'field_construction': None,
            'gradient_computation': None,
            'log_gradient_computation': None,
            'q_calculation': None,
            'regime_classification': None,
            'summary': {}
        }
        
    def construct_s_field(self):
        """Construct s(x,t) using feature space (from successful Phase 1 candidate)"""
        print("\n=== STEP 1: CONSTRUCT s(x,t) FIELD ===")
        
        try:
            from problem_analyzer import ProblemAnalyzer
            analyzer = ProblemAnalyzer()
            
            # Create temporal sequence
            texts = [
                "System is stable and coherent",
                "Processing complex input data",
                "Computing gradient field with high precision",
                "Detecting significant novelty in pattern",
                "Transition to unstable state",
                "System collapse imminent"
            ]
            
            features_list = []
            for text in texts:
                features = analyzer.extract_features(text)
                features_list.append(features)
                print(f"Text: '{text[:40]}...'")
                print(f"  Features: math={features.get('math_symbols',0):.2f}, tech={features.get('technical_density',0):.2f}, len={features.get('length_score',0):.2f}")
            
            # Construct field from features
            feature_names = ["math_symbols", "abstract_terms", "technical_density", "complexity_words", "length_score"]
            field_matrix = np.array([[features.get(k, 0.0) for k in feature_names] for features in features_list])
            
            print(f"\n--- Field Properties ---")
            print(f"Field shape: {field_matrix.shape} (temporal states x spatial dimensions)")
            print(f"Spatial coordinates: {feature_names}")
            print(f"Temporal range: 0-{len(texts)-1}")
            
            # Define s(x,t) as sum of normalized features (information density)
            s_field = np.sum(field_matrix, axis=1)  # scalar at each timestep
            print(f"s(x,t) shape: {s_field.shape}")
            print(f"s(x,t) values: {s_field}")
            
            result = {
                'success': True,
                'field_shape': list(field_matrix.shape),
                's_field_shape': list(s_field.shape),
                's_field_values': s_field.tolist(),
                'spatial_coordinates': feature_names,
                'temporal_range': list(range(len(texts)))
            }
            
            self.results['field_construction'] = result
            print(f"\nFIELD CONSTRUCTION: {'SUCCESS' if result['success'] else 'FAILURE'}")
            
            return field_matrix, s_field, feature_names
            
        except Exception as e:
            print(f"FIELD CONSTRUCTION FAILED: {e}")
            self.results['field_construction'] = {'success': False, 'error': str(e)}
            return None, None, None
    
    def compute_gradient(self, field_matrix, s_field, feature_names):
        """Compute ∇s and ∇ln(s)"""
        print("\n=== STEP 2: COMPUTE GRADIENTS ===")
        
        if field_matrix is None:
            print("Cannot compute gradients - field construction failed")
            self.results['gradient_computation'] = {'success': False, 'error': 'No field available'}
            return None, None
        
        try:
            # Compute spatial gradient ∇s (gradient across feature dimensions)
            print("--- Computing ∇s (spatial gradient) ---")
            
            gradients = []
            for i, row in enumerate(field_matrix):
                gradient = np.gradient(row)  # gradient across feature dimensions
                gradient_magnitude = np.linalg.norm(gradient)
                gradients.append(gradient)
                print(f"State {i}: ∇s magnitude = {gradient_magnitude:.4f}")
            
            gradient_field = np.array(gradients)
            print(f"∇s field shape: {gradient_field.shape}")
            
            # Compute logarithmic gradient ∇ln(s) = ∇s / s
            print("\n--- Computing ∇ln(s) (logarithmic gradient) ---")
            
            log_gradients = []
            for i, (gradient, s_val) in enumerate(zip(gradients, s_field)):
                if s_val > 0:
                    log_gradient = gradient / s_val
                    log_gradient_magnitude = np.linalg.norm(log_gradient)
                    log_gradients.append(log_gradient)
                    print(f"State {i}: s={s_val:.4f}, ∇ln(s) magnitude = {log_gradient_magnitude:.4f}")
                else:
                    print(f"State {i}: s={s_val:.4f}, CANNOT compute ∇ln(s) (s <= 0)")
                    log_gradients.append(np.zeros_like(gradient))
            
            log_gradient_field = np.array(log_gradients)
            print(f"∇ln(s) field shape: {log_gradient_field.shape}")
            
            # Compute |∇ln(s)|²
            print("\n--- Computing |∇ln(s)|² ---")
            
            squared_magnitudes = []
            for i, log_gradient in enumerate(log_gradients):
                squared_mag = np.sum(log_gradient**2)
                squared_magnitudes.append(squared_mag)
                print(f"State {i}: |∇ln(s)|² = {squared_mag:.4f}")
            
            result = {
                'success': True,
                'gradient_field_shape': list(gradient_field.shape),
                'log_gradient_field_shape': list(log_gradient_field.shape),
                'avg_gradient_magnitude': float(np.mean([np.linalg.norm(g) for g in gradients])),
                'avg_log_gradient_magnitude': float(np.mean([np.linalg.norm(g) for g in log_gradients])),
                'squared_magnitudes': squared_magnitudes
            }
            
            self.results['gradient_computation'] = result
            self.results['log_gradient_computation'] = {'success': True, 'squared_magnitudes': squared_magnitudes}
            print(f"\nGRADIENT COMPUTATION: {'SUCCESS' if result['success'] else 'FAILURE'}")
            
            return squared_magnitudes
            
        except Exception as e:
            print(f"GRADIENT COMPUTATION FAILED: {e}")
            self.results['gradient_computation'] = {'success': False, 'error': str(e)}
            self.results['log_gradient_computation'] = {'success': False, 'error': str(e)}
            return None
    
    def compute_q(self, squared_magnitudes):
        """Compute Q = 4c²τ²|∇ln s|² - 1"""
        print("\n=== STEP 3: COMPUTE Q ===")
        
        if squared_magnitudes is None:
            print("Cannot compute Q - gradient computation failed")
            self.results['q_calculation'] = {'success': False, 'error': 'No gradients available'}
            return None
        
        try:
            # Test with different c and τ values
            print("--- Testing with default parameters (c=1.0, τ=0.5) ---")
            
            c = 1.0
            tau = 0.5
            
            q_values = []
            for squared_mag in squared_magnitudes:
                q = 4.0 * (c**2) * (tau**2) * squared_mag - 1.0
                q_values.append(q)
                print(f"Q = 4*({c}²)*({tau}²)*{squared_mag:.4f} - 1 = {q:.4f}")
            
            print(f"\nQ values: {q_values}")
            
            # Test parameter sensitivity
            print("\n--- Testing parameter sensitivity ---")
            
            test_params = [
                (1.0, 0.5),
                (2.0, 0.5),
                (1.0, 1.0),
                (0.5, 0.5)
            ]
            
            param_results = []
            for c_test, tau_test in test_params:
                q_test = [4.0 * (c_test**2) * (tau_test**2) * sm - 1.0 for sm in squared_magnitudes]
                param_results.append({
                    'c': c_test,
                    'tau': tau_test,
                    'q_values': q_test
                })
                print(f"c={c_test}, τ={tau_test}: Q values = {[f'{q:.2f}' for q in q_test]}")
            
            result = {
                'success': True,
                'default_q_values': q_values,
                'parameter_sensitivity': param_results,
                'note': 'Parameters are NOT empirically grounded - using arbitrary values'
            }
            
            self.results['q_calculation'] = result
            print(f"\nQ CALCULATION: {'SUCCESS' if result['success'] else 'FAILURE'}")
            print("WARNING: Using arbitrary c and τ values - NOT empirically grounded")
            
            return q_values
            
        except Exception as e:
            print(f"Q CALCULATION FAILED: {e}")
            self.results['q_calculation'] = {'success': False, 'error': str(e)}
            return None
    
    def classify_regimes(self, q_values):
        """Classify regimes based on Q values"""
        print("\n=== STEP 4: CLASSIFY REGIMES ===")
        
        if q_values is None:
            print("Cannot classify regimes - Q calculation failed")
            self.results['regime_classification'] = {'success': False, 'error': 'No Q values available'}
            return None
        
        try:
            regimes = []
            for i, q in enumerate(q_values):
                if q > 0:
                    regime = 'coherent'
                elif q < 0:
                    regime = 'overdamped'
                else:
                    regime = 'critical'
                regimes.append(regime)
                print(f"State {i}: Q={q:.4f} -> {regime}")
            
            # Check if regime boundaries are crossed
            regime_changes = []
            for i in range(1, len(regimes)):
                if regimes[i] != regimes[i-1]:
                    regime_changes.append((i-1, regimes[i-1], i, regimes[i]))
                    print(f"Regime change at state {i-1} -> {i}: {regimes[i-1]} -> {regimes[i]}")
            
            if not regime_changes:
                print("No regime changes detected")
            
            result = {
                'success': True,
                'regimes': regimes,
                'regime_changes': regime_changes,
                'note': 'Regime classification based on theoretical Q thresholds'
            }
            
            self.results['regime_classification'] = result
            print(f"\nREGIME CLASSIFICATION: {'SUCCESS' if result['success'] else 'FAILURE'}")
            
            return regimes
            
        except Exception as e:
            print(f"REGIME CLASSIFICATION FAILED: {e}")
            self.results['regime_classification'] = {'success': False, 'error': str(e)}
            return None
    
    def run_experiment(self):
        """Run complete Q calculation experiment"""
        print("=" * 60)
        print("Q FIELD INSTANTIATION EXPERIMENT - PHASE 2")
        print("Testing whether theoretical Q can be calculated")
        print("=" * 60)
        
        # Step 1: Construct field
        field_matrix, s_field, feature_names = self.construct_s_field()
        
        # Step 2: Compute gradients
        squared_magnitudes = self.compute_gradient(field_matrix, s_field, feature_names)
        
        # Step 3: Compute Q
        q_values = self.compute_q(squared_magnitudes)
        
        # Step 4: Classify regimes
        regimes = self.classify_regimes(q_values)
        
        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        
        steps = [
            ('field_construction', self.results['field_construction']),
            ('gradient_computation', self.results['gradient_computation']),
            ('log_gradient_computation', self.results['log_gradient_computation']),
            ('q_calculation', self.results['q_calculation']),
            ('regime_classification', self.results['regime_classification'])
        ]
        
        successes = sum(1 for name, result in steps if result and result.get('success', False))
        total = len(steps)
        
        print(f"Successful steps: {successes}/{total}")
        
        for name, result in steps:
            status = "SUCCESS" if result and result.get('success', False) else "FAILURE"
            print(f"  {name}: {status}")
            if result and result.get('error'):
                print(f"    Error: {result['error']}")
        
        self.results['summary'] = {
            'total_steps': total,
            'successful_steps': successes,
            'q_can_be_calculated': self.results['q_calculation'] and self.results['q_calculation'].get('success', False)
        }
        
        return self.results

if __name__ == "__main__":
    experiment = QCalculationExperiment()
    results = experiment.run_experiment()
    
    # Save results
    output_dir = os.path.join(os.path.dirname(__file__), 'Q_FIELD_RAW_RESULTS')
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, 'phase2_q_calculation.json')
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
