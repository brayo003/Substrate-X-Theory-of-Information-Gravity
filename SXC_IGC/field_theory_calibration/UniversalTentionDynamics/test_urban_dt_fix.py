#!/usr/bin/env python3
"""
TEMPORARY FIX TEST: Urban dt reduction
If this works, we understand the issue. If not, we revert.
"""
import sys
import os
sys.path.insert(0, 'core_engine/src')
from universal_dynamics_robust import create_robust_engine
import numpy as np

print("🔧 TEMPORARY URBAN FIX TEST")
print("Testing if dt reduction solves explosion")
print("REVERTIBLE: If this doesn't work, we go back to original")
print("=" * 50)

def test_urban_with_fixed_dt():
    """Test urban with finance-like dt"""
    
    print("🧪 TEST 1: Urban with original dt=0.01 (baseline)")
    urban_original = create_robust_engine('urban', grid_size=32)
    urban_original.initialize_gaussian(amplitude=0.5)
    
    # Track evolution
    original_rhos = []
    for step in range(15):
        urban_original.evolve_robust_imex()
        rho_max = np.max(urban_original.rho)
        original_rhos.append(rho_max)
        if rho_max > 1000:
            print(f"  Step {step}: ρ_max = {rho_max:.1f} 💥")
            break
        else:
            print(f"  Step {step}: ρ_max = {rho_max:.3f}")
    
    print(f"\n🧪 TEST 2: Urban with reduced dt=0.001")
    urban_fixed = create_robust_engine('urban', grid_size=32, dt=0.001)
    urban_fixed.initialize_gaussian(amplitude=0.5)
    
    fixed_rhos = []
    for step in range(15):
        urban_fixed.evolve_robust_imex()
        rho_max = np.max(urban_fixed.rho)
        fixed_rhos.append(rho_max)
        stiffness = np.max(urban_fixed.rho) > urban_fixed.rho_cutoff
        print(f"  Step {step}: ρ_max = {rho_max:.3f} | Stiffness: {stiffness}")
    
    print(f"\n🧪 TEST 3: Compare with finance domain (dt=0.001)")
    finance = create_robust_engine('finance', grid_size=32)
    finance.initialize_gaussian(amplitude=0.5)
    
    finance_rhos = []
    for step in range(15):
        finance.evolve_robust_imex()
        rho_max = np.max(finance.rho)
        finance_rhos.append(rho_max)
        stiffness = np.max(finance.rho) > finance.rho_cutoff
        print(f"  Step {step}: ρ_max = {rho_max:.3f} | Stiffness: {stiffness}")
    
    return original_rhos, fixed_rhos, finance_rhos

def analyze_results(original, fixed, finance):
    """Analyze if the fix worked and what it tells us"""
    
    print(f"\n{'='*50}")
    print("📊 RESULTS ANALYSIS")
    print("=" * 50)
    
    original_exploded = any(rho > 1000 for rho in original)
    fixed_exploded = any(rho > 1000 for rho in fixed)
    finance_exploded = any(rho > 1000 for rho in finance)
    
    print(f"Original urban (dt=0.01): {'💥 EXPLODED' if original_exploded else '✅ STABLE'}")
    print(f"Fixed urban (dt=0.001):   {'💥 EXPLODED' if fixed_exploded else '✅ STABLE'}")
    print(f"Finance (dt=0.001):       {'💥 EXPLODED' if finance_exploded else '✅ STABLE'}")
    
    # Compare growth patterns
    if not original_exploded:
        original_growth = original[-1] / original[0] if original[0] > 0 else 1
    else:
        original_growth = "INFINITE"
    
    fixed_growth = fixed[-1] / fixed[0] if fixed[0] > 0 else 1
    finance_growth = finance[-1] / finance[0] if finance[0] > 0 else 1
    
    print(f"\n📈 GROWTH COMPARISON (final/initial):")
    print(f"Original urban: {original_growth}")
    print(f"Fixed urban:    {fixed_growth:.3f}x")
    print(f"Finance:        {finance_growth:.3f}x")
    
    print(f"\n💡 INTERPRETATION:")
    if not fixed_exploded:
        print("✅ HYPOTHESIS CONFIRMED: dt was the primary issue")
        print("   Urban physics can be stable with proper time stepping")
        print("   The explosion was numerical, not physical")
    else:
        print("❌ HYPOTHESIS REJECTED: dt is not the only issue")
        print("   Urban has fundamentally different physics")
        print("   We should revert and study further")

# Run the reversible test
if __name__ == "__main__":
    print("🎯 TEST STRATEGY: Temporary fix → Analyze → Revert if wrong")
    print("This is SCIENCE, not brute force!")
    print("=" * 60)
    
    original, fixed, finance = test_urban_with_fixed_dt()
    analyze_results(original, fixed, finance)
    
    print(f"\n{'='*60}")
    print("🔮 NEXT STEPS:")
    print("If hypothesis confirmed: We understand urban needs smaller dt")
    print("If hypothesis rejected: Revert and study urban's unique physics")
    print("Either way: We learn something valuable!")
    print("=" * 60)
