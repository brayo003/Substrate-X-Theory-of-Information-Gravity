import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from universal_dynamics_engine.universal_pde_engine import UniversalDynamicsEngine

engine = UniversalDynamicsEngine()

print("=== CHECKING FIELD EVOLUTION ===")

# Add a simple domain and track its field evolution
class SimpleDomainState:
    def __init__(self):
        self.field = np.array([0.5, 0.5, 0.5])
        self.history = [self.field.copy()]
        
    def evolve(self):
        # Simple evolution: add some noise
        self.field += 0.1 * (np.random.random(3) - 0.5)
        self.field = np.clip(self.field, 0.0, 1.0)
        self.history.append(self.field.copy())
        return len(self.history) >= 3  # Ready for metrics

# Test evolution
domain = SimpleDomainState()
print("Initial field:", domain.field)

for step in range(5):
    domain.evolve()
    print(f"Step {step}: field = {domain.field}")
    if len(domain.history) >= 3:
        from theory.dynamic_metrics_core import generate_domain_tmv_metrics
        metrics = generate_domain_tmv_metrics(domain.history[-3:], 0.1)
        print(f"       metrics = {metrics}")

print("\nThe issue may be that the engine's fields aren't evolving significantly,")
print("or the metric generation isn't being called with updated field states.")
