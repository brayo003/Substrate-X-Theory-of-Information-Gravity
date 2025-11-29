import numpy as np

def C_at_bif(delta2, tauE, tauF):
    return delta2 * np.sqrt(tauF/tauE)

delta2 = 0.5
tauE = 1.0
ratios = np.linspace(0.1, 50, 1000)
Cvals = [C_at_bif(delta2, tauE, r*tauE) for r in ratios]

# compute where C is near 2
close = [(r, c) for r,c in zip(ratios, Cvals) if abs(c-2.0) < 0.01]

print(f"Sensitivity analysis for delta2 = {delta2}:")
print(f"C_universal = delta2 * sqrt(tauF/tauE)")
print(f"Range where C ≈ 2.0 (within 0.01):")
if close:
    print(f"First 5 matches: {close[:5]}")
    print(f"Total matches: {len(close)} out of {len(ratios)} ratios tested")
else:
    print("No matches found in tested range")
