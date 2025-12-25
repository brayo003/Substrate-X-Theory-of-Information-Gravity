#!/usr/bin/env python3
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

# Create a solver instance to check available methods
solver = CompleteFieldTheorySolver(alpha=1e-5, delta1=25.0)
print("Available methods in CompleteFieldTheorySolver:")
methods = [method for method in dir(solver) if not method.startswith('_')]
for method in sorted(methods):
    print(f"  - {method}")

# Check if we have the right initialization method
print(f"\nHas 'initialize_system': {hasattr(solver, 'initialize_system')}")
print(f"Has 'initialize_fields': {hasattr(solver, 'initialize_fields')}")
print(f"Has 'evolve': {hasattr(solver, 'evolve')}")
print(f"Has 'evolve_system': {hasattr(solver, 'evolve_system')}")
