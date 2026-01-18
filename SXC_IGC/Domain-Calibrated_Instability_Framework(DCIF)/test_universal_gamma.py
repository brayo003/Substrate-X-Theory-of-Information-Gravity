import numpy as np

print("=== TEST: IS THE SUBSTRATE UNIVERSAL? ===\n")
print("Hypothesis: γ_observed * m_object = Γ(ρ), a universal function.\n")

# Known systems: (Name, mass [kg], estimated γ [s⁻¹], environment ρ [kg/m³])
systems = [
    ("Pioneer (approx)", 250, 1e-10 / 1.2e-8, 1.4e-16),  # γ ~ a_anomaly / v
    ("Lab Torsion Pendulum", 1e-3, 1/(500e6), 1.2),      # γ ~ 1/τ, rough guess
    ("Muon in g-2", 1.883e-28, 1.0e-6, 1e-17)           # Placeholder γ for illustration
]

for name, m, gamma_est, rho in systems:
    Gamma = m * gamma_est
    print(f"{name:25} m={m:.2e} kg, γ~{gamma_est:.2e} s⁻¹, ρ={rho:.2e} kg/m³")
    print(f"  → Γ = mγ = {Gamma:.2e} kg/s")
    print(f"  → Does Γ(ρ) follow Aρ^α? Γ/(Aρ^α) = {Gamma/(1.58e-09 * rho**1.254):.2e}\n")
