import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from universal_dynamics_engine.universal_pde_engine import UniversalDynamicsEngine, Domain

engine = UniversalDynamicsEngine()
engine.add_domain(Domain.BIO_PHYSICS)
engine.add_domain(Domain.FINANCE)

print("=== Detailed domain state inspection ===")
for domain_name, domain_state in engine.integrator.domain_states.items():
    print(f"\n--- {domain_name} ---")
    
    print("concentrations:", domain_state.concentrations)
    print("metrics:", domain_state.metrics)
    print("stability:", domain_state.stability)
    print("history keys:", list(domain_state.history.keys()) if domain_state.history else "No history")
    
print("\n=== After one integration step ===")
engine.integrator.coupled_pde_step()

for domain_name, domain_state in engine.integrator.domain_states.items():
    print(f"\n--- {domain_name} after step ---")
    print("concentrations:", domain_state.concentrations)
    print("metrics:", domain_state.metrics)
    print("stability:", domain_state.stability)
    
    # Check if metrics changed
    if domain_state.metrics:
        for metric_name, metric_value in domain_state.metrics.items():
            print(f"  {metric_name}: {metric_value}")
