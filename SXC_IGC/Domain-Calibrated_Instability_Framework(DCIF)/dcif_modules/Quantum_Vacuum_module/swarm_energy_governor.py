import numpy as np
from scipy.special import gamma

def calculate_v12_stats(extraction_per_node):
    health = 1.0 - extraction_per_node
    tension = abs(gamma(health))
    return tension

# 1. Single Tap (Icarus Strategy)
energy_single = 80  # units
tension_single = calculate_v12_stats(0.80)

# 2. Swarm Tap (V12-G Global Strategy)
nodes = 100
energy_per_node = 5 # units
total_energy_swarm = nodes * energy_per_node
tension_per_node = calculate_v12_stats(0.05) # Very low extraction

print(f"--- STRATEGY 1: SINGLE TAP ---")
print(f"Total Energy: {energy_single} units")
print(f"Substrate Tension: {round(tension_single, 4)} (HIGH RISK)")

print(f"\n--- STRATEGY 2: V12-G SWARM ---")
print(f"Total Energy: {total_energy_swarm} units")
print(f"Node Tension: {round(tension_per_node, 4)} (PERFECT STABILITY)")
print(f"Efficiency Gain: {((total_energy_swarm / energy_single) - 1) * 100}% more power.")
