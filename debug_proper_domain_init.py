import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from universal_dynamics_engine.universal_pde_engine import UniversalDynamicsEngine

engine = UniversalDynamicsEngine()

print("=== PROPER DOMAIN INITIALIZATION TEST ===")

# First, let's find the Domain enum
from universal_dynamics_engine.universal_pde_engine import Domain

print("Available domains:")
for domain in Domain:
    print(f"  - {domain} (value: {domain.value})")

# Now add domains properly
print("\n=== ADDING DOMAINS PROPERLY ===")
engine.integrator.add_domain(Domain.BIO_PHYSICS, {})
engine.integrator.add_domain(Domain.FINANCE, {})
engine.integrator.add_domain(Domain.ENERGY, {})

print(f"Number of domains after proper addition: {len(engine.integrator.domain_states)}")

# Check domain states
for domain, state in engine.integrator.domain_states.items():
    print(f"\nDomain: {domain.value}")
    print(f"  State type: {type(state)}")
    print(f"  Metrics: {state.metrics}")
    print(f"  Has field: {hasattr(state, 'field')}")
    print(f"  Has history: {hasattr(state, 'history')}")
    if hasattr(state, 'field'):
        print(f"  Field shape: {state.field.shape if state.field is not None else 'None'}")
    if hasattr(state, 'history'):
        print(f"  History length: {len(state.history) if state.history is not None else 'None'}")

# Now test if evolution works
print("\n=== TESTING EVOLUTION ===")
try:
    ig_score, alignment, anomalies, uri_signal = engine.integrator.coupled_pde_step()
    print(f"Evolution successful!")
    print(f"  IG: {ig_score:.4f}")
    print(f"  Alignment: {alignment:.4f}")
    print(f"  Anomalies: {anomalies}")
    print(f"  Signal: {uri_signal}")
except Exception as e:
    print(f"Evolution failed: {e}")
    import traceback
    traceback.print_exc()
