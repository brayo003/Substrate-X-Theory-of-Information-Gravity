"""
Test: Solver Invariance
"""

import numpy as np
from scipy.integrate import solve_ivp

def V12_dynamics(t, y, r=0.153, a=1.0, b=1.0):
    """V12 Engine dynamics"""
    I, v = y
    dvdt = r + 2*a*I - 3*b*I**2
    return [v, dvdt]

def main():
    print("PHASE IV: UNIVERSALITY OR DEATH")
    print("=" * 60)
    
    solvers = ['RK45', 'BDF', 'Radau']
    results = []
    
    for solver in solvers:
        print(f"\nTesting {solver}...")
        try:
            sol = solve_ivp(
                V12_dynamics,
                (0, 30),
                [0.0, 0.01],
                method=solver,
                max_step=0.1,
                rtol=1e-8
            )
            
            I = sol.y[0]
            I_max = np.max(np.abs(I))
            I_final = I[-1]
            
            print(f"  Max |I|: {I_max:.4f}")
            print(f"  Final I: {I_final:.4f}")
            
            results.append({
                'solver': solver,
                'I_max': I_max,
                'I_final': I_final
            })
            
        except Exception as e:
            print(f"  Failed: {str(e)}")
    
    if len(results) < 2:
        print("\nNot enough successful solvers")
        return False
    
    # Check consistency
    I_max_vals = [r['I_max'] for r in results]
    I_max_mean = np.mean(I_max_vals)
    I_max_std = np.std(I_max_vals)
    
    print(f"\nConsistency check:")
    print(f"  Mean I_max: {I_max_mean:.4f}")
    print(f"  Std I_max: {I_max_std:.4f}")
    print(f"  CV: {I_max_std/I_max_mean:.4f}")
    
    print("\n" + "=" * 60)
    if I_max_std/I_max_mean < 0.1:
        print("✓ SOLVER INVARIANCE CONFIRMED")
        print("  Dynamics are physical, not numerical")
        return True
    else:
        print("✗ SOLVER INVARIANCE VIOLATED")
        return False

if __name__ == "__main__":
    main()
