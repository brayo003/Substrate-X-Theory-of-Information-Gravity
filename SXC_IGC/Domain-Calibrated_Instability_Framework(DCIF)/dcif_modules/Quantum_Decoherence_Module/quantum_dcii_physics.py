"""
QUANTUM DCII MODULE - PHYSICS BASED
NO curve fitting, ONLY quantum physics

Usage:
    from quantum_dcii_physics import QuantumDCIIPhysics
    
    # From experimental T1, T2* times
    result = QuantumDCIIPhysics.quantum_dcii(T2_star=50e-6, T1=100e-6)
    
    print(f"E = {result['E']:.3f} (from 1/T2*)")
    print(f"F = {result['F']:.3f} (from T2*/2T1)")
    print(f"T = {result['T']:.3f} = E × (1-F)")
    print(f"Level: {result['level']}")
"""

import numpy as np
from typing import Dict

class QuantumDCIIPhysics:
    """Physics-based quantum DCII - NO curve fitting"""
    
    @staticmethod
    def estimate_E_from_coherence(T2_star: float, T2_max: float = 10.0) -> float:
        """
        Estimate E from coherence time using QUANTUM PHYSICS
        E ∝ 1/T2* (decoherence rate)
        """
        if T2_star <= 0:
            return 1.0
        
        # Quantum physics: Γ = 1/T2
        decoherence_rate = 1.0 / T2_star
        
        # Normalize: Max rate at T2_min = 1ns
        T2_min = 1e-9
        max_rate = 1.0 / T2_min
        
        E = min(1.0, decoherence_rate / max_rate)
        return E
    
    @staticmethod
    def estimate_F_from_protection(T2_star: float, T1: float) -> float:
        """
        Estimate F from protection quality using QUANTUM PHYSICS
        F = T2*/2T1 (quantum limit ratio)
        """
        if T1 <= 0:
            return 0.0
        
        # Quantum limit: T2 ≤ 2T1
        quantum_limit = 2.0 * T1
        F = min(1.0, T2_star / quantum_limit)
        return F
    
    @staticmethod
    def quantum_dcii(T2_star: float, T1: float) -> Dict:
        """
        Compute Quantum DCII from PHYSICAL measurements ONLY
        
        Args:
            T2_star: Decoherence/dephasing time (seconds)
            T1: Energy relaxation time (seconds)
            
        Returns:
            Dict with E, F, T, and interpretation
        """
        # Physics-based estimation (NO curve fitting)
        E = QuantumDCIIPhysics.estimate_E_from_coherence(T2_star)
        F = QuantumDCIIPhysics.estimate_F_from_protection(T2_star, T1)
        
        # Quantum tension: T = E × (1 - F)
        T = E * (1.0 - F)
        
        # Classification
        if T < 0.05:
            level = "Coherent"
        elif T < 0.25:
            level = "Partially Decohered"
        elif T < 0.50:
            level = "Mostly Decohered"
        else:
            level = "Fully Decohered"
        
        return {
            "physics_based": True,
            "T2_star": T2_star,
            "T1": T1,
            "E": E,
            "F": F,
            "T": T,
            "level": level,
            "quantum_limit_ratio": T2_star / (2.0 * T1) if T1 > 0 else 0,
            "interpretation": f"T = {E:.3f} × (1 - {F:.3f}) = {T:.3f}"
        }
