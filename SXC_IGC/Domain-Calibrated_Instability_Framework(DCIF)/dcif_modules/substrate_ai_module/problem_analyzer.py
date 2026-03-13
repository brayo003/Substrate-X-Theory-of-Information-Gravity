import re

class ProblemAnalyzer:
    def extract_features(self, text):
        text_lc = text.lower()
        
        # 1. Structural Intent: Is a formal closure required?
        formal_demand = bool(re.search(r'(compute|calculate|determine|find|prove|evaluate|derive)', text_lc))
        
        # 2. Vocabulary Domain
        advanced_lexicon = bool(re.search(r'(bordism|manifold|eigen|spin|topology|\\∫|homology|cohomology|tensor)', text_lc))
        simple_math = bool(re.search(r'(\d+[\+\-\*\/]\d+)|(solve for x)', text_lc))
        
        return {
            'formal_demand': formal_demand,
            'advanced_lexicon': advanced_lexicon,
            'simple_math': simple_math,
            'problem_type': 'formal_math' if (formal_demand and (advanced_lexicon or simple_math)) else 'narrative'
        }

    def predict_tension_from_features(self, features):
        # Implementation of Constraint Gravity
        if features['advanced_lexicon'] and features['formal_demand']:
            return 0.99  # FORMAL_REQUIRED (Substrate Collapse)
        if features['advanced_lexicon'] and not features['formal_demand']:
            return 0.45  # NARRATIVE_OK (High Gravity but no closure demand)
        if features['simple_math'] and features['formal_demand']:
            return 0.25  # NARRATIVE_OK (Manageable local logic)
        return 0.10      # LOW_GRAVITY
