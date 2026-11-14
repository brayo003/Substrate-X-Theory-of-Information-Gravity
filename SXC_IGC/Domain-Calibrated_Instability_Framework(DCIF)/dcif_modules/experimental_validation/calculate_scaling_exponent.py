import numpy as np
import matplotlib.pyplot as plt

# Your actual data from the audit
systems = {
    "Quantum": {"scale": 1e-15, "beta": 0.9533, "gamma": 0.0393, "ratio": 24.26},
    "Logistics": {"scale": 1e3, "beta": 1.2500, "gamma": 0.0500, "ratio": 25.00},
    "Seismic": {"scale": 1e6, "beta": 18.3916, "gamma": 0.0403, "ratio": 456.37},
}

# Extract arrays
names = list(systems.keys())
scales = np.array([systems[n]["scale"] for n in names])
ratios = np.array([systems[n]["ratio"] for n in names])
betas = np.array([systems[n]["beta"] for n in names])
gammas = np.array([systems[n]["gamma"] for n in names])

# Calculate log-log scaling
log_scales = np.log10(scales)
log_ratios = np.log10(ratios)

# Fit line: log(β/γ) = α * log(scale) + C
A = np.vstack([log_scales, np.ones(len(log_scales))]).T
alpha, C = np.linalg.lstsq(A, log_ratios, rcond=None)[0]

print("SXC-V12: UNIVERSAL SCALING LAW CALCULATION")
print("="*60)
print(f"{'System':<12} | {'Scale (m)':<12} | {'β/γ':<10} | {'log10(Scale)':<12} | {'log10(β/γ)':<12}")
print("-"*60)

for i, name in enumerate(names):
    print(f"{name:<12} | {scales[i]:<12.1e} | {ratios[i]:<10.2f} | {log_scales[i]:<12.3f} | {log_ratios[i]:<12.3f}")

print("\n" + "="*60)
print(f"SCALING LAW: log10(β/γ) = {alpha:.4f} × log10(Scale) + {C:.4f}")
print(f"Or: β/γ ∝ Scale^{alpha:.4f}")
print(f"\nInterpretation: Fragility (β/γ) scales with Scale^{alpha:.4f}")

# Calculate R-squared
predicted = alpha * log_scales + C
ss_res = np.sum((log_ratios - predicted)**2)
ss_tot = np.sum((log_ratios - np.mean(log_ratios))**2)
r_squared = 1 - (ss_res / ss_tot)

print(f"R-squared: {r_squared:.4f}")

# Enhanced plot
plt.figure(figsize=(12, 8))

# Plot 1: Log-Log scaling
plt.subplot(2, 2, 1)
plt.loglog(scales, ratios, 'ro-', lw=2, markersize=10)
for i, name in enumerate(names):
    plt.annotate(name, (scales[i], ratios[i]), textcoords="offset points", 
                 xytext=(0,10), ha='center', fontsize=9)
plt.plot(scales, 10**(alpha * log_scales + C), 'b--', alpha=0.7, label=f'Fit: β/γ ∝ Scale^{alpha:.2f}')
plt.title("Universal Scaling: β/γ vs Spatial Scale")
plt.xlabel("Spatial Scale (meters)")
plt.ylabel("Fragility Ratio (β/γ)")
plt.grid(True, which="both", ls="-", alpha=0.3)
plt.legend()

# Plot 2: β vs γ by system
plt.subplot(2, 2, 2)
for i, name in enumerate(names):
    plt.plot(betas[i], gammas[i], 'o', markersize=12, label=name)
    plt.annotate(f"β/γ={ratios[i]:.0f}", (betas[i], gammas[i]), 
                 textcoords="offset points", xytext=(5,5), fontsize=8)
plt.xlabel("β (Excitation Sensitivity)")
plt.ylabel("γ (Damping Rate)")
plt.title("β-γ Space by System")
plt.grid(True, alpha=0.3)
plt.legend()

# Plot 3: γ distribution
plt.subplot(2, 2, 3)
plt.bar(names, gammas, color=['red', 'orange', 'green'])
plt.axhline(y=0.04, color='r', linestyle='--', alpha=0.5, label='γ=0.04 class')
plt.axhline(y=0.05, color='orange', linestyle='--', alpha=0.5, label='γ=0.05 class')
plt.ylabel("γ value")
plt.title("γ Distribution (Note: Both ≈ 0.04-0.05!)")
plt.legend(fontsize=8)

# Plot 4: β distribution
plt.subplot(2, 2, 4)
plt.bar(names, betas, color=['red', 'orange', 'green'])
plt.ylabel("β value")
plt.title("β Distribution (Seismic has 19× Quantum β!)")
plt.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5, label='β=1 reference')

plt.tight_layout()
plt.savefig('complete_scaling_analysis.png', dpi=150)
print(f"\nPlot saved as: complete_scaling_analysis.png")

# Calculate warning time scaling
print("\n" + "="*60)
print("EARLY WARNING TIME SCALING:")
print("-"*60)
for i, name in enumerate(names):
    # Time to reach 70% tension (tangle point)
    t_tangle = -np.log(0.3) / gammas[i]
    # Relative to quantum
    if i > 0:
        rel_to_quantum = t_tangle / (-np.log(0.3) / systems["Quantum"]["gamma"])
        print(f"{name:<12}: t_tangle = {t_tangle:6.2f} time units ({rel_to_quantum:.2f}x Quantum)")
    else:
        print(f"{name:<12}: t_tangle = {t_tangle:6.2f} time units (reference)")
