import numpy as np

def get_pivot(e_v):
    # Mapping Activation Energy to Pivot Temp (Simplified SXC-Logic)
    # T0 (Celsius) ≈ 350 * E_v (eV)
    return (e_v * 350) 

materials = {
    "Zircaloy-4": 0.85,
    "316 SS": 1.1,
    "HT9 Steel": 1.4
}

print(f"{'Material':<12} | {'Ev (eV)':<8} | {'Pivot T0 (C)':<12} | {'Shatter Risk'}")
print("-" * 55)

for mat, ev in materials.items():
    t0 = get_pivot(ev)
    risk = "HIGH @ 300C" if t0 > 300 else "LOW @ 300C"
    print(f"{mat:<12} | {ev:<8.2f} | {t0:<12.1f} | {risk}")
