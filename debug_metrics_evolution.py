import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from universal_dynamics_engine.universal_pde_engine import UniversalDynamicsEngine, Domain

engine = UniversalDynamicsEngine()
engine.add_domain(Domain.BIO_PHYSICS)
engine.add_domain(Domain.FINANCE)

print("=== Monitoring metrics evolution ===")
for step in range(5):
    print(f"\n--- Step {step} ---")
    engine.integrator.coupled_pde_step()
    
    for domain_name, domain_state in engine.integrator.domain_states.items():
        print(f"{domain_name}:")
        print(f"  Tension: {domain_state.metrics['Tension']}")
        print(f"  Momentum: {domain_state.metrics['Momentum']}") 
        print(f"  Variance: {domain_state.metrics['Variance']}")
        print(f"  Stability: {domain_state.stability}")
        # Also check if concentrations change
        conc_mean = np.mean(domain_state.concentrations)
        conc_std = np.std(domain_state.concentrations)
        print(f"  Concentrations: mean={conc_mean:.4f}, std={conc_std:.4f}")
