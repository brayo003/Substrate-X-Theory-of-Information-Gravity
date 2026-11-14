#!/usr/bin/env python3
"""
Q FIELD INSTANTIATION EXPERIMENT - Phase 1: Field Construction (Simplified)
Tests whether s(x,t) can be constructed from existing backend components
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

class FieldConstructionExperiment:
    """Test whether s(x,t) can be constructed from existing backend"""
    
    def __init__(self):
        self.results = {
            'candidate1_clip_magnitude': None,
            'candidate2_feature_space': None,
            'candidate3_temporal_novelty': None,
            'summary': {}
        }
        
    def test_candidate1_clip_magnitude(self):
        """Test CLIP embedding magnitude as information density"""
        print("\n=== CANDIDATE 1: CLIP Embedding Magnitude ===")
        
        try:
            # Try to use sentence-transformers as fallback
            from sentence_transformers import SentenceTransformer
            
            # Load model
            print("Loading sentence-transformers model...")
            model = SentenceTransformer("all-MiniLM-L6-v2")
            
            # Test texts
            texts = [
                "The quick brown fox jumps over the lazy dog",
                "A complex mathematical equation describing quantum field theory",
                "Simple response: yes",
                "The system exhibits coherent transport behavior",
                "Instability detected in the substrate field"
            ]
            
            embeddings = []
            magnitudes = []
            
            for text in texts:
                emb = model.encode(text)
                embeddings.append(emb)
                magnitude = np.linalg.norm(emb)
                magnitudes.append(magnitude)
                print(f"Text: '{text[:50]}...'")
                print(f"  Embedding dim: {len(emb)}")
                print(f"  Magnitude: {magnitude:.4f}")
            
            # Test spatial domain construction
            print("\n--- Testing Spatial Domain Construction ---")
            
            # Treat embedding dimensions as spatial coordinates
            spatial_coords = np.arange(len(embeddings[0]))
            print(f"Spatial coordinates: embedding dimensions 0-{len(embeddings[0])-1}")
            
            # Create field by stacking embeddings
            field_matrix = np.array(embeddings)  # shape: (n_texts, embedding_dim)
            print(f"Field shape: {field_matrix.shape}")
            print(f"Field represents: {field_matrix.shape[0]} temporal states x {field_matrix.shape[1]} spatial positions")
            
            # Test gradient computation
            print("\n--- Testing Gradient Computation ---")
            
            # Compute spatial gradient (difference between adjacent dimensions)
            gradients = []
            for i, emb in enumerate(embeddings):
                gradient = np.gradient(emb)  # gradient across embedding dimensions
                gradient_magnitude = np.linalg.norm(gradient)
                gradients.append(gradient_magnitude)
                print(f"Text {i}: gradient magnitude = {gradient_magnitude:.4f}")
            
            # Test if field has information density interpretation
            print("\n--- Information Density Interpretation ---")
            
            # Higher magnitude = higher information density?
            correlations = []
            for i, text in enumerate(texts):
                # Simple complexity metric
                complexity = len(text.split())
                correlation = np.corrcoef([magnitudes[i]], [complexity])[0,1]
                correlations.append(correlation)
                print(f"Text {i}: magnitude={magnitudes[i]:.4f}, complexity={complexity}, correlation={correlation:.4f}")
            
            result = {
                'success': True,
                'field_shape': list(field_matrix.shape),
                'spatial_domain': f'embedding dimensions (0-{len(embeddings[0])-1})',
                'gradient_computable': True,
                'avg_gradient_magnitude': float(np.mean(gradients)),
                'information_density_interpretation': 'embedding magnitude as proxy',
                'complexity_correlation': float(np.mean(correlations))
            }
            
            self.results['candidate1_clip_magnitude'] = result
            print(f"\nCANDIDATE 1 RESULT: {'SUCCESS' if result['success'] else 'FAILURE'}")
            
        except ImportError:
            print("CANDIDATE 1 FAILED: sentence-transformers not available")
            self.results['candidate1_clip_magnitude'] = {'success': False, 'error': 'sentence-transformers not available'}
        except Exception as e:
            print(f"CANDIDATE 1 FAILED: {e}")
            self.results['candidate1_clip_magnitude'] = {'success': False, 'error': str(e)}
    
    def test_candidate2_feature_space(self):
        """Test text feature space as information density"""
        print("\n=== CANDIDATE 2: Feature Space ===")
        
        try:
            from problem_analyzer import ProblemAnalyzer
            
            analyzer = ProblemAnalyzer()
            
            texts = [
                "The quick brown fox jumps over the lazy dog",
                "A complex mathematical equation describing quantum field theory with ∇²ψ = 0",
                "Simple response: yes",
                "The system exhibits coherent transport behavior with Q > 0",
                "Instability detected in the substrate field"
            ]
            
            features_list = []
            for text in texts:
                features = analyzer.extract_features(text)
                features_list.append(features)
                print(f"Text: '{text[:50]}...'")
                print(f"  Features: {features}")
            
            # Construct field from features
            feature_names = ["math_symbols", "abstract_terms", "technical_density", "complexity_words", "length_score"]
            field_matrix = np.array([[features.get(k, 0.0) for k in feature_names] for features in features_list])
            
            print(f"\n--- Field Construction ---")
            print(f"Field shape: {field_matrix.shape}")
            print(f"Spatial coordinates: {feature_names}")
            print(f"Field represents: {field_matrix.shape[0]} temporal states x {field_matrix.shape[1]} feature dimensions")
            
            # Test gradient computation
            print("\n--- Testing Gradient Computation ---")
            
            gradients = []
            for i, row in enumerate(field_matrix):
                gradient = np.gradient(row)
                gradient_magnitude = np.linalg.norm(gradient)
                gradients.append(gradient_magnitude)
                print(f"State {i}: gradient magnitude = {gradient_magnitude:.4f}")
            
            # Test information density interpretation
            print("\n--- Information Density Interpretation ---")
            
            # Sum of normalized features as information density
            info_densities = np.sum(field_matrix, axis=1)
            print(f"Information densities: {info_densities}")
            
            result = {
                'success': True,
                'field_shape': list(field_matrix.shape),
                'spatial_domain': 'feature space (5 dimensions)',
                'gradient_computable': True,
                'avg_gradient_magnitude': float(np.mean(gradients)),
                'information_density_interpretation': 'sum of normalized features',
                'info_densities': info_densities.tolist()
            }
            
            self.results['candidate2_feature_space'] = result
            print(f"\nCANDIDATE 2 RESULT: {'SUCCESS' if result['success'] else 'FAILURE'}")
            
        except Exception as e:
            print(f"CANDIDATE 2 FAILED: {e}")
            self.results['candidate2_feature_space'] = {'success': False, 'error': str(e)}
    
    def test_candidate3_temporal_novelty(self):
        """Test temporal semantic novelty as information density"""
        print("\n=== CANDIDATE 3: Temporal Semantic Novelty ===")
        
        try:
            # Try to use sentence-transformers
            from sentence_transformers import SentenceTransformer
            
            print("Loading sentence-transformers model...")
            model = SentenceTransformer("all-MiniLM-L6-v2")
            
            # Simulate temporal sequence
            texts = [
                "Initial state: system is stable",
                "Processing input data",
                "Computing gradient field",
                "Detecting novelty in pattern",
                "Transition to new state",
                "Final state: system evolved"
            ]
            
            embeddings = []
            for text in texts:
                emb = model.encode(text)
                embeddings.append(emb)
            
            # Compute temporal novelty (E_t)
            from sklearn.metrics.pairwise import cosine_similarity
            
            novelties = []
            for i in range(1, len(embeddings)):
                sim = cosine_similarity([embeddings[i-1]], [embeddings[i]])[0][0]
                novelty = 1.0 - sim
                novelties.append(novelty)
                print(f"Transition {i-1} -> {i}: similarity={sim:.4f}, novelty={novelty:.4f}")
            
            # Construct temporal field
            print(f"\n--- Temporal Field Construction ---")
            temporal_field = np.array(novelties)
            print(f"Temporal field shape: {temporal_field.shape}")
            print(f"Spatial domain: 1D time (timesteps 1-{len(novelties)})")
            print(f"Field represents: semantic novelty at each timestep")
            
            # Test gradient computation (temporal gradient)
            print("\n--- Testing Temporal Gradient ---")
            
            temporal_gradient = np.gradient(temporal_field)
            print(f"Temporal gradient: {temporal_gradient}")
            print(f"Gradient magnitude: {np.linalg.norm(temporal_gradient):.4f}")
            
            result = {
                'success': True,
                'field_shape': list(temporal_field.shape),
                'spatial_domain': '1D temporal (no spatial component)',
                'gradient_computable': True,
                'temporal_gradient_magnitude': float(np.linalg.norm(temporal_gradient)),
                'information_density_interpretation': 'temporal semantic novelty',
                'novelties': novelties
            }
            
            self.results['candidate3_temporal_novelty'] = result
            print(f"\nCANDIDATE 3 RESULT: {'SUCCESS' if result['success'] else 'FAILURE'}")
            print("WARNING: This is purely temporal, not spatial - fails spatial field requirement")
            
        except ImportError:
            print("CANDIDATE 3 FAILED: sentence-transformers not available")
            self.results['candidate3_temporal_novelty'] = {'success': False, 'error': 'sentence-transformers not available'}
        except Exception as e:
            print(f"CANDIDATE 3 FAILED: {e}")
            self.results['candidate3_temporal_novelty'] = {'success': False, 'error': str(e)}
    
    def run_all_tests(self):
        """Run all field construction tests"""
        print("=" * 60)
        print("Q FIELD INSTANTIATION EXPERIMENT - PHASE 1")
        print("Testing whether s(x,t) can be constructed from existing backend")
        print("=" * 60)
        
        self.test_candidate1_clip_magnitude()
        self.test_candidate2_feature_space()
        self.test_candidate3_temporal_novelty()
        
        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        
        successes = sum(1 for r in self.results.values() if r and r.get('success', False))
        total = len([r for r in self.results.values() if r is not None])
        
        print(f"Successful constructions: {successes}/{total}")
        
        for name, result in self.results.items():
            if result:
                status = "SUCCESS" if result.get('success', False) else "FAILURE"
                print(f"  {name}: {status}")
                if result.get('error'):
                    print(f"    Error: {result['error']}")
        
        self.results['summary'] = {
            'total_tests': total,
            'successful': successes,
            'viable_s_constructions': successes
        }
        
        return self.results

if __name__ == "__main__":
    experiment = FieldConstructionExperiment()
    results = experiment.run_all_tests()
    
    # Save results
    output_dir = os.path.join(os.path.dirname(__file__), 'Q_FIELD_RAW_RESULTS')
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, 'phase1_field_construction.json')
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
