"""
DEBUG: Check if engine is using real IG calculation or hardcoded values
"""
import sys
import os
sys.path.insert(0, '/home/lenovo/Git/Substrate X Theory of Information Gravity')

from theory.information_gravity_core import calculate_information_gravity
from applications.universal_risk_indicator import generate_risk_signal

print("=== REAL IG SYSTEM CHECK ===")

# Test with the same metrics your engine might be using
test_metrics = {
    'bio_physics_vr': 0.9,
    'planetary_momentum_error_ppm': 100,
    'planetary_energy_error_ppm': 100
}

real_ig = calculate_information_gravity(test_metrics)
signal, _ = generate_risk_signal(test_metrics)

print(f"Real IG calculation: {real_ig:.4f}")
print(f"Real signal: {signal}")
print()

# Now let's see what the engine is actually doing
print("=== ENGINE INTEGRATION CHECK ===")

# Import and check the engine's IG usage
from universal_dynamics_engine.universal_pde_engine import UniversalPDEIntegrator

# Create a minimal engine instance to test
engine = UniversalPDEIntegrator()
print("Engine created successfully")

# Check if engine has access to real IG function
if hasattr(engine, 'calculate_information_gravity'):
    print("✅ Engine has IG calculation method")
else:
    print("❌ Engine missing IG calculation method")
