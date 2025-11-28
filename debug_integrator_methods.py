import inspect
from universal_dynamics_engine.universal_pde_engine import UniversalDynamicsEngine

engine = UniversalDynamicsEngine()
integrator = engine.integrator

print("=== Integrator Methods ===")
for name, member in inspect.getmembers(integrator, predicate=inspect.ismethod):
    print(name)

print("\n=== Method Usage Hint ===")
print("Use 'integrator.coupled_pde_step()' to advance the system instead of 'step()'")
