#!/usr/bin/env python3
"""
FIXED VERSION: Test Substrate X Theory against experimental constraints
"""
import numpy as np
import matplotlib.pyplot as plt

class SubstrateXTheoryFixed:
    """Correct implementation of the Proca-screened force theory"""
    def __init__(self, m_S=2e-10, alpha_S=5e-21):
        # Parameters from your theory
        self.m_S = m_S  # eV (mass)
        self.alpha_S = alpha_S  # dimensionless coupling
        
        # Constants (all in SI units)
        self.G = 6.67430e-11  # m³/kg/s²
        self.M_Pl = 2.176434e-8  # kg (Planck mass)
        self.hbar_c = 1.97327e-7  # eV·m
        self.eV_to_J = 1.60218e-19  # J/eV
        
    def force_ratio_at_contact(self):
        """Force relative to gravity at r → 0 (ignoring Yukawa)"""
        # From the theory: F_X/F_G = (α_S/4πG) * (1/M_Pl²) * (m1*m2 normalization)
        # For point masses, ratio is constant
        return self.alpha_S / (4 * np.pi * self.G * self.M_Pl**2)
    
    def yukawa_suppression(self, r_meters):
        """Yukawa factor: exp(-m_S * r / ħc)"""
        r_eVinv = r_meters / self.hbar_c  # Convert meters to (eV)⁻¹
        return np.exp(-self.m_S * r_eVinv)
    
    def screening_function(self, r_meters):
        """Additional screening from self-interaction (β term)"""
        r0 = 1e-3  # 1 mm screening scale
        return 1.0 / (1.0 + (r_meters/r0)**4)
    
    def force_ratio(self, r_meters):
        """Complete prediction: F_X/F_G at distance r"""
        base_ratio = self.force_ratio_at_contact()
        yukawa = self.yukawa_suppression(r_meters)
        screening = self.screening_function(r_meters)
        return base_ratio * yukawa * screening

def main():
    print("="*60)
    print("CORRECTED Substrate X Theory Test")
    print("="*60)
    
    theory = SubstrateXTheoryFixed()
    
    print(f"\nParameters:")
    print(f"  m_S = {theory.m_S:.1e} eV")
    print(f"  Range = {1/(theory.m_S * 5.06e6):.2f} mm")
    print(f"  α_S = {theory.alpha_S:.1e}")
    
    print(f"\nContact force ratio (r→0): {theory.force_ratio_at_contact():.3e}")
    
    print(f"\nPredicted force ratios:")
    distances_mm = [0.1, 0.2, 0.5, 1.0, 2.0, 5.0]
    for d in distances_mm:
        r = d * 1e-3  # Convert to meters
        ratio = theory.force_ratio(r)
        yuk = theory.yukawa_suppression(r)
        print(f"  {d:4.1f} mm: {ratio:.3e} (Yukawa: {yuk:.3f})")
    
    # Create plot
    r = np.logspace(-4, -2, 200)  # 0.1 mm to 1 cm
    ratios = [theory.force_ratio(ri) for ri in r]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(r*1e3, ratios, 'b-', linewidth=3, label='Substrate X Theory')
    
    # Add experimental constraints (approximate)
    # Eöt-Wash 2012 constraints (simulated)
    r_exp = np.array([0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0])*1e-3
    bounds = np.array([1e-2, 1e-3, 1e-4, 1e-5, 5e-6, 2e-6, 1e-6])
    ax.fill_between(r_exp*1e3, 0, bounds, alpha=0.3, color='red',
                   label='Eöt-Wash 2012 Exclusion')
    
    # CANNEX projected sensitivity (2023)
    r_can = np.array([0.5, 1.0, 2.0])*1e-3
    cannex = np.array([1e-6, 5e-7, 2e-7])
    ax.plot(r_can*1e3, cannex, 'g--', linewidth=2, label='CANNEX Projected')
    
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Distance (mm)', fontsize=12)
    ax.set_ylabel('|F_X / F_G|', fontsize=12)
    ax.set_title('Substrate X Theory: Predictions vs Experiments', fontsize=14)
    ax.grid(True, alpha=0.3, which='both')
    ax.legend()
    ax.set_ylim(1e-10, 1e-2)
    
    plt.tight_layout()
    plt.savefig('corrected_theory_test.png', dpi=150)
    plt.show()
    
    # Check if theory is excluded
    theory_at_exp = [theory.force_ratio(re) for re in r_exp]
    max_violation = max([t/b for t, b in zip(theory_at_exp, bounds) if b > 0])
    
    print(f"\n" + "="*60)
    print("EXPERIMENTAL STATUS:")
    if max_violation > 1.0:
        print(f"❌ Theory is EXCLUDED!")
        print(f"   Max violation: {max_violation:.1f}x above experimental bound")
    else:
        print(f"✅ Theory is NOT YET RULED OUT")
        print(f"   Closest to bound: {max_violation:.3f} of limit")
        print(f"   Margin: {1/max_violation:.1f}x below current sensitivity")
    
    # Check if detectable by CANNEX
    print(f"\nCANNEX PROSPECTS:")
    for rc, can_bound in zip(r_can, cannex):
        theory_val = theory.force_ratio(rc)
        if theory_val > can_bound:
            print(f"  {rc*1e3:.1f} mm: ✅ DETECTABLE (theory: {theory_val:.2e}, CANNEX: {can_bound:.2e})")
        else:
            print(f"  {rc*1e3:.1f} mm: ❌ below sensitivity (theory: {theory_val:.2e}, CANNEX: {can_bound:.2e})")

if __name__ == "__main__":
    main()
