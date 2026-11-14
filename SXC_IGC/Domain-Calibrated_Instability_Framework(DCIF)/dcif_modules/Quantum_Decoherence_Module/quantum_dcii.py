"""
QUANTUM DCII MODULE - UNIVERSAL
For integration into SXC-IGC framework

Usage:
    from quantum_dcii import QuantumDCII, QuantumPlatform
    
    # Analyze a superconducting qubit
    qdcii = QuantumDCII(QuantumPlatform.SUPERCONDUCTING_QUBIT)
    
    # From experimental parameters
    params = {"T1_s": 50e-6, "T2_s": 30e-6}
    result = qdcii.analyze(params)
    
    print(f"Tension: {result['T']:.3f}")
    print(f"Sensitivity: β/γ = {result['sensitivity_ratio']:.1f}")
"""

import numpy as np
from enum import Enum

class QuantumPlatform(Enum):
    TRAPPED_ION = "trapped_ion"
    SUPERCONDUCTING_QUBIT = "superconducting_qubit"
    LEVITATED_NANO = "levitated_nano"
    NV_CENTER = "nv_center"
    QUANTUM_DOT = "quantum_dot"

class QuantumDCII:
    """Main quantum DCII class"""
    
    PLATFORM_CALIBRATIONS = {
        QuantumPlatform.TRAPPED_ION: {"β": 0.920, "γ": 0.008, "τ": 0.2},
        QuantumPlatform.SUPERCONDUCTING_QUBIT: {"β": 0.850, "γ": 0.080, "τ": 0.15},
        QuantumPlatform.LEVITATED_NANO: {"β": 0.948, "γ": 0.014, "τ": 0.1},
        QuantumPlatform.NV_CENTER: {"β": 0.950, "γ": 0.020, "τ": 0.25},
        QuantumPlatform.QUANTUM_DOT: {"β": 0.900, "γ": 0.050, "τ": 0.12},
    }
    
    def __init__(self, platform: QuantumPlatform):
        self.platform = platform
        cal = self.PLATFORM_CALIBRATIONS[platform]
        self.β, self.γ, self.τ = cal["β"], cal["γ"], cal["τ"]
    
    def compute(self, E: float, F: float) -> float:
        """Compute quantum tension"""
        T_linear = max(0.0, self.β * E - self.γ * F)
        return 1.0 - np.exp(-T_linear / self.τ)
    
    @property
    def sensitivity_ratio(self) -> float:
        """Get β/γ sensitivity ratio"""
        return self.β / self.γ
    
    def get_calibration_info(self) -> dict:
        """Get calibration information"""
        return {
            "platform": self.platform.value,
            "beta": self.β,
            "gamma": self.γ,
            "tau": self.τ,
            "sensitivity_ratio": self.sensitivity_ratio,
            "description": f"Quantum {self.platform.value}: β/γ = {self.sensitivity_ratio:.1f}"
        }
