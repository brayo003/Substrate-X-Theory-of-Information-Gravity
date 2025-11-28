import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from universal_dynamics_engine.universal_pde_engine import UniversalDynamicsEngine, Domain

# Create engine and check its structure
engine = UniversalDynamicsEngine()
engine.add_domain(Domain.BIO_PHYSICS)
engine.add_domain(Domain.FINANCE)

print("=== Engine Attributes ===")
for attr in dir(engine):
    if not attr.startswith('_'):
        print(attr)

print("\n=== Integrator Attributes ===")
for attr in dir(engine.integrator):
    if not attr.startswith('_'):
        print(attr)

print("\n=== Available domains in integrator ===")
if hasattr(engine.integrator, 'domains'):
    print(f"Integrator domains: {list(engine.integrator.domains.keys())}")
else:
    print("No domains attribute in integrator")

print("\n=== Checking domain access methods ===")
# Try to compute information gravity to see what methods work
try:
    ig = engine.compute_information_gravity()
    print(f"Information Gravity: {ig}")
except Exception as e:
    print(f"Error computing IG: {e}")

try:
    alignment = engine.compute_alignment()
    print(f"Alignment: {alignment}")
except Exception as e:
    print(f"Error computing alignment: {e}")
