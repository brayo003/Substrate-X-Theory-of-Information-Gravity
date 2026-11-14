#!/usr/bin/env python3
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

# Check what the parent method actually returns
solver = CompleteFieldTheorySolver(alpha=1e-5, delta1=25.0)
solver.initialize_system('gaussian')

print("Testing parent compute_field_evolution method:")
try:
    result = solver.compute_field_evolution()
    print(f"Return type: {type(result)}")
    print(f"Return length: {len(result) if hasattr(result, '__len__') else 'N/A'}")
    
    if hasattr(result, '__len__') and len(result) == 2:
        dE_dt, dF_dt = result
        print(f"dE_dt shape: {dE_dt.shape}, range: [{np.min(dE_dt):.6f}, {np.max(dE_dt):.6f}]")
        print(f"dF_dt shape: {dF_dt.shape}, range: [{np.min(dF_dt):.6f}, {np.max(dF_dt):.6f}]")
    else:
        print(f"Unexpected return: {result}")
        
except Exception as e:
    print(f"Error: {e}")

print(f"\nAvailable attributes:")
attrs = [attr for attr in dir(solver) if not attr.startswith('_')]
for attr in sorted(attrs):
    print(f"  {attr}")
