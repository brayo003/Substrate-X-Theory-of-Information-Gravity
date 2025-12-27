#!/usr/bin/env python3
"""
STUDY: Urban Explosion Physics
Understanding the mechanism before considering fixes
"""
import sys
import os
sys.path.insert(0, 'core_engine/src')
from universal_dynamics_robust import create_robust_engine
import numpy as np

print("🔬 URBAN EXPLOSION STUDY")
print("Understanding the physics, not fixing it")
print("=" * 50)

def study_explosion_mechanism():
    """Study exactly how and why urban explodes"""
    
    print("Creating urban engine with monitoring...")
    urban = create_robust_engine('urban', grid_size=32)
    urban.initialize_gaussian(amplitude=0.5)
    
    print("\n📊 INITIAL STATE:")
    print(f"  ρ_max: {np.max(urban.rho):.3f}")
    print(f"  ρ at center: {urban.rho[16,16]:.3f}")
    print(f"  Stiffness active: {np.max(urban.rho) > urban.rho_cutoff}")
    
    print("\n🧪 STEP-BY-STEP EVOLUTION STUDY:")
    
    for step in range(15):  # Stop before complete explosion
        # Store pre-evolution state
        rho_pre = urban.rho.copy()
        rho_max_pre = np.max(rho_pre)
        stiffness_pre = np.max(rho_pre) > urban.rho_cutoff
        
        # Evolve one step
        urban.evolve_robust_imex()
        
        # Analyze changes
        rho_max_post = np.max(urban.rho)
        growth_factor = rho_max_post / rho_max_pre if rho_max_pre > 0 else 1.0
        stiffness_post = np.max(urban.rho) > urban.rho_cutoff
        
        print(f"Step {step:2d}: ρ_max={rho_max_post:8.3f} (x{growth_factor:5.1f}) | "
              f"Stiffness: {stiffness_pre}→{stiffness_post}")
        
        # Detailed analysis at critical points
        if step == 4 or step == 5:  # Around explosion start
            print(f"    🔍 CRITICAL POINT ANALYSIS:")
            print(f"      ρ range: [{np.min(urban.rho):.3f}, {np.max(urban.rho):.3f}]")
            print(f"      E range: [{np.min(urban.E):.3f}, {np.max(urban.E):.3f}]")
            print(f"      F range: [{np.min(urban.F):.3f}, {np.max(urban.F):.3f}]")
            
            # Check stiffness activation
            alpha_eff = urban.compute_effective_stiffness(urban.rho)
            max_stiffness = np.max(alpha_eff)
            print(f"      Max stiffness factor: {max_stiffness:.1f}")
        
        if rho_max_post > 1000:
            print("💥 EXPLOSION REACHED - stopping study")
            break
    
    return urban

def compare_domains():
    """Compare urban with other domains to understand uniqueness"""
    
    print(f"\n{'='*50}")
    print("🌍 DOMAIN COMPARISON STUDY")
    print("=" * 50)
    
    domains = ['finance', 'urban', 'healthcare']
    
    for domain in domains:
        print(f"\n📈 {domain.upper()} DOMAIN:")
        engine = create_robust_engine(domain, grid_size=32)
        engine.initialize_gaussian(amplitude=0.5)
        
        # Evolve 10 steps and track growth
        growth_factors = []
        for step in range(10):
            rho_pre = np.max(engine.rho)
            engine.evolve_robust_imex()
            rho_post = np.max(engine.rho)
            
            growth = rho_post / rho_pre if rho_pre > 0 else 1.0
            growth_factors.append(growth)
            
            stiffness = np.max(engine.rho) > engine.rho_cutoff
            if stiffness and step > 0:
                print(f"  Step {step}: stiffness activated, growth={growth:.2f}x")
        
        avg_growth = np.mean(growth_factors)
        max_growth = np.max(growth_factors)
        print(f"  Average growth: {avg_growth:.3f}x per step")
        print(f"  Maximum growth: {max_growth:.3f}x per step")
        print(f"  Final ρ_max: {np.max(engine.rho):.3f}")

def study_parameter_sensitivity():
    """Study which parameters most affect urban stability"""
    
    print(f"\n{'='*50}")
    print("⚖️ PARAMETER SENSITIVITY STUDY")
    print("=" * 50)
    
    base_params = {'grid_size': 32}
    
    # Test different parameter modifications
    test_cases = [
        ('Default Urban', {}),
        ('Lower dt', {'dt': 0.001}),
        ('Higher Damping', {'cubic_damping': 1.0}),
        ('Lower M_factor', {'M_factor': 1000}),
        ('Higher M_factor', {'M_factor': 10000}),
        ('Different rho_cutoff', {'rho_cutoff': 0.5}),
    ]
    
    for case_name, params in test_cases:
        print(f"\n🧪 {case_name}:")
        test_params = base_params.copy()
        test_params.update(params)
        
        try:
            engine = create_robust_engine('urban', **test_params)
            engine.initialize_gaussian(amplitude=0.5)
            
            # Evolve and check stability
            stable_steps = 0
            for step in range(20):
                engine.evolve_robust_imex()
                if np.max(engine.rho) < 100:  # Reasonable bound
                    stable_steps += 1
                else:
                    break
            
            final_rho = np.max(engine.rho)
            status = "STABLE" if stable_steps == 20 else f"EXPLODED at step {stable_steps+1}"
            print(f"  {status} | Final ρ_max: {final_rho:.3f}")
            
        except Exception as e:
            print(f"  CRASHED: {e}")

# Run the comprehensive study
if __name__ == "__main__":
    print("🔬 COMPREHENSIVE URBAN EXPLOSION STUDY")
    print("Goal: Understand the physics before considering fixes")
    print("=" * 60)
    
    # Study 1: Detailed explosion mechanism
    urban_engine = study_explosion_mechanism()
    
    # Study 2: Domain comparison
    compare_domains()
    
    # Study 3: Parameter sensitivity
    study_parameter_sensitivity()
    
    print(f"\n{'='*60}")
    print("📋 STUDY CONCLUSIONS:")
    print("1. When does stiffness activate?")
    print("2. What triggers the exponential growth?") 
    print("3. How do other domains avoid this?")
    print("4. Which parameters control stability?")
    print("=" * 60)
