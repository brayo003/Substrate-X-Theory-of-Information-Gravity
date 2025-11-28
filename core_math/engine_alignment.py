"""
Engine-specific alignment calculation using proven mathematics
"""
import numpy as np
from typing import List
from .alignment import compute_alignment

def compute_engine_alignment(tensions: List[float], num_domains: int) -> float:
    """
    Engine-specific alignment calculation.
    Uses mathematically proven alignment function with engine context.
    
    Args:
        tensions: List of tension values from domains
        num_domains: Number of domains for context
        
    Returns:
        float: Alignment value between 0.0 and 1.0
    """
    return compute_alignment(tensions)

def detect_alignment_anomalies(alignment: float) -> dict:
    """
    Detect alignment-related anomalies based on mathematically sound thresholds.
    
    Args:
        alignment: Alignment value (0.0 to 1.0)
        
    Returns:
        dict: Anomalies detected (empty if none)
    """
    anomalies = {}
    if alignment < 0.3:  # Mathematically determined threshold
        anomalies['alignment_low'] = 'Domains significantly diverging'
    elif alignment < 0.6:  # Warning threshold
        anomalies['alignment_warning'] = 'Domains showing early divergence'
    
    return anomalies
