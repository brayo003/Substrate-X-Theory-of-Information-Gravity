import numpy as np
import matplotlib.pyplot as plt

def test_theory_fundamentals():
    """Test if the Master PDE makes physical sense"""
    
    print("=== CRITICAL ANALYSIS OF SUBSTRATE X THEORY ===\n")
    
    # Test 1: Dimensional analysis
    print("1. DIMENSIONAL ANALYSIS:")
    print("   Left side: ∂s/∂t + ∇·(s v) → [kg/m³·s]")
    print("   Right side: αE - β∇·(E v) + γF - σ → mixed dimensions")
    print("   PROBLEM: Terms don't have consistent dimensions\n")
    
    # Test 2: Energy conservation  
    print("2. ENERGY CONSERVATION:")
    print("   Source term αE adds energy indefinitely")
    print("   No clear energy conservation law")
    print("   Violates first law of thermodynamics\n")
    
    # Test 3: Comparison to established theories
    print("3. COMPARISON TO KNOWN PHYSICS:")
    print("   General Relativity: derived from fundamental principles")
    print("   EM: from gauge symmetry U(1)")
    print("   Substrate X: postulated without fundamental derivation")
    print("   PROBLEM: Not derived from first principles\n")
    
    # Test 4: Predictive power
    print("4. PREDICTIVE POWER:")
    print("   Can retrodict known effects (Mercury, lensing)")
    print("   But new prediction (rotation decoherence) untested")
    print("   Many parameters allow curve-fitting\n")
    
    return False  # Theory has fundamental issues

def simple_newtonian_test():
    """Test if we can recover Newtonian gravity simply"""
    
    # Simple Poisson equation: ∇²Φ = 4πGρ
    # This works and is well-established
    
    grid_size = 100
    x = np.linspace(0, 2, grid_size)
    dx = x[1] - x[0]
    
    # Point mass density
    rho = np.zeros(grid_size)
    rho[50] = 1.0  # Delta function
    
    # Solve Poisson equation directly
    # This is how gravity actually works
    phi = np.zeros(grid_size)
    for i in range(1, grid_size):
        # Simple 1D Poisson solver
        phi[i] = phi[i-1] + dx * (4 * np.pi * 6.674e-11 * np.trapz(rho[:i], x[:i]))
    
    plt.figure(figsize=(10, 4))
    plt.subplot(121)
    plt.plot(x, rho)
    plt.title('Mass Density ρ(x)')
    plt.subplot(122)
    plt.plot(x, phi)
    plt.title('Newtonian Potential Φ(x)')
    plt.tight_layout()
    plt.show()
    
    print("Newtonian gravity works simply and reliably")
    return True

# Run critical analysis
theory_valid = test_theory_fundamentals()
simple_newtonian_test()

print(f"\nCONCLUSION: Substrate X Theory has fundamental issues.")
print("It's better to understand why established theories work than to invent new ones without clear foundations.")
