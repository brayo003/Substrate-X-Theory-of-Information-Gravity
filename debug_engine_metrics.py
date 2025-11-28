import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from theory.dynamic_metrics_core import generate_domain_tmv_metrics

# Test the metric generation directly
print("=== TESTING METRIC GENERATION DIRECTLY ===")

# Simulate what the engine does
test_history = [
    np.array([0.5, 0.5, 0.5]),
    np.array([0.6, 0.6, 0.6]), 
    np.array([0.7, 0.7, 0.7])
]
external_pressure = 0.1

metrics = generate_domain_tmv_metrics(test_history, external_pressure)
print(f"Generated metrics: {metrics}")

# Test with different histories
print("\n=== METRIC RESPONSE TO DIFFERENT HISTORIES ===")
histories = [
    ([0.1, 0.1, 0.1], "Stable"),
    ([0.1, 0.5, 0.9], "Volatile"), 
    ([0.9, 0.1, 0.9], "Oscillating")
]

for history_data, description in histories:
    hist = [np.array(history_data) for _ in range(3)]
    m = generate_domain_tmv_metrics(hist, external_pressure)
    print(f"{description:12} -> Tension: {m['Tension']:.4f}, Momentum: {m['Momentum']:.4f}, Variance: {m['Variance']:.4f}")

# Check the actual engine's domain states
print("\n=== CHECKING ENGINE'S ACTUAL METRICS ===")
from universal_dynamics_engine.universal_pde_engine import UniversalDynamicsEngine

engine = UniversalDynamicsEngine()
# Run a few steps to see if metrics evolve
engine.evolve_system(steps=5)  # Just a few steps to check

print("\nFinal domain states:")
for domain, state in engine.integrator.domain_states.items():
    print(f"  {domain.value}: {state.metrics}")
