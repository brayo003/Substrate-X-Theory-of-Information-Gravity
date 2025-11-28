import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from universal_dynamics_engine.universal_pde_engine import UniversalDynamicsEngine, Domain

engine = UniversalDynamicsEngine()
engine.add_domain(Domain.BIO_PHYSICS)
engine.add_domain(Domain.FINANCE)

print("=== Testing stress injection impact ===")
print("Baseline tensions:")
for step in range(3):
    engine.integrator.coupled_pde_step()
    tensions = [state.metrics['Tension'] for state in engine.integrator.domain_states.values()]
    print(f"Step {step}: {tensions}, Avg: {np.mean(tensions):.4f}")

print("\n=== With stress injection ===")
# Test different stress levels
for stress_level in [0.5, 1.0, 2.0, 5.0]:
    print(f"\nStress level: {stress_level}")
    
    # Reset to fresh state
    engine = UniversalDynamicsEngine()
    engine.add_domain(Domain.BIO_PHYSICS)
    engine.add_domain(Domain.FINANCE)
    
    # Get baseline
    engine.integrator.coupled_pde_step()
    baseline_tensions = [state.metrics['Tension'] for state in engine.integrator.domain_states.values()]
    baseline_avg = np.mean(baseline_tensions)
    
    # Apply stress
    for domain_state in engine.integrator.domain_states.values():
        noise = np.random.normal(0, stress_level * 0.1, domain_state.concentrations.shape)
        domain_state.concentrations += noise
    
    # Step and measure
    engine.integrator.coupled_pde_step()
    stressed_tensions = [state.metrics['Tension'] for state in engine.integrator.domain_states.values()]
    stressed_avg = np.mean(stressed_tensions)
    
    print(f"Baseline: {baseline_avg:.4f}, After stress: {stressed_avg:.4f}")
    print(f"Change: {((stressed_avg - baseline_avg) / baseline_avg * 100):+.1f}%")
    
    # Check if this would trigger detection
    if stressed_avg > baseline_avg * 1.15:
        print("🚨 WOULD TRIGGER STRESS DETECTION")
