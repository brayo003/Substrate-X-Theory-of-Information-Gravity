"""
Universal Risk Indicator
"""
from typing import Dict, Tuple
from theory.information_gravity_core import calculate_information_gravity

EXPAND_THRESHOLD = 0.6
CONTRACT_THRESHOLD = 0.3

def generate_risk_signal(stability_data: Dict[str, float]) -> Tuple[str, float]:
    ig_score = calculate_information_gravity(stability_data)
    
    if ig_score >= EXPAND_THRESHOLD:
        signal = "EXECUTE/EXPAND (High Confidence)"
    elif ig_score <= CONTRACT_THRESHOLD:
        signal = "CONTRACT/STAND ASIDE (Low Confidence/High Risk)"
    else:
        signal = "CAUTION/HOLD (Ambiguous Coherence)"
        
    return signal, ig_score
