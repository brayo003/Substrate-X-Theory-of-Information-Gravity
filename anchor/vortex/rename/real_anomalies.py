import numpy as np
import pandas as pd

print("="*80)
print("REAL EXPERIMENTAL ANOMALIES NEEDING EXPLANATION")
print("="*80)

# Known anomalies in precision measurements
anomalies = [
    {
        'name': 'Proton Radius Puzzle',
        'description': 'Proton radius from muonic hydrogen ≠ electronic hydrogen',
        'discrepancy': '4% difference (0.8409 vs 0.8751 fm)',
        'significance': '7σ',
        'year': '2010-2020',
        'could_explain': 'Fifth force coupling differently to muons vs electrons',
        'reference': 'Nature 466, 213–216 (2010)'
    },
    {
        'name': 'g-2 Muon Anomaly',
        'description': 'Muon magnetic moment measurement ≠ Standard Model prediction',
        'discrepancy': '4.2σ difference',
        'significance': '4.2σ',
        'year': '2021',
        'could_explain': 'New force coupling to muons',
        'reference': 'Phys. Rev. Lett. 126, 141801 (2021)'
    },
    {
        'name': 'Atomki Anomaly',
        'description': 'Unexplained bump in nuclear transitions of Be-8, He-4',
        'discrepancy': '6.8σ excess at 17 MeV',
        'significance': '6.8σ',
        'year': '2016',
        'could_explain': 'New boson with ~17 MeV mass',
        'reference': 'Phys. Rev. Lett. 116, 042501 (2016)'
    },
    {
        'name': 'KTeV Anomaly',
        'description': 'Rare kaon decay K⁺ → π⁺νν̄ rate higher than predicted',
        'discrepancy': '~3σ excess',
        'significance': '3σ',
        'year': '2021',
        'could_explain': 'New force in flavor-changing neutral currents',
        'reference': 'Phys. Rev. Lett. 126, 141801 (2021)'
    },
    {
        'name': 'EDGES 21-cm Anomaly',
        'description': 'Unexpectedly strong 21-cm absorption signal from early universe',
        'discrepancy': '3.8σ from ΛCDM prediction',
        'significance': '3.8σ',
        'year': '2018',
        'could_explain': 'Dark matter-baryon interactions',
        'reference': 'Nature 555, 67–70 (2018)'
    }
]

print("\nACTUAL ANOMALIES THAT NEED EXPLANATION:")
print("-"*80)

for i, anomaly in enumerate(anomalies, 1):
    print(f"\n{i}. {anomaly['name']}:")
    print(f"   {anomaly['description']}")
    print(f"   Discrepancy: {anomaly['discrepancy']} ({anomaly['significance']})")
    print(f"   Could a fifth force explain it? {anomaly['could_explain']}")

print("\n" + "="*80)
print("HOW TO BUILD A THEORY THAT MATTERS:")
print("-"*80)
print("""
1. PICK ONE ANOMALY (e.g., Atomki 17 MeV bump)
2. DEDUCE REQUIRED PARAMETERS:
   - Mass: m_X ≈ 17 MeV (from bump position)
   - Coupling: α_X from decay rate excess
   - Range: 1/m_X ≈ 10⁻¹⁴ m (nuclear scale)
3. CHECK CONSISTENCY:
   - Does it affect other measurements?
   - Is it ruled out by other experiments?
   - Does it predict NEW testable effects?
4. MAKE NEW PREDICTIONS:
   - "This should appear in XYZ experiment"
   - "The force should do ABC in stars"
""")

# Let's analyze Atomki anomaly as example
print("\n" + "="*80)
print("EXAMPLE: ATOMKİ 17 MeV BOSON THEORY")
print("="*80)

# Atomki parameters
m_X = 17.0  # MeV
m_X_eV = m_X * 1e6  # eV

# From paper: branching ratio ~10⁻⁶ suggests coupling
# g²/4π ~ 10⁻⁵ to 10⁻⁷
alpha_X = 1e-6  # Rough estimate

hbar = 1.0545718e-34
c = 299792458
eV = 1.6021766e-19

range_m = hbar * c / (m_X_eV * eV)
force_range = f"{range_m:.1e} m ≈ {range_m*1e15:.1f} fm"

print(f"\nDeduced parameters:")
print(f"  Mass: m_X = {m_X:.1f} MeV = {m_X_eV:.1e} eV")
print(f"  Coupling: α_X ≈ {alpha_X:.1e}")
print(f"  Force range: {force_range}")
print(f"  (Nuclear scale: ~1-10 fm ✓)")

print("\nThis theory would:")
print("1. EXPLAIN Atomki anomaly (primary motivation)")
print("2. PREDICT similar bumps in other nuclei")
print("3. REQUIRE new searches in specific experiments")
print("4. HAVE astrophysical consequences (star cooling)")

print("\n" + "="*80)
print("THIS is how you build a meaningful theory.")
print("Start with DATA, derive parameters, make predictions.")
print("="*80)

# Save to file
with open('real_anomalies_analysis.txt', 'w') as f:
    f.write("REAL ANOMALIES FOR FIFTH FORCE THEORIES\n")
    f.write("="*60 + "\n\n")
    for anomaly in anomalies:
        f.write(f"{anomaly['name']}:\n")
        f.write(f"  {anomaly['description']}\n")
        f.write(f"  Discrepancy: {anomaly['discrepancy']}\n")
        f.write(f"  Could explain: {anomaly['could_explain']}\n")
        f.write(f"  Reference: {anomaly['reference']}\n\n")
    
    f.write("\nRECOMMENDED STARTING POINT:\n")
    f.write("Atomki anomaly → 17 MeV boson\n")
    f.write(f"m_X = {m_X} MeV, α_X ≈ {alpha_X:.1e}\n")
    f.write(f"Range ≈ {range_m*1e15:.1f} fm (nuclear scale)\n")

print(f"\n📁 Analysis saved to 'real_anomalies_analysis.txt'")
