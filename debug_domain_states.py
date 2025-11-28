import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from universal_dynamics_engine.universal_pde_engine import UniversalDynamicsEngine, Domain

engine = UniversalDynamicsEngine()
engine.add_domain(Domain.BIO_PHYSICS)
engine.add_domain(Domain.FINANCE)

print("=== Inspecting domain_states ===")
print(f"Type: {type(engine.integrator.domain_states)}")
print(f"Keys: {list(engine.integrator.domain_states.keys())}")

for domain_name, domain_state in engine.integrator.domain_states.items():
    print(f"\n--- {domain_name} ---")
    print(f"Type: {type(domain_state)}")
    print(f"Attributes: {[attr for attr in dir(domain_state) if not attr.startswith('_')]}")
    
    # Try to access common potential attributes
    for attr in ['tension', 'pressure', 'state', 'value', 'field']:
        if hasattr(domain_state, attr):
            value = getattr(domain_state, attr)
            print(f"{attr}: {value} (type: {type(value)})")
    
    # If it's a numpy array or similar, show shape and some values
    if hasattr(domain_state, 'shape'):
        print(f"shape: {domain_state.shape}")
        print(f"sample values: {domain_state.flatten()[:5]}")
    elif hasattr(domain_state, '__array__'):
        arr = np.array(domain_state)
        print(f"as array shape: {arr.shape}")
        print(f"sample values: {arr.flatten()[:5]}")

print("\n=== After one integration step ===")
engine.integrator.coupled_pde_step()
for domain_name, domain_state in engine.integrator.domain_states.items():
    print(f"\n--- {domain_name} after step ---")
    for attr in ['tension', 'pressure', 'state', 'value', 'field']:
        if hasattr(domain_state, attr):
            value = getattr(domain_state, attr)
            print(f"{attr}: {value} (type: {type(value)})")
