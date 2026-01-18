#!/usr/bin/env python3
import numpy as np
from corrected_physics import CorrectedSubstratePhysics

class LargeScaleTests:
    def __init__(self):
        self.physics = CorrectedSubstratePhysics()
    
    def test_pioneer_anomaly(self):
        """Test if substrate explains Pioneer anomaly at large distances"""
        print("🚀 TESTING PIONEER ANOMALY EXPLANATION")
        print("=" * 50)
        
        # Pioneer anomaly: 8.74e-10 m/s² at ~20 AU
        pioneer_distance = 20 * 1.496e11  # meters
        earth_distance = 1.496e11
        
        # Your current scaling: s ∝ 1/r, v ∝ 1/r
        s_ratio = earth_distance / pioneer_distance
        v_ratio = earth_distance / pioneer_distance
        
        print(f"At 20 AU vs 1 AU:")
        print(f"  s ratio: {s_ratio:.3f}")
        print(f"  v ratio: {v_ratio:.3f}")
        print(f"  Force ratio (s×v): {s_ratio * v_ratio:.3f}")
        
        print("\nCurrent scaling gives pure 1/r² force")
        print("For Pioneer anomaly, need modified scaling at large r")
        
        return "scaling_modification_needed"
    
    def test_galactic_rotation(self):
        """Test dark matter replacement at galactic scales"""
        print("\n🌌 TESTING GALACTIC ROTATION")
        print("=" * 50)
        
        # Galactic scale: ~50,000 light years vs solar system scale
        solar_scale = 1.496e11  # 1 AU
        galactic_scale = 50000 * 9.461e15  # 50k ly in meters
        
        scale_ratio = solar_scale / galactic_scale
        print(f"Galactic vs solar scale ratio: {scale_ratio:.2e}")
        
        print("\nPossible substrate modifications at large scales:")
        print("1. s(r) becomes constant (information saturation)")
        print("2. v(r) scaling changes (enhanced flow)")
        print("3. k becomes scale-dependent")
        
        return "multiple_mechanisms_possible"

if __name__ == "__main__":
    tests = LargeScaleTests()
    tests.test_pioneer_anomaly()
    tests.test_galactic_rotation()
END
