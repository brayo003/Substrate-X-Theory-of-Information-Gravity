#!/usr/bin/env python3
"""
Test Substrate X Theory against experimental constraints
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

class SubstrateXTheory:
    """Implements the Proca-screened force theory"""
    def __init__(self, m_S=2e-10, alpha_S=5e-21, beta=1.0):
        # Convert everything to eV natural units
        self.m_S = m_S  # eV
        self.alpha_S = alpha_S
        self.beta = beta
        self.M_Pl = 2.435e18  # GeV
        self.hbar_c = 1.97327e-7  # eV·m (ħc in natural units)
        
    def force_ratio(self, r_meters):
        """Predicted force relative to Newtonian gravity at distance r"""
        # Convert distance to natural units (eV^-1)
        r_eV = r_meters / self.hbar_c
        
        # Yukawa suppression factor
        yukawa = np.exp(-self.m_S * r_eV)
        
        # Contact force ratio (at r << 1/m_S)
        F_contact = self.alpha_S / (4 * np.pi * 6.67e-11 * self.M_Pl**2)
        
        # Full expression including screening onset
        # Simplified model: F/F_g = F_contact * yukawa * screening(r)
        # screening(r) = 1/(1 + (r/r0)^4) where r0 ~ 1mm
        r0 = 1e-3  # 1 mm
        screening = 1 / (1 + (r_meters/r0)**4)
        
        return F_contact * yukawa * screening
    
    def plot_comparison(self, experimental_file="data/experimental_constraints/eotwash_2012.dat"):
        """Plot theory vs experimental bounds"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Theory prediction
        r = np.logspace(-4, -2, 100)  # 0.1 mm to 1 cm
        theory = self.force_ratio(r)
        ax.plot(r*1e3, theory, 'b-', linewidth=2, label='Substrate X Theory', alpha=0.7)
        
        # Experimental bounds (example Eöt-Wash 2012)
        try:
            exp_data = np.loadtxt(experimental_file)
            r_exp = exp_data[:, 0]
            bound = exp_data[:, 1]
            ax.fill_between(r_exp*1e3, 0, bound, alpha=0.3, color='red', 
                           label='Eöt-Wash 2012 Exclusion')
        except:
            # Fallback if data not available
            print("Experimental data not found, using simulated bounds")
            r_exp = np.array([0.05, 0.1, 0.2, 0.5, 1.0, 2.0])*1e-3
            bound = np.array([1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7])
            ax.fill_between(r_exp*1e3, 0, bound, alpha=0.3, color='red',
                           label='Simulated Exclusion')
        
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel('Distance (mm)', fontsize=12)
        ax.set_ylabel('|F_X / F_G|', fontsize=12)
        ax.set_title('Substrate X Theory vs Experimental Constraints', fontsize=14)
        ax.grid(True, alpha=0.3)
        ax.legend()
        plt.tight_layout()
        plt.savefig('theory_vs_experiment.png', dpi=150)
        plt.show()
        
        # Check if theory is excluded
        theory_at_points = self.force_ratio(r_exp)
        excluded = np.any(theory_at_points > bound)
        
        if excluded:
            print("❌ Theory is EXCLUDED by current experiments!")
            print(f"   Max violation: {max(theory_at_points/bound):.2f}x above bound")
        else:
            print("✅ Theory is NOT YET EXCLUDED")
            print(f"   Closest to bound: {max(theory_at_points/bound):.3f} of limit")
        
        return not excluded

def main():
    """Run the analysis"""
    print("="*60)
    print("Testing Substrate X Theory of Information Gravity")
    print("="*60)
    
    # Initialize theory with default parameters
    theory = SubstrateXTheory()
    
    print(f"\nParameters:")
    print(f"  m_S = {theory.m_S:.1e} eV")
    print(f"  α_S = {theory.alpha_S:.1e}")
    print(f"  β = {theory.beta}")
    
    print(f"\nPredicted force ratios:")
    test_distances = [1e-4, 5e-4, 1e-3, 5e-3]  # meters
    for r in test_distances:
        ratio = theory.force_ratio(r)
        print(f"  at {r*1000:.1f} mm: F_X/F_G = {ratio:.3e}")
    
    # Compare with experiments
    print("\n" + "="*60)
    print("Comparing with experimental constraints...")
    
    still_allowed = theory.plot_comparison()
    
    if still_allowed:
        print("\n📍 Next experimental target:")
        print("   Improve sensitivity at 0.5-2.0 mm range")
        print("   Or test baryon-number dependence")
        
        # Generate testable prediction file
        predictions = []
        for r in np.linspace(0.1e-3, 5e-3, 20):
            ratio = theory.force_ratio(r)
            predictions.append(f"{r:.6e}, {ratio:.6e}")
        
        with open('testable_predictions.csv', 'w') as f:
            f.write("distance_m, force_ratio\n")
            f.write("\n".join(predictions))
        
        print(f"\n📁 Predictions saved to 'testable_predictions.csv'")
    
    return still_allowed

if __name__ == "__main__":
    main()
