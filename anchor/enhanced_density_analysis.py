#!/usr/bin/env python3
"""
Enhanced Density-Viscosity Correlation Analysis
- Includes error estimates on measurements
- Calculates statistical significance
- Tests alternative models
- Saves comprehensive results
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy import stats
import uncertainties as unc
from uncertainties import unumpy

# 1. DATA WITH ESTIMATED UNCERTAINTIES
# Density estimates (kg/m^3) with reasonable uncertainty bounds
densities = np.array([1.4e-16, 1.0e-21, 1.0e-27])
density_err = np.array([0.3e-16, 0.2e-21, 0.3e-27])  # ~20% relative error

# Measured η with uncertainties based on your analyses
measured_eta = np.array([0.0531, 0.0185, 3.82e-16])
eta_err = np.array([0.005, 0.002, 1.0e-16])  # Conservative estimates

# Create arrays with uncertainties
rho_u = unumpy.uarray(densities, density_err)
eta_u = unumpy.uarray(measured_eta, eta_err)

print("="*70)
print("ENHANCED DENSITY-VISCOSITY CORRELATION ANALYSIS")
print("="*70)
print("\nInput Data with Uncertainties:")
for i, (rho, eta) in enumerate(zip(rho_u, eta_u)):
    print(f"  Point {i+1}: ρ = {rho:.2e}, η = {eta:.2e}")

# 2. POWER LAW FIT: η(ρ) = A * ρ^b
def power_law(rho, A, b):
    return A * np.power(rho, b)

# Weighted fit (inverse variance weighting)
weights = 1.0 / (eta_err**2)
params, cov = curve_fit(power_law, densities, measured_eta, 
                       sigma=eta_err, absolute_sigma=True,
                       p0=[1e15, 1.0])  # Initial guess

A_fit, b_fit = params
A_err, b_err = np.sqrt(np.diag(cov))

print(f"\n--- POWER LAW FIT RESULTS ---")
print(f"Amplitude A:     ({A_fit:.3e} ± {A_err:.3e})")
print(f"Exponent b:      ({b_fit:.4f} ± {b_err:.4f})")
print(f"Correlation:     η ∝ ρ^{b_fit:.3f}")

# 3. STATISTICAL SIGNIFICANCE TESTS
print(f"\n--- STATISTICAL SIGNIFICANCE ---")

# Calculate R²
eta_pred = power_law(densities, A_fit, b_fit)
ss_res = np.sum((measured_eta - eta_pred)**2)
ss_tot = np.sum((measured_eta - np.mean(measured_eta))**2)
r_squared = 1 - (ss_res / ss_tot)
print(f"R² = {r_squared:.4f}")

# Pearson correlation (log space)
log_rho = np.log10(densities)
log_eta = np.log10(measured_eta)
pearson_r, pearson_p = stats.pearsonr(log_rho, log_eta)
print(f"Pearson r (log): {pearson_r:.4f}, p-value: {pearson_p:.4e}")

# Test if b is significantly different from 0
b_zscore = b_fit / b_err
b_pvalue = 2 * (1 - stats.norm.cdf(abs(b_zscore)))
print(f"b significance: z = {b_zscore:.2f}, p = {b_pvalue:.4e}")

# 4. ALTERNATIVE MODELS COMPARISON
print(f"\n--- MODEL COMPARISON ---")

# Linear model: η = m*ρ + c
def linear_model(rho, m, c):
    return m*rho + c

# Exponential model: η = α*exp(β*ρ)
def exp_model(rho, alpha, beta):
    return alpha * np.exp(beta * rho)

# Fit all models
models = {
    "Power Law": power_law,
    "Linear": linear_model,
    "Exponential": exp_model
}

results = {}
for name, model in models.items():
    try:
        params, _ = curve_fit(model, densities, measured_eta, 
                             sigma=eta_err, maxfev=5000)
        eta_pred = model(densities, *params)
        chi2 = np.sum(((measured_eta - eta_pred)/eta_err)**2)
        results[name] = {"params": params, "chi2": chi2, "pred": eta_pred}
        print(f"  {name:12} χ² = {chi2:.4f}")
    except:
        print(f"  {name:12} Failed to fit")

# 5. PHYSICAL INTERPRETATION
print(f"\n--- PHYSICAL INTERPRETATION ---")

if b_fit > 0.7 and b_pvalue < 0.05:
    print(f"✓ STRONG EVIDENCE for density-dependent viscosity")
    print(f"  Exponent b ≈ {b_fit:.2f} means η ∝ ρ^{b_fit:.2f}")
    
    if abs(b_fit - 1.0) < 0.2:
        print(f"  → Consistent with LINEAR scaling (η ∝ ρ)")
        print(f"  → Supports 'Information Clog' hypothesis")
        print(f"  → Substrate interacts with baryonic matter")
    elif b_fit > 1.0:
        print(f"  → SUPER-LINEAR scaling (η ∝ ρ^{b_fit:.2f})")
        print(f"  → Collective effects or threshold behavior")
    else:
        print(f"  → SUB-LINEAR scaling")
        print(f"  → Saturation or screening effects")
else:
    print(f"✗ Insufficient evidence for density dependence")

# Calculate what this means for different environments
print(f"\n--- PREDICTIONS FOR OTHER ENVIRONMENTS ---")

# Using the fitted power law
def predict_eta(rho):
    return A_fit * (rho**b_fit)

environments = {
    "Earth's Surface": 1.2e3,      # kg/m³
    "Interstellar Medium": 1e-21,  # kg/m³  
    "Galactic Halo": 1e-24,        # kg/m³
    "Cosmic Web Filament": 1e-26,  # kg/m³
    "Deep Void": 1e-30             # kg/m³
}

print("Predicted viscosities:")
for env, rho in environments.items():
    eta_pred = predict_eta(rho)
    print(f"  {env:25}: η ≈ {eta_pred:.2e}")

# 6. VISUALIZATION
plt.figure(figsize=(14, 5))

# Plot 1: Data with error bars and fit
plt.subplot(1, 2, 1)
plt.errorbar(densities, measured_eta, xerr=density_err, yerr=eta_err, 
             fmt='ro', capsize=5, label='Data with errors')

# Plot fitted curve
rho_plot = np.logspace(-30, -15, 200)
eta_plot = power_law(rho_plot, A_fit, b_fit)
plt.loglog(rho_plot, eta_plot, 'b-', label=f'Fit: η ∝ ρ^{b_fit:.2f}')

plt.xlabel("Local Matter Density ρ (kg/m³)", fontsize=12)
plt.ylabel("Substrate Viscosity η", fontsize=12)
plt.title("Density-Viscosity Correlation", fontsize=14)
plt.grid(True, which="both", ls="-", alpha=0.2)
plt.legend()

# Annotate points
labels = ["Solar System\n(Pioneer)", "Galactic Disk\n(Pulsar)", "Cosmic Void\n(LIGO)"]
for i, (x, y, label) in enumerate(zip(densities, measured_eta, labels)):
    plt.annotate(label, (x, y), xytext=(10, 10 if i==0 else -20), 
                 textcoords='offset points', fontsize=9,
                 bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.7))

# Plot 2: Residuals
plt.subplot(1, 2, 2)
residuals = (measured_eta - eta_pred) / eta_err
plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
plt.axhline(y=2, color='r', linestyle='--', alpha=0.3, label='2σ')
plt.axhline(y=-2, color='r', linestyle='--', alpha=0.3)
plt.errorbar(densities, residuals, xerr=density_err, fmt='bo', capsize=5)
plt.xlabel("Density ρ (kg/m³)", fontsize=12)
plt.ylabel("Standardized Residuals", fontsize=12)
plt.title(f"Residuals (χ²/ν = {results['Power Law']['chi2']/1:.2f})", fontsize=14)
plt.xscale('log')
plt.grid(True, alpha=0.3)
plt.legend()

plt.tight_layout()
plt.savefig('enhanced_density_correlation.png', dpi=150, bbox_inches='tight')
print(f"\n✓ Plot saved as 'enhanced_density_correlation.png'")

# 7. SAVE RESULTS
with open('density_correlation_results.txt', 'w') as f:
    f.write("# SUBSTRATE X: DENSITY-VISCOSITY CORRELATION RESULTS\n")
    f.write("# ================================================\n\n")
    f.write(f"Power Law Fit: η = ({A_fit:.6e}) × ρ^{b_fit:.6f}\n")
    f.write(f"Uncertainties: A_err = {A_err:.6e}, b_err = {b_err:.6f}\n\n")
    f.write(f"Statistical Significance:\n")
    f.write(f"  R² = {r_squared:.6f}\n")
    f.write(f"  Pearson r = {pearson_r:.6f}, p = {pearson_p:.6e}\n")
    f.write(f"  b significance: z = {b_zscore:.2f}, p = {b_pvalue:.6e}\n\n")
    f.write("Predictions for Various Environments:\n")
    for env, rho in environments.items():
        eta_pred = predict_eta(rho)
        f.write(f"  {env:25}: ρ = {rho:.2e} → η ≈ {eta_pred:.2e}\n\n")
    f.write("CONCLUSION: ")
    if b_fit > 0.7 and b_pvalue < 0.05:
        f.write("Strong evidence for density-dependent viscosity.\n")
        f.write(f"Supports 'Information Clog' hypothesis with η ∝ ρ^{b_fit:.2f}.\n")
    else:
        f.write("Insufficient evidence for density dependence.\n")

print("="*70)
print("✓ Analysis complete! Results saved to:")
print("  - enhanced_density_correlation.png")
print("  - density_correlation_results.txt")
print("\nNEXT STEPS:")
print("  1. Verify density estimates with astrophysical literature")
print("  2. Test with more data points (more GW events, lab experiments)")
print("  3. Derive theoretical basis for η ∝ ρ from first principles")
print("="*70)
