import numpy as np

def calculate_axial_suppression(energy_mev, m_x=17.01):
    """
    Simulates momentum-dependent suppression for an Axial-Vector.
    The effective coupling g_eff drops as energy decreases.
    """
    # Simple scaling: g_eff ~ g_base * (q / M_X)
    q = energy_mev 
    suppression = q / m_x
    return suppression

# Current Scenario
g_n_base = 1.09e-03
atomki_energy = 17.23
neutron_scattering_energy = 0.5 # Typical low-energy neutron scattering

g_atomki = g_n_base * calculate_axial_suppression(atomki_energy)
g_neutron = g_n_base * calculate_axial_suppression(neutron_scattering_energy)

print(f"--- AXIAL-VECTOR SUPPRESSION REPORT ---")
print(f"Effective g_n at Atomki (17 MeV): {g_atomki:.2e} (RESONANT)")
print(f"Effective g_n at Scattering (0.5 MeV): {g_neutron:.2e} (SUPPRESSED)")

n_pb_limit = 2e-4
if g_neutron < n_pb_limit:
    print(f"\nSTATUS: SAFE ✓")
    print(f"Reason: Axial-Vector suppression reduces coupling by {g_atomki/g_neutron:.1f}x at low energies.")
else:
    print(f"\nSTATUS: STILL CONSTRAINED ❌")
