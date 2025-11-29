import numpy as np

# Given delta2 (measured/assumed), find tauF value (with tauE fixed) that yields C=2
def find_tauF_for_C2(delta2, tauE=1.0):
    # target: delta2 * sqrt(tauF / tauE) = 2  => tauF = (2/delta2)**2 * tauE
    tauF = (2.0 / delta2)**2 * tauE
    return tauF

print("Parameter fitting for C=2:")
print("-" * 30)
for d2 in [0.4, 0.5, 1.0]:
    ratio = (2.0/d2)**2
    tauF = find_tauF_for_C2(d2)
    print(f"delta2 = {d2} -> tauF/tauE required = {ratio:.4f} -> tauF (if tauE=1) = {tauF:.4f}")
