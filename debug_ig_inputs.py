import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from universal_dynamics_engine.universal_pde_engine import UniversalDynamicsEngine

# Create engine and check IG inputs
engine = UniversalDynamicsEngine()

# Check what _generate_ig_inputs produces (after domains are added in evolve_system)
ig_inputs = engine.integrator._generate_ig_inputs()
print("=== ENGINE IG INPUTS (BEFORE EVOLUTION) ===")
print(ig_inputs)

# Calculate IG with these inputs
from theory.information_gravity_core import calculate_information_gravity
if ig_inputs:
    ig_score = calculate_information_gravity(ig_inputs)
    print(f"IG Score from inputs: {ig_score:.4f}")
else:
    print("No IG inputs available (domains not initialized)")

# Test if IG calculation itself responds to different inputs
print("\n=== IG CALCULATION RESPONSE TEST ===")
test_inputs = [
    {'bio_physics_vr': 0.1, 'planetary_momentum_error_ppm': 5000, 'planetary_energy_error_ppm': 5000},
    {'bio_physics_vr': 0.5, 'planetary_momentum_error_ppm': 2500, 'planetary_energy_error_ppm': 2500}, 
    {'bio_physics_vr': 0.9, 'planetary_momentum_error_ppm': 100, 'planetary_energy_error_ppm': 100},
]

for inputs in test_inputs:
    ig = calculate_information_gravity(inputs)
    print(f"Inputs: bio_physics={inputs['bio_physics_vr']:.1f}, errors=({inputs['planetary_momentum_error_ppm']}, {inputs['planetary_energy_error_ppm']}) -> IG: {ig:.4f}")
