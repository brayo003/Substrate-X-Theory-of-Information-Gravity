import numpy as np

def C_univ(delta1, delta2, tauE, tauF):
    R = (tauF/tauE)**0.5
    return R * delta1  # general expression (at bifurcation delta1=delta2 gives R*delta2)

cases = [
    (1.0, 1.0, 1.0, 4.0),
    (0.5, 0.5, 1.0, 16.0),
    (1.0, 0.5, 2.0, 8.0),
    (0.8, 0.4, 3.0, 9.6),
]

print("Testing cases with new R definition:")
print("R = sqrt(tauF/tauE)")
print("-" * 50)

for i,(d1,d2,tE,tF) in enumerate(cases,1):
    C = C_univ(d1,d2,tE,tF)
    print(f"Case {i}: δ1={d1}, δ2={d2}, τE={tE}, τF={tF} -> C_universal = {C:.6f}")

# Also compute predicted time ratio for C=2 given δ2:
def required_ratio_for_C2(delta2):
    return (4.0 / (delta2**2))

print("\nRequired tauF/tauE ratios for C=2:")
print("-" * 30)
for d2 in [0.5, 0.75, 1.0]:
    print(f"delta2 = {d2} => required tauF/tauE = {required_ratio_for_C2(d2):.4f}")
