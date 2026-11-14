import numpy as np

# ==================== CORRECT PHYSICS ====================
class CorrectSubstrateX:
    """
    CORRECT derivation based on YOUR original parameters
    """
    
    def __init__(self):
        # YOUR original parameters from the theory
        self.m_S_eV = 2e-10  # eV - FROM YOUR THEORY
        self.alpha_S = 5e-21  # dimensionless - FROM YOUR THEORY
        
        # Natural constants
        self.hbar_c = 1.97327e-7  # eV·m
        self.M_Pl = 2.435e18  # GeV (reduced Planck mass)
        
        # Calculate what these parameters actually mean
        self.derive_from_your_parameters()
    
    def derive_from_your_parameters(self):
        """What YOUR parameters actually predict"""
        print("="*70)
        print("YOUR ORIGINAL THEORY PARAMETERS:")
        print("="*70)
        print(f"m_S = {self.m_S_eV:.1e} eV")
        print(f"α_S = {self.alpha_S:.1e}")
        
        # 1. Yukawa range in meters
        self.range_m = self.hbar_c / self.m_S_eV
        print(f"\n1. Yukawa range 1/m_S = {self.range_m:.2e} m")
        print(f"   That's {self.range_m*1000:.2f} mm (NOT 1 mm!)")
        
        # 2. Force ratio from potential formula
        # From your theory: Φ_X(r) = (α_S/4πM_Pl) × (M_B/r) × e^{-m_S r}
        # Newtonian: Φ_N(r) = G M_B/r = (1/8πM_Pl²) M_B/r
        # So: F_X/F_G = Φ_X/Φ_N = 2α_S M_Pl
        M_Pl_eV = self.M_Pl * 1e9  # Convert GeV to eV
        self.force_ratio = 2 * self.alpha_S * M_Pl_eV
        print(f"\n2. Force ratio F_X/F_G = {self.force_ratio:.3e}")
        print(f"   That's {self.force_ratio*100:.2f}% of gravity")
        
        # 3. Screening length from self-interaction
        # From β term: V = (β/M_Pl⁴) X⁴
        # Screening happens when V ~ m_S² X²
        # So: X_screen ~ M_Pl² m_S / √β
        beta = 1.0  # from your theory
        self.screening_length = self.M_Pl**2 / (self.m_S_eV * np.sqrt(beta))
        print(f"\n3. Screening length = {self.screening_length:.2e} GeV⁻¹")
        
    def check_consistency(self):
        """Check if theory makes sense"""
        print("\n" + "="*70)
        print("CONSISTENCY CHECK:")
        print("="*70)
        
        issues = []
        
        # Issue 1: Range mismatch
        if self.range_m > 0.01:  # > 1 cm
            issues.append(f"Range is {self.range_m*1000:.0f} mm, not 1 mm")
        
        # Issue 2: Force too strong
        if self.force_ratio > 1e-3:
            issues.append(f"Force is {self.force_ratio:.1e}× gravity (> 0.1%)")
        
        # Issue 3: Screening at wrong scale
        screening_m = self.screening_length * 1.97327e-16  # GeV⁻¹ to m
        if screening_m < 1e-3:
            issues.append(f"Screening at {screening_m*1000:.1e} mm (too small)")
        
        if issues:
            print("❌ THEORY HAS PROBLEMS:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        else:
            print("✅ Theory is self-consistent")
            return True
    
    def make_real_predictions(self):
        """What you should actually test"""
        print("\n" + "="*70)
        print("WHAT TO TEST IN LAB:")
        print("="*70)
        
        # Test 1: Force at different distances
        print("\n1. Force vs Distance (for 1g gold masses):")
        distances = [0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0]  # mm
        for d in distances:
            r = d * 1e-3  # meters
            yukawa = np.exp(-r / self.range_m)
            force = self.force_ratio * yukawa
            
            # Gravitational force between 1g masses at this distance
            G = 6.67430e-11
            m = 1e-3  # kg
            F_gravity = G * m**2 / r**2
            F_X = force * F_gravity
            
            print(f"  {d:4.1f} mm: F_X = {F_X:.2e} N, "
                  f"F_X/F_G = {force:.2e} (Yukawa: {yukawa:.3f})")
        
        # Test 2: Material dependence
        print("\n2. Material Comparison (force relative to gravity):")
        materials = {
            'Hydrogen (H)': 1,
            'Helium (He)': 4,
            'Carbon (C)': 12,
            'Aluminum (Al)': 27,
            'Gold (Au)': 197
        }
        for name, A in materials.items():
            # Force scales with baryon number squared
            relative_force = A**2
            print(f"  {name:12}: {relative_force:5.0f}× stronger than H")
        
        # Test 3: Experimental requirements
        print("\n3. Experimental Sensitivity Needed:")
        # Smallest force we need to detect
        r_min = 0.1e-3  # 0.1 mm
        yukawa_min = np.exp(-r_min / self.range_m)
        F_min = self.force_ratio * yukawa_min
        F_gravity_min = 6.67430e-11 * (1e-3)**2 / (r_min)**2
        F_X_min_N = F_min * F_gravity_min
        
        print(f"  At 0.1 mm: Need to detect {F_X_min_N:.1e} N")
        print(f"  Current best: ~1e-15 N (Eöt-Wash)")
        print(f"  Required improvement: {F_X_min_N/1e-15:.0f}× better")
        
        return True

# ==================== MAIN ====================
def main():
    """Run the corrected analysis"""
    
    # Create theory with YOUR parameters
    theory = CorrectSubstrateX()
    
    # Check if it makes sense
    consistent = theory.check_consistency()
    
    if not consistent:
        print("\n" + "="*70)
        print("FIX NEEDED: Your parameters don't match your claims!")
        print("="*70)
        print("\nTo get 1 mm range and 0.1% force:")
        print(f"  m_S should be ~{1.97327e-7/0.001:.1e} eV (not {theory.m_S_eV:.1e} eV)")
        print(f"  α_S should be ~{1e-3/(2*2.435e18*1e9):.1e} (not {theory.alpha_S:.1e})")
    
    # Make predictions anyway
    theory.make_real_predictions()
    
    # Save to file
    with open('corrected_predictions.txt', 'w') as f:
        f.write("CORRECTED PREDICTIONS FROM YOUR THEORY\n")
        f.write("="*60 + "\n")
        f.write(f"Range: {theory.range_m:.3e} m\n")
        f.write(f"Force ratio: {theory.force_ratio:.3e}\n")
        f.write(f"Yukawa suppression at 1 mm: {np.exp(-0.001/theory.range_m):.3e}\n")
        f.write(f"\nExperimental requirement:\n")
        f.write(f"Need to measure forces of ~{theory.force_ratio*6.67430e-11*(1e-3)**2/(0.001)**2:.1e} N at 1 mm\n")
    
    print(f"\n📁 Predictions saved to 'corrected_predictions.txt'")

if __name__ == "__main__":
    main()
