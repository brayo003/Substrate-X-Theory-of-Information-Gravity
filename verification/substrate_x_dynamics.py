import numpy as np
import matplotlib.pyplot as plt

def analyze_tension_dynamics(r_range=(-2, 2), a=1.0, b=1.0):
    """Analyze fixed points and stability of dx/dt = r*x + a*x² - b*x³"""
    
    rs = np.linspace(r_range[0], r_range[1], 100)
    results = []
    
    for r in rs:
        # Find fixed points (dx/dt = 0)
        discriminant = a**2 + 4*b*r
        
        if discriminant >= 0:
            x1 = (a + np.sqrt(discriminant)) / (2*b)
            x2 = (a - np.sqrt(discriminant)) / (2*b)
            
            # Stability analysis (derivative at fixed point)
            # f'(x) = r + 2a*x - 3b*x²
            stability1 = "Stable" if (r + 2*a*x1 - 3*b*x1**2) < 0 else "Unstable"
            stability2 = "Stable" if (r + 2*a*x2 - 3*b*x2**2) < 0 else "Unstable"
            
            results.append({
                'r': r,
                'x1': x1, 'stable1': stability1,
                'x2': x2, 'stable2': stability2,
                'has_fixed_points': True
            })
        else:
            results.append({
                'r': r,
                'x1': None, 'stable1': None,
                'x2': None, 'stable2': None,
                'has_fixed_points': False
            })
    
    return results

def plot_bifurcation(results):
    """Plot bifurcation diagram"""
    rs = [r['r'] for r in results]
    x1s = [r['x1'] if r['x1'] is not None else np.nan for r in results]
    x2s = [r['x2'] if r['x2'] is not None else np.nan for r in results]
    
    plt.figure(figsize=(10, 6))
    plt.plot(rs, x1s, 'b-', label='Fixed point 1', linewidth=2)
    plt.plot(rs, x2s, 'r-', label='Fixed point 2', linewidth=2)
    
    # Highlight stable/unstable (assuming you calculate stability)
    plt.axvline(x=0, color='gray', linestyle='--', alpha=0.5, label='Critical r=0')
    
    plt.xlabel('Growth rate (r)')
    plt.ylabel('Fixed point value (x)')
    plt.title('Bifurcation Diagram: dx/dt = r·x + a·x² - b·x³')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('bifurcation_diagram.png', dpi=150, bbox_inches='tight')
    print("Saved bifurcation_diagram.png")
    plt.show()

if __name__ == "__main__":
    print("=== Substrate X Dynamical Systems Analysis ===")
    print("Model: dx/dt = r·x + a·x² - b·x³")
    print("Where x represents system tension")
    print("\n" + "="*50)
    
    # Test specific cases
    test_cases = [
        {"r": 1.0, "label": "Positive growth (bistable)"},
        {"r": -1.0, "label": "Negative growth (monostable)"},
        {"r": 0.0, "label": "Critical point"}
    ]
    
    for case in test_cases:
        r = case["r"]
        print(f"\nCase: {case['label']} (r = {r})")
        
        discriminant = 1**2 + 4*1*r  # a=1, b=1
        
        if discriminant >= 0:
            x1 = (1 + np.sqrt(discriminant)) / 2
            x2 = (1 - np.sqrt(discriminant)) / 2
            print(f"  Fixed points: x₁ = {x1:.3f}, x₂ = {x2:.3f}")
            
            # Stability
            df1 = r + 2*1*x1 - 3*1*x1**2
            df2 = r + 2*1*x2 - 3*1*x2**2
            print(f"  Stability: x₁ is {'Stable' if df1 < 0 else 'Unstable'} (f'={df1:.3f})")
            print(f"             x₂ is {'Stable' if df2 < 0 else 'Unstable'} (f'={df2:.3f})")
        else:
            print(f"  No real fixed points (discriminant = {discriminant:.3f})")
        
        print(f"  x=0 is {'Stable' if r < 0 else 'Unstable'}")
    
    print("\n" + "="*50)
    print("Generating bifurcation diagram...")
    
    # Full analysis and plot
    results = analyze_tension_dynamics(r_range=(-1.5, 1.5))
    plot_bifurcation(results)
    
    print("\n=== Interpretation ===")
    print("• r < 0: Single stable state at x=0 (monostable)")
    print("• r = 0: Critical point (bifurcation)")
    print("• r > 0: Two stable states, x=0 unstable (bistable)")
    print("\nThis matches observed system behaviors:")
    print("• Some systems always return to calm (r < 0)")
    print("• Some systems 'tip' into persistent states (r > 0)")
    print("• Explains hysteresis and tipping points")
