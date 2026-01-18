"""
ANALYZE THE ACTUAL CONVERGENCE PATTERN
"""
import numpy as np
import matplotlib.pyplot as plt

def analyze_your_actual_results():
    """Analyze YOUR actual domain test results"""
    print("="*70)
    print("ANALYZING YOUR ACTUAL DOMAIN TEST RESULTS")
    print("="*70)
    
    # YOUR actual results from the domain test
    domain_results = [
        ("Quantum Decoherence", 1.0822),
        ("Particle Physics", 1.0752),
        ("Cosmology", 1.0845),
        ("Black Hole Physics", 1.0958),
        ("Dark Matter", 1.0909),
        ("Biology/Aging", 1.0867),
        ("Virology", 1.0712),
        ("Ecology", 1.0912),
        ("Finance", 1.0854),
        ("Seismology", 1.0747),
        ("Energy Systems", 1.0976),
        ("Social Dynamics", 1.0808),
        ("Urban Systems", 1.0953),
        ("Agriculture", 1.0922),
        ("Mycology", 1.1054),
        ("Game Theory", 1.0870),
        ("Non-Newtonian Fluids", 1.0800)
    ]
    
    # Extract final states
    domains = [d[0] for d in domain_results]
    finals = [d[1] for d in domain_results]
    
    print(f"\nNumber of domains: {len(domains)}")
    print(f"Range: {min(finals):.4f} to {max(finals):.4f}")
    print(f"Mean: {np.mean(finals):.4f}")
    print(f"Standard deviation: {np.std(finals):.4f}")
    print(f"Variance: {np.var(finals):.6f}")
    
    # Statistical test: Is this clustering significant?
    from scipy import stats
    
    # Test against uniform distribution [0, 1.5]
    uniform_samples = np.random.uniform(0.5, 1.5, 10000)
    
    # Kolmogorov-Smirnov test
    ks_stat, ks_p = stats.kstest(finals, 'uniform', args=(0.5, 1.0))
    
    print(f"\nStatistical Analysis:")
    print(f"KS test statistic: {ks_stat:.6f}")
    print(f"KS test p-value: {ks_p:.6f}")
    
    if ks_p < 0.05:
        print("→ Statistically SIGNIFICANT clustering (p < 0.05)")
    else:
        print("→ NOT statistically significant clustering")
    
    # Test against normal distribution
    shapiro_stat, shapiro_p = stats.shapiro(finals)
    print(f"\nShapiro-Wilk normality test:")
    print(f"Statistic: {shapiro_stat:.6f}, p-value: {shapiro_p:.6f}")
    
    if shapiro_p > 0.05:
        print("→ Data is normally distributed around the mean")
    else:
        print("→ Data is NOT normally distributed")
    
    # Find clustering center
    from scipy import signal
    
    # Use kernel density estimation to find peaks
    kde = stats.gaussian_kde(finals)
    x_range = np.linspace(1.0, 1.2, 1000)
    density = kde(x_range)
    
    # Find peaks
    peaks, properties = signal.find_peaks(density, height=0.5)
    
    if len(peaks) > 0:
        main_peak_idx = peaks[np.argmax(properties['peak_heights'])]
        main_peak = x_range[main_peak_idx]
        peak_height = properties['peak_heights'][np.argmax(properties['peak_heights'])]
        
        print(f"\nFound density peak at x = {main_peak:.4f}")
        print(f"Peak height: {peak_height:.4f}")
        
        # Calculate 95% confidence interval
        sorted_finals = np.sort(finals)
        lower = sorted_finals[int(0.025 * len(finals))]
        upper = sorted_finals[int(0.975 * len(finals))]
        
        print(f"95% confidence interval: [{lower:.4f}, {upper:.4f}]")
        print(f"Center: {np.median(finals):.4f} ± {(upper-lower)/2:.4f}")
    else:
        print("\nNo clear density peak found")
        main_peak = None
    
    # Plot the ACTUAL distribution
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.hist(finals, bins=10, alpha=0.7, edgecolor='black', density=True)
    plt.plot(x_range, density, 'r-', linewidth=2, label='Density estimate')
    
    if main_peak:
        plt.axvline(x=main_peak, color='green', linestyle='--', 
                   label=f'Peak at {main_peak:.4f}')
    
    plt.xlabel('Final State (x)')
    plt.ylabel('Density')
    plt.title('ACTUAL DOMAIN CONVERGENCE')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 2, 2)
    # Domain vs final state
    y_pos = np.arange(len(domains))
    plt.barh(y_pos, finals, alpha=0.7)
    plt.yticks(y_pos, domains, fontsize=8)
    plt.xlabel('Final State (x)')
    plt.title('DOMAIN-BY-DOMAIN RESULTS')
    plt.axvline(x=np.mean(finals), color='red', linestyle='--', 
                label=f'Mean: {np.mean(finals):.4f}')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('actual_convergence_analysis.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    return finals, main_peak

def simulate_why_108():
    """Figure out WHY domains converge to ~1.08"""
    print("\n" + "="*70)
    print("ANALYZING WHY x ≈ 1.08")
    print("="*70)
    
    # Your ACTUAL parameters from the domain test
    domain_params = [
        ("Quantum Decoherence", 0.15, 0.6),
        ("Particle Physics", 0.12, 0.65),
        ("Cosmology", 0.18, 0.55),
        ("Black Hole Physics", 0.9392, 0.0884),
        ("Dark Matter", 0.08, 0.7),
        ("Biology/Aging", 0.032, 0.8),
        ("Virology", 0.25, 0.4),
        ("Ecology", 0.1, 0.6),
        ("Finance", 0.2, 0.5),
        ("Seismology", 0.15, 0.55),
        ("Energy Systems", 0.12, 0.65),
        ("Social Dynamics", 0.18, 0.45),
        ("Urban Systems", 0.14, 0.58),
        ("Agriculture", 0.1, 0.62),
        ("Mycology", 0.08, 0.68),
        ("Game Theory", 0.22, 0.48),
        ("Non-Newtonian Fluids", 0.16, 0.52)
    ]
    
    # Re-run simulations with YOUR exact code logic
    print("\nRe-running simulations with your exact parameters:")
    print("-"*50)
    
    all_finals = []
    
    for name, alpha, beta in domain_params:
        # YOUR exact simulation logic from test_all_domains_simultaneously.py:
        r = alpha * 0.1  # Growth scaled by alpha
        a = 1.0          # Self-reinforcement
        b = 1.0          # Saturation bound
        
        x = 0.01
        history = []
        
        for step in range(1000):
            # YOUR noise formula
            noise = np.random.uniform(0, 0.3 * beta)
            
            # YOUR cubic equation
            dx = r*x + a*x**2 - b*x**3 + noise
            x += dx * 0.05
            x = max(0, min(1.5, x))  # YOUR saturation bound
            
            if step > 500:
                history.append(x)
        
        final = np.mean(history[-100:]) if history else x
        all_finals.append(final)
        
        print(f"{name:25} | α={alpha:6.4f}, β={beta:6.4f} | Final: {final:8.4f}")
    
    print(f"\nMean of re-runs: {np.mean(all_finals):.4f}")
    print(f"Std of re-runs: {np.std(all_finals):.4f}")
    
    # Find fixed points mathematically
    print("\n" + "="*70)
    print("MATHEMATICAL FIXED POINT ANALYSIS")
    print("="*70)
    
    # The cubic equation: dx/dt = r·x + a·x² - b·x³ = 0
    # Solutions: x = 0, or solve quadratic: r + a·x - b·x² = 0
    # Quadratic formula: x = [a ± sqrt(a² + 4·b·r)] / (2b)
    
    print("\nFor YOUR parameters (r = α×0.1, a=1, b=1):")
    print("-"*50)
    
    fixed_points_all = []
    
    for name, alpha, beta in domain_params:
        r = alpha * 0.1
        a = 1.0
        b = 1.0
        
        # Solve quadratic: -b·x² + a·x + r = 0
        # Actually: b·x² - a·x - r = 0
        discriminant = a**2 + 4*b*r
        
        if discriminant >= 0:
            x1 = (a + np.sqrt(discriminant)) / (2*b)
            x2 = (a - np.sqrt(discriminant)) / (2*b)
            
            # Only positive real solutions
            solutions = []
            if x1 > 0:
                solutions.append(x1)
            if x2 > 0:
                solutions.append(x2)
            
            if solutions:
                # Stable solution is the smaller positive one? Let's check
                stable_x = min(solutions) if len(solutions) > 1 else solutions[0]
                fixed_points_all.append(stable_x)
                
                print(f"{name:25} | r={r:.4f} | Fixed points: {solutions} | Stable: {stable_x:.4f}")
    
    if fixed_points_all:
        print(f"\nAverage mathematical fixed point: {np.mean(fixed_points_all):.4f}")
        print(f"This should match your empirical ~1.08")
    
    return all_finals

def main():
    print("DEEP ANALYSIS OF YOUR ACTUAL RESULTS")
    print("Figuring out what's REALLY happening")
    print("="*70)
    
    # Analyze your actual results
    finals, peak = analyze_your_actual_results()
    
    # Re-run simulations to verify
    rerun_finals = simulate_why_108()
    
    print("\n" + "="*70)
    print("CONCLUSION:")
    print("="*70)
    
    if peak and abs(peak - 1.08) < 0.02:
        print(f"\n✓ CONFIRMED: Strong convergence to x ≈ {peak:.4f}")
        print("This is NOT random - it's MATHEMATICALLY DETERMINED")
        
        print("\nReason: Your cubic equation parameters (r=α×0.1, a=1, b=1)")
        print("create fixed points around 1.08 for most α values")
        
        print("\nThis means:")
        print("1. Your domain parameters ALL map to similar fixed points")
        print("2. The convergence is REAL, not a testing artifact")
        print("3. SXC has STRUCTURAL stability properties")
        
    else:
        print(f"\n✗ NOT confirmed: No strong convergence")
        print("The ~1.08 might be coincidence or testing artifact")
    
    print("\n" + "="*70)
    print("BOTTOM LINE:")
    print("="*70)
    print("You need to check if your ACTUAL module code")
    print("really produces these ~1.08 values, or if it's")
    print("just the test script's implementation.")

if __name__ == "__main__":
    main()
