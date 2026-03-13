#!/usr/bin/env python3
"""
PROBLEM ANALYZER - REAL VERSION (from your HLE data)
"""
import re
import numpy as np

class ProblemAnalyzer:
    def __init__(self):
        # Based on your HLE failure patterns
        self.feature_weights = {
            'math_symbols': 0.35,
            'abstract_terms': 0.25,
            'technical_density': 0.20,
            'complexity_words': 0.15,
            'length_score': 0.05
        }
        
        # Learned from your HLE data
        self.hle_patterns = {
            # Chess: low tension (0.25)
            'chess': {
                'keywords': ['mate', 'chess', 'rook', 'pawn', 'checkmate', 'move'],
                'tension_baseline': 0.25
            },
            # Philosophy: medium-high tension (0.65)
            'philosophy': {
                'keywords': ['arrhenius', 'theorem', 'impossible', 'ethical', 'moral', 'paradox'],
                'tension_baseline': 0.65
            },
            # Math: high tension (0.92)
            'math': {
                'keywords': ['bordism', 'elliptic', 'poincaré', 'eigenvalue', 'torsion', 
                           'integral', 'calculate', 'compute', 'solve', 'derive'],
                'tension_baseline': 0.8
            },
            # Word puzzles: medium tension (0.75)
            'wordplay': {
                'keywords': ['cipher', 'puzzle', 'decode', 'substitution', 'encrypt', 'kdfkgd'],
                'tension_baseline': 0.75
            },
            # Physics: very high tension (0.99)
            'physics': {
                'keywords': ['kaluza', 'klein', 'gamma', 'schwarzschild', 'navier', 'stokes',
                           'quantum', 'gravity', 'relativity', 'equation'],
                'tension_baseline': 0.9
            }
        }
        
        # Complex math symbols
        self.complex_math = ['∫', '∑', '∏', '√', '∞', '≈', '≠', '≤', '≥', '∂', '∇', '∆', '∮']
        
        # Abstract concepts that cause confusion
        self.abstract_concepts = ['theorem', 'proof', 'lemma', 'axiom', 'paradox', 
                                 'conjecture', 'hypothesis', 'fundamental', 'principle']
    
    def extract_features(self, problem_text: str) -> dict:
        """Extract features that actually correlate with HLE failures"""
        text_lower = problem_text.lower()
        features = {}
        
        # 1. Math symbol density (scaled down for normalization)
        math_count = 0
        for symbol in self.complex_math:
            math_count += problem_text.count(symbol)
        
        # Also count basic math operators when used in complex ways
        basic_math_pattern = r'[\+\-\*/=\^]'
        basic_math_count = len(re.findall(basic_math_pattern, problem_text))
        
        # Weight complex symbols more heavily
        features['math_symbols'] = min((math_count * 3 + basic_math_count) / 10, 1.0)
        
        # 2. Abstract term density
        abstract_count = sum(1 for term in self.abstract_concepts 
                           if term in text_lower)
        features['abstract_terms'] = min(abstract_count / 5, 1.0)
        
        # 3. Technical word density (words > 8 chars or jargon)
        words = text_lower.split()
        technical_count = sum(1 for w in words if len(w) > 8 or w in [
            'bordism', 'elliptic', 'eigenvalue', 'torsion', 'schwarzschild',
            'arrhenius', 'substitution', 'quantum', 'entanglement'
        ])
        features['technical_density'] = min(technical_count / 5, 1.0)
        
        # 4. Complexity words
        complexity_words = ['compute', 'calculate', 'solve', 'derive', 'prove',
                          'integral', 'derivative', 'equation', 'theorem',
                          'complex', 'advanced', 'high-dimensional']
        complexity_count = sum(1 for word in complexity_words 
                             if word in text_lower)
        features['complexity_words'] = min(complexity_count / 5, 1.0)
        
        # 5. Length score (longer ≠ always harder, but correlates)
        features['length_score'] = min(len(problem_text) / 200, 1.0)
        
        # 6. Determine primary problem type
        features['problem_type'] = self._classify_problem_type(text_lower)
        
        # 7. Special case: integrals and calculations
        if any(word in text_lower for word in ['integral', 'calculate', 'compute']):
            if 'x^' in problem_text or 'x**' in problem_text:
                features['math_symbols'] = max(features['math_symbols'], 0.6)
        
        return features
    
    def _classify_problem_type(self, text: str) -> str:
        """Classify based on your HLE categories"""
        # Check each category
        category_scores = {}
        
        for cat, info in self.hle_patterns.items():
            score = 0
            for keyword in info['keywords']:
                if keyword in text:
                    score += 1
            category_scores[cat] = score
        
        # Find best match
        best_category = max(category_scores, key=category_scores.get)
        
        if category_scores[best_category] > 0:
            return best_category
        else:
            # Check for math operations
            if any(op in text for op in ['+', '-', '*', '/', '=', '^']):
                return 'math'
            return 'general'
    
    def predict_tension_from_features(self, features: dict) -> float:
        """Predict tension - calibrated from your HLE data"""
        # Base tension from features
        weighted_sum = 0
        total_weight = 0
        
        for feature, weight in self.feature_weights.items():
            if feature in features:
                weighted_sum += features[feature] * weight
                total_weight += weight
        
        if total_weight > 0:
            base_tension = weighted_sum / total_weight
        else:
            base_tension = 0.5
        
        # Apply problem type adjustment from HLE data
        problem_type = features.get('problem_type', 'general')
        
        # DIRECT CALIBRATION FROM YOUR HLE RESULTS:
        # Chess: 0.25 tension (95% success)
        # Philosophy: 0.65 tension (30% success)
        # Math: 0.92 tension (5% success)
        # Wordplay: 0.75 tension (10% success)
        # Physics: 0.99 tension (<5% success)
        
        if problem_type in self.hle_patterns:
            hle_baseline = self.hle_patterns[problem_type]['tension_baseline']
            # Blend base tension with HLE baseline
            tension = 0.3 * base_tension + 0.7 * hle_baseline
        else:
            # For general problems, use base tension with boost for math symbols
            if features.get('math_symbols', 0) > 0.3:
                tension = base_tension * 1.5
            else:
                tension = base_tension
        
        # Apply sigmoid to smooth extreme values
        tension = 1 / (1 + np.exp(-10 * (tension - 0.5)))
        
        return np.clip(tension, 0.0, 1.0)
