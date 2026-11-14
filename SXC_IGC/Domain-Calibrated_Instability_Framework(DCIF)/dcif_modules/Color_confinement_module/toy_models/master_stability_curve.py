import numpy as np
import matplotlib.pyplot as plt

def generate_curve():
    # R-axis: Logarithmic scale from Sub-Planck to Macro
    r = np.logspace(-16, 1, 1000) # fm to meters
    
    # 1. STRONG FORCE (Baryon NLI) - V = sigma*r - alpha/r
    sigma = 0.9
    alpha_s = 0.3
    nli_strong = ((sigma * r) - (alpha_s / r)) / 0.756
    
    # 2. ELECTROMAGNETIC (Lepton NLI) - V = alpha/r
    alpha_em = 1/137.036
    b_gov = 1e-10
    nli_em = (alpha_em / r) / (1 + (b_gov / r**2))
    
    # 3. GRAVITY (Schwarzschild NLI) - Linear scaling for a solar mass
    # Normalized to hit 1.0 at 3000m
    nli_gravity = 3000 / (r * 1e15) # Scaling r back to macro for vis

    plt.figure(figsize=(12, 7))
    
    # Plotting the "Shatter-Point"
    plt.axhline(y=1.0, color='r', linestyle='--', label='V12 SHATTER-POINT (Limit)')
    plt.fill_between(r, 1.0, 2.0, color='red', alpha=0.1, label='Swampland (Illegal)')
    plt.fill_between(r, 0, 1.0, color='green', alpha=0.05, label='Landscape (Physical)')

    # Force Curves
    plt.plot(r, nli_strong, label='Strong Force (Baryon Confinement)', color='blue', linewidth=2)
    plt.plot(r, nli_em, label='Electromagnetic (Electron Density)', color='orange', linewidth=2)
    
    plt.xscale('log')
    plt.ylim(0, 1.5)
    plt.title('⚛️ MASTER STABILITY CURVE: SXC-IGC V12')
    plt.xlabel('Interaction Scale (r in fm)')
    plt.ylabel('Normalized Load Index (NLI)')
    plt.legend()
    plt.grid(True, which="both", ls="-", alpha=0.2)
    
    plt.savefig('stability_reports/master_stability_curve.png')
    print("⚛️ MASTER CURVE GENERATED: Check stability_reports/master_stability_curve.png")
    print("Logic Summary:")
    print("- Strong Force hits the Shatter-Point as distance INCREASES (Confinement).")
    print("- EM and Gravity hit the Shatter-Point as distance DECREASES (Singularity Protection).")

if __name__ == "__main__":
    generate_curve()
