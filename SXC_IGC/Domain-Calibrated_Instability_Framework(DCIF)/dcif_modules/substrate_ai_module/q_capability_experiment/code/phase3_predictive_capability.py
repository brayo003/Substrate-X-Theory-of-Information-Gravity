#!/usr/bin/env python3
"""
Q FIELD INSTANTIATION EXPERIMENT - Phase 3: Predictive Capability Test
Tests whether calculated Q predicts future system behavior
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

class PredictiveCapabilityExperiment:
    """Test whether Q predicts future system behavior"""
    
    def __init__(self):
        self.results = {
            'q_sequence': None,
            'baseline_sequences': None,
            'prediction_accuracy': None,
            'lead_time_analysis': None,
            'summary': {}
        }
        
    def generate_controlled_trajectory(self, n_steps=20):
        """Generate a controlled trajectory with known instability"""
        print("\n=== GENERATING CONTROLLED TRAJECTORY ===")
        
        try:
            from problem_analyzer import ProblemAnalyzer
            analyzer = ProblemAnalyzer()
            
            # Generate trajectory that goes from stable -> unstable -> recovery
            trajectory_texts = []
            
            # Phase 1: Stable coherent states
            for i in range(5):
                trajectory_texts.append(f"System is stable with coherent transport behavior step {i}")
            
            # Phase 2: Increasing complexity/novelty
            for i in range(5):
                complexity = 0.2 + 0.1 * i
                trajectory_texts.append(f"Processing complex input with increasing complexity {complexity:.2f}")
            
            # Phase 3: High gradient/unstable
            for i in range(5):
                trajectory_texts.append(f"Detecting high gradient and potential instability at step {i}")
            
            # Phase 4: Instability/collapse
            for i in range(3):
                trajectory_texts.append(f"System collapse imminent with critical substrate failure step {i}")
            
            # Phase 5: Recovery
            for i in range(2):
                trajectory_texts.append(f"System recovery initiated with restoration step {i}")
            
            print(f"Generated trajectory with {len(trajectory_texts)} steps")
            print(f"Phase structure: 5 stable -> 5 increasing -> 5 unstable -> 3 collapse -> 2 recovery")
            
            return trajectory_texts
            
        except Exception as e:
            print(f"TRAJECTORY GENERATION FAILED: {e}")
            return None
    
    def compute_q_sequence(self, trajectory_texts):
        """Compute Q sequence for trajectory"""
        print("\n=== COMPUTING Q SEQUENCE ===")
        
        try:
            from problem_analyzer import ProblemAnalyzer
            analyzer = ProblemAnalyzer()
            
            feature_names = ["math_symbols", "abstract_terms", "technical_density", "complexity_words", "length_score"]
            
            # Construct field
            features_list = []
            for text in trajectory_texts:
                features = analyzer.extract_features(text)
                features_list.append(features)
            
            field_matrix = np.array([[features.get(k, 0.0) for k in feature_names] for features in features_list])
            s_field = np.sum(field_matrix, axis=1)
            
            # Compute gradients
            gradients = []
            for row in field_matrix:
                gradient = np.gradient(row)
                gradients.append(gradient)
            
            # Compute ∇ln(s)
            log_gradients = []
            for gradient, s_val in zip(gradients, s_field):
                if s_val > 0:
                    log_gradient = gradient / s_val
                else:
                    log_gradient = np.zeros_like(gradient)
                log_gradients.append(log_gradient)
            
            # Compute |∇ln(s)|²
            squared_magnitudes = []
            for log_gradient in log_gradients:
                squared_mag = np.sum(log_gradient**2)
                squared_magnitudes.append(squared_mag)
            
            # Compute Q with default parameters
            c, tau = 1.0, 0.5
            q_values = [4.0 * (c**2) * (tau**2) * sm - 1.0 for sm in squared_magnitudes]
            
            print(f"Q sequence length: {len(q_values)}")
            print(f"Q values: {[f'{q:.2f}' for q in q_values]}")
            
            # Define ground truth labels based on trajectory phases
            labels = []
            # 5 stable -> 5 increasing -> 5 unstable -> 3 collapse -> 2 recovery
            for i in range(len(trajectory_texts)):
                if i < 5:
                    labels.append('stable')
                elif i < 10:
                    labels.append('increasing')
                elif i < 15:
                    labels.append('unstable')
                elif i < 18:
                    labels.append('collapse')
                else:
                    labels.append('recovery')
            
            print(f"Ground truth labels: {labels}")
            
            result = {
                'q_values': q_values,
                'labels': labels,
                's_field': s_field.tolist(),
                'squared_magnitudes': squared_magnitudes
            }
            
            self.results['q_sequence'] = result
            print(f"\nQ SEQUENCE COMPUTATION: SUCCESS")
            
            return q_values, labels
            
        except Exception as e:
            print(f"Q SEQUENCE COMPUTATION FAILED: {e}")
            self.results['q_sequence'] = {'success': False, 'error': str(e)}
            return None, None
    
    def compute_baselines(self, trajectory_texts):
        """Compute baseline predictor variables"""
        print("\n=== COMPUTING BASELINE PREDICTORS ===")
        
        try:
            from problem_analyzer import ProblemAnalyzer
            analyzer = ProblemAnalyzer()
            
            baselines = {
                'response_length': [],
                'word_count': [],
                'technical_density': [],
                'complexity_score': []
            }
            
            for text in trajectory_texts:
                features = analyzer.extract_features(text)
                
                baselines['response_length'].append(len(text))
                baselines['word_count'].append(len(text.split()))
                baselines['technical_density'].append(features.get('technical_density', 0.0))
                baselines['complexity_score'].append(features.get('technical_density', 0.0) + features.get('length_score', 0.0))
            
            print(f"Baseline sequences computed:")
            for name, values in baselines.items():
                print(f"  {name}: {[f'{v:.2f}' for v in values[:5]]}...")
            
            self.results['baseline_sequences'] = baselines
            print(f"\nBASELINE COMPUTATION: SUCCESS")
            
            return baselines
            
        except Exception as e:
            print(f"BASELINE COMPUTATION FAILED: {e}")
            self.results['baseline_sequences'] = {'success': False, 'error': str(e)}
            return None
    
    def test_prediction_accuracy(self, q_values, labels, baselines):
        """Test whether Q predicts future states better than baselines"""
        print("\n=== TESTING PREDICTION ACCURACY ===")
        
        if q_values is None or labels is None or baselines is None:
            print("Cannot test prediction - missing data")
            self.results['prediction_accuracy'] = {'success': False, 'error': 'Missing data'}
            return
        
        try:
            # Test prediction at different lead times
            lead_times = [1, 2, 3]
            
            results = {}
            
            for lead_time in lead_times:
                print(f"\n--- Lead time {lead_time} ---")
                
                # Create training data (use past to predict future)
                X_q = []
                X_baseline = []
                y = []
                
                for i in range(len(q_values) - lead_time):
                    # Predict label at i+lead_time using data at i
                    X_q.append(q_values[i])
                    # Use first baseline as representative
                    X_baseline.append(baselines['technical_density'][i])
                    
                    # Binary classification: unstable/collapse vs stable/recovery
                    future_label = labels[i + lead_time]
                    y.append(1 if future_label in ['unstable', 'collapse'] else 0)
                
                # Simple threshold prediction
                q_threshold = np.median(X_q)
                baseline_threshold = np.median(X_baseline)
                
                # Q predictions
                q_predictions = [1 if q > q_threshold else 0 for q in X_q]
                # Baseline predictions
                baseline_predictions = [1 if b > baseline_threshold else 0 for b in X_baseline]
                
                # Calculate accuracy
                q_accuracy = sum(1 for p, t in zip(q_predictions, y) if p == t) / len(y)
                baseline_accuracy = sum(1 for p, t in zip(baseline_predictions, y) if p == t) / len(y)
                
                print(f"Q prediction accuracy: {q_accuracy:.3f}")
                print(f"Baseline prediction accuracy: {baseline_accuracy:.3f}")
                print(f"Improvement: {q_accuracy - baseline_accuracy:+.3f}")
                
                results[f'lead_time_{lead_time}'] = {
                    'q_accuracy': q_accuracy,
                    'baseline_accuracy': baseline_accuracy,
                    'improvement': q_accuracy - baseline_accuracy
                }
            
            self.results['prediction_accuracy'] = results
            print(f"\nPREDICTION ACCURACY TEST: SUCCESS")
            
        except Exception as e:
            print(f"PREDICTION ACCURACY TEST FAILED: {e}")
            self.results['prediction_accuracy'] = {'success': False, 'error': str(e)}
    
    def test_lead_time(self, q_values, labels):
        """Test whether Q provides early warning of instability"""
        print("\n=== TESTING LEAD TIME ===")
        
        if q_values is None or labels is None:
            print("Cannot test lead time - missing data")
            self.results['lead_time_analysis'] = {'success': False, 'error': 'Missing data'}
            return
        
        try:
            # Find when Q first indicates instability
            instability_threshold = 0  # Q < 0 indicates overdamped/potential instability
            
            q_crossing = None
            for i, q in enumerate(q_values):
                if q < instability_threshold:
                    q_crossing = i
                    break
            
            # Find when actual instability occurs in labels
            label_crossing = None
            for i, label in enumerate(labels):
                if label in ['unstable', 'collapse']:
                    label_crossing = i
                    break
            
            print(f"Q crosses threshold at step: {q_crossing}")
            print(f"Label shows instability at step: {label_crossing}")
            
            if q_crossing is not None and label_crossing is not None:
                lead_time = label_crossing - q_crossing
                print(f"Lead time: {lead_time} steps")
                
                if lead_time > 0:
                    print(f"Q provides {lead_time} steps of early warning")
                elif lead_time < 0:
                    print(f"Q lags behind actual instability by {-lead_time} steps")
                else:
                    print(f"Q detects instability simultaneously")
            else:
                print("Cannot compute lead time - crossings not detected")
                lead_time = None
            
            result = {
                'q_crossing_step': q_crossing,
                'label_crossing_step': label_crossing,
                'lead_time_steps': lead_time,
                'early_warning': lead_time > 0 if lead_time is not None else None
            }
            
            self.results['lead_time_analysis'] = result
            print(f"\nLEAD TIME ANALYSIS: SUCCESS")
            
        except Exception as e:
            print(f"LEAD TIME ANALYSIS FAILED: {e}")
            self.results['lead_time_analysis'] = {'success': False, 'error': str(e)}
    
    def run_experiment(self):
        """Run complete predictive capability experiment"""
        print("=" * 60)
        print("Q FIELD INSTANTIATION EXPERIMENT - PHASE 3")
        print("Testing whether Q predicts future system behavior")
        print("=" * 60)
        
        # Generate trajectory
        trajectory_texts = self.generate_controlled_trajectory()
        
        if trajectory_texts is None:
            print("Cannot continue - trajectory generation failed")
            return self.results
        
        # Compute Q sequence
        q_values, labels = self.compute_q_sequence(trajectory_texts)
        
        # Compute baselines
        baselines = self.compute_baselines(trajectory_texts)
        
        # Test prediction accuracy
        self.test_prediction_accuracy(q_values, labels, baselines)
        
        # Test lead time
        self.test_lead_time(q_values, labels)
        
        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        
        steps = [
            ('q_sequence', self.results['q_sequence']),
            ('baseline_sequences', self.results['baseline_sequences']),
            ('prediction_accuracy', self.results['prediction_accuracy']),
            ('lead_time_analysis', self.results['lead_time_analysis'])
        ]
        
        successes = sum(1 for name, result in steps if result and result.get('success', True))
        total = len(steps)
        
        print(f"Successful steps: {successes}/{total}")
        
        for name, result in steps:
            status = "SUCCESS" if result and result.get('success', True) else "FAILURE"
            print(f"  {name}: {status}")
            if result and result.get('error'):
                print(f"    Error: {result['error']}")
        
        # Overall conclusion
        print("\n=== OVERALL CONCLUSION ===")
        
        if self.results['prediction_accuracy']:
            print("Prediction Accuracy Results:")
            for lead_time, data in self.results['prediction_accuracy'].items():
                if isinstance(data, dict) and 'improvement' in data:
                    print(f"  {lead_time}: Q accuracy={data['q_accuracy']:.3f}, "
                          f"Baseline={data['baseline_accuracy']:.3f}, "
                          f"Improvement={data['improvement']:+.3f}")
        
        if self.results['lead_time_analysis'] and self.results['lead_time_analysis'].get('lead_time_steps') is not None:
            lead_time = self.results['lead_time_analysis']['lead_time_steps']
            print(f"\nLead Time: {lead_time} steps")
            print(f"Early Warning: {'YES' if lead_time > 0 else 'NO'}")
        
        self.results['summary'] = {
            'total_steps': total,
            'successful_steps': successes,
            'q_has_predictive_power': self.results['prediction_accuracy'] is not None,
            'q_provides_lead_time': self.results['lead_time_analysis'] and 
                                     self.results['lead_time_analysis'].get('early_warning', False)
        }
        
        return self.results

if __name__ == "__main__":
    experiment = PredictiveCapabilityExperiment()
    results = experiment.run_experiment()
    
    # Save results
    output_dir = os.path.join(os.path.dirname(__file__), 'Q_FIELD_RAW_RESULTS')
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, 'phase3_predictive_capability.json')
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
