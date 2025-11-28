import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from universal_dynamics_engine.universal_pde_engine import UniversalDynamicsEngine

engine = UniversalDynamicsEngine()

print("=== CHECKING DOMAIN INITIALIZATION ===")

# Check what happens when we add domains
print("Before adding domains:")
print(f"Domain states: {engine.integrator.domain_states}")
print(f"Number of domains: {len(engine.integrator.domain_states)}")

# Let's trace the add_domain method
print("\n=== TRACING add_domain METHOD ===")

# Check the actual add_domain implementation
import inspect
source = inspect.getsource(engine.integrator.add_domain)
print("add_domain source:")
print(source)

# Check if domains are being added properly
print("\n=== TESTING DOMAIN ADDITION ===")
try:
    engine.integrator.add_domain("test_domain", {})
    print(f"After adding test_domain: {len(engine.integrator.domain_states)} domains")
    if "test_domain" in engine.integrator.domain_states:
        state = engine.integrator.domain_states["test_domain"]
        print(f"Test domain state: {state}")
        print(f"Test domain metrics: {getattr(state, 'metrics', 'NO METRICS')}")
        print(f"Test domain field: {getattr(state, 'field', 'NO FIELD')}")
        print(f"Test domain history: {getattr(state, 'history', 'NO HISTORY')}")
    else:
        print("test_domain not found in domain_states!")
except Exception as e:
    print(f"Error adding domain: {e}")
