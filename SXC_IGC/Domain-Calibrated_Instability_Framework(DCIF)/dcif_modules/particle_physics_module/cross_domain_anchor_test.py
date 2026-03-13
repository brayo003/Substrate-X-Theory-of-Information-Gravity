import numpy as np

# ===== 1. ANCHOR FROM QUANTT (Macroscopic Substrate X) =====
A = 1.58e-09
alpha = 1.254
rho = 1.2e-8  # Approximate density in a lab vacuum (kg/m³). ADJUST AS NEEDED.
gamma_beta_ratio_anchor = A * (rho ** alpha)

print("=== CROSS-DOMAIN ANCHOR TEST (Substrate X) ===")
print(f"Macroscopic Anchor (from quantt):")
print(f"  Density ρ = {rho:.2e} kg/m³")
print(f"  γ/β = Aρ^α = {gamma_beta_ratio_anchor:.2e}")

# ===== 2. LINK TO PARTICLE PHYSICS MODULE =====
gamma_dcif = 0.0852  # From coefficients.json
G_B_THEORY = 1.15e-3
k = (G_B_THEORY ** 2) / gamma_dcif

print(f"\nParticle Physics Bridge:")
print(f"  DCIF γ (particle module) = {gamma_dcif}")
print(f"  Theory baryon coupling g_b = {G_B_THEORY:.2e}")
print(f"  Derived scaling k = g_b^2 / γ = {k:.2e}")

# ===== 3. PREDICT MUON COUPLING FROM ANCHOR =====
beta_dcif = 0.8671
gamma_from_anchor = gamma_beta_ratio_anchor * beta_dcif
g_mu_squared_predicted = k * gamma_from_anchor
g_mu_predicted = np.sqrt(g_mu_squared_predicted)

print(f"\nPrediction from Macroscopic Anchor:")
print(f"  Using DCIF β = {beta_dcif}")
print(f"  Predicted γ = (γ/β) × β = {gamma_from_anchor:.2e}")
print(f"  Predicted muon coupling g_μ = √(k × γ) = {g_mu_predicted:.2e}")

# ===== 4. COMPARE WITH INDEPENDENT MUON G-2 CALCULATION =====
def calculate_required_g_mu():
    TARGET_TENSION = 251e-11
    M_X17 = 17.01e6
    required_g = np.sqrt(TARGET_TENSION * (2 * np.pi) * (M_X17 / 105.66e6)**2 * (4 * np.pi))
    return required_g

g_mu_from_g2 = calculate_required_g_mu()
print(f"\nIndependent Check (from muon g-2 anomaly):")
print(f"  Required g_μ to fix Δa_μ = {g_mu_from_g2:.2e}")

# ===== 5. CONSISTENCY ANALYSIS =====
print(f"\n=== CONSISTENCY ANALYSIS ===")
ratio = g_mu_predicted / g_mu_from_g2
print(f"Predicted / Required ratio = {ratio:.2f}")

if 0.1 < ratio < 10:
    print("✅ RESULT: ANCHOR HOLDS.")
    print("The macroscopic Substrate X damping predicts a muon coupling within an order of magnitude of the value needed for g-2.")
else:
    print("⚠️  RESULT: ANCHOR STRAINED.")
    print("The predicted and required couplings differ significantly.")

# ===== 6. CHECK AGAINST GLOBAL CONSTRAINTS =====
print(f"\n--- Quick Global Constraint Check ---")
print(f"Predicted baryon coupling g_b (scaled from g_μ):")
print(f"  If g_b ≈ g_μ ≈ {g_mu_predicted:.2e}, compare to Atomki limit ~1.2e-3.")
if g_mu_predicted < 1.2e-3:
    print("  Within Atomki signal range.")
else:
    print("  Exceeds typical bounds.")
